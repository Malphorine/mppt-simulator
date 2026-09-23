"""
Single-Diode Photovoltaic Model
===============================

Implements the standard single-diode five-parameter (SDM) model for a
photovoltaic module:

    I = Iph - I0 * [exp((V + I*Rs) / (n*Ns*Vt)) - 1] - (V + I*Rs) / Rsh

where:
    I     : module output current [A]
    V     : module output voltage [V]
    Iph   : photo-generated current [A]
    I0    : diode reverse saturation current [A]
    Rs    : series resistance [Ω]
    Rsh   : shunt (parallel) resistance [Ω]
    n     : diode ideality factor [–]
    Ns    : number of cells in series [–]
    Vt    : thermal voltage per cell = kB*T/q [V]

Temperature & irradiance dependence follows De Soto et al. (2006).

References:
    [1] Villalva, Gazoli, Filho, "Comprehensive Approach to Modeling and
        Simulation of Photovoltaic Arrays," IEEE Trans. Power Electron., 2009.
    [2] De Soto, Klein, Beckman, "Improvement and validation of a model for
        photovoltaic array performance," Solar Energy, 2006.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import Optional, Tuple

import numpy as np
from scipy.optimize import minimize_scalar, brentq
from scipy.special import lambertw


# ── Physical constants ──────────────────────────────────────────────────────
KB: float = 1.380649e-23      # Boltzmann constant [J/K]
Q: float = 1.602176634e-19    # Elementary charge [C]
T_REF: float = 298.15         # STC temperature [K]  (25 °C)
G_REF: float = 1000.0         # STC irradiance [W/m²]


@dataclass
class PVModuleParams:
    """Electrical parameters of a PV module at STC.

    Default values correspond to a Canadian Solar CS3U-400MS
    (Mono-PERC, 144 half-cut cells → 72 series equivalent).
    """

    # ── Datasheet parameters at STC ──
    Ns: int = 72             # Number of cells in series
    Voc: float = 48.6        # Open-circuit voltage [V]
    Isc: float = 10.33       # Short-circuit current [A]
    Vmp: float = 40.8        # Voltage at maximum power [V]
    Imp: float = 9.81        # Current at maximum power [A]
    Pmax: float = 400.25     # Maximum power [W]  (Vmp × Imp)

    # ── Five-parameter model ──
    Rs: float = 0.15         # Series resistance [Ω]
    Rsh: float = 650.0       # Shunt resistance [Ω]
    n: float = 1.10          # Diode ideality factor

    # ── Temperature coefficients ──
    alpha_sc: float = 0.0005   # Isc temp. coeff. [1/°C]  (+0.05 %/°C)
    beta_oc: float = -0.0029   # Voc temp. coeff. [1/°C]  (-0.29 %/°C)

    # ── Bandgap ──
    Eg0: float = 1.121        # Bandgap at STC [eV]
    dEgdT: float = -0.0002677  # Bandgap temperature coefficient [1/K]

    # ── Derived (computed at init) ──
    Iph0: float = field(init=False)
    I0_0: float = field(init=False)

    def __post_init__(self) -> None:
        self._compute_derived()
        self.validate()

    def _compute_derived(self) -> None:
        """Compute photo-current and saturation current at STC."""
        Vt0 = KB * T_REF / Q
        a0 = self.n * self.Ns * Vt0

        # Photo-current at STC  (Eq. from Villalva et al.)
        self.Iph0 = self.Isc * (1.0 + self.Rs / self.Rsh)

        # Saturation current at STC  (open-circuit condition)
        exp_voc = np.exp(self.Voc / a0)
        self.I0_0 = (self.Iph0 - self.Voc / self.Rsh) / (exp_voc - 1.0)

    def validate(self) -> list[str]:
        """Run sanity checks; return list of warnings."""
        issues: list[str] = []

        if self.Voc <= self.Vmp:
            issues.append(f"Voc ({self.Voc}) must be > Vmp ({self.Vmp})")
        if self.Isc <= self.Imp:
            issues.append(f"Isc ({self.Isc}) must be > Imp ({self.Imp})")

        pmax_calc = self.Vmp * self.Imp
        rel_err = abs(self.Pmax - pmax_calc) / max(self.Pmax, 1e-9)
        if rel_err > 0.02:
            issues.append(
                f"Pmax ({self.Pmax:.1f}) differs from Vmp×Imp "
                f"({pmax_calc:.1f}) by {rel_err*100:.1f}%"
            )

        if self.Rs < 0:
            issues.append(f"Rs ({self.Rs}) must be ≥ 0")
        if self.Rsh <= 0:
            issues.append(f"Rsh ({self.Rsh}) must be > 0")
        if not (0.5 <= self.n <= 2.5):
            issues.append(f"Ideality factor n ({self.n}) outside [0.5, 2.5]")
        if self.I0_0 <= 0:
            issues.append(f"Saturation current I0 ({self.I0_0:.3e}) must be > 0")
        if self.Iph0 <= 0:
            issues.append(f"Photo-current Iph ({self.Iph0:.3e}) must be > 0")
        if self.Ns <= 0:
            issues.append(f"Ns ({self.Ns}) must be > 0")

        for msg in issues:
            warnings.warn(f"[PV Validation] {msg}", stacklevel=2)

        return issues


class PVModule:
    """Single PV module using the single-diode model.

    Solves the implicit I-V equation using the Lambert W function for
    robustness and speed.  A Newton-Raphson fallback is available.
    """

    def __init__(self, params: Optional[PVModuleParams] = None) -> None:
        self.params = params or PVModuleParams()

        # Current operating conditions
        self._G: float = G_REF
        self._T: float = 25.0  # °C

        # Current model parameters (recomputed when G/T change)
        self._Iph: float = 0.0
        self._I0: float = 0.0
        self._Rs: float = 0.0
        self._Rsh: float = 0.0
        self._a: float = 0.0  # n * Ns * Vt
        self._cached_mpp: Optional[Tuple[float, float, float]] = None
        self._update_model()

    # ── Environmental setters ───────────────────────────────────────────
    @property
    def G(self) -> float:
        return self._G

    @property
    def T(self) -> float:
        return self._T

    def set_conditions(self, G: float, T_celsius: float) -> None:
        """Set irradiance [W/m²] and cell temperature [°C]."""
        G = max(G, 1.0)  # Avoid division by zero
        if abs(self._G - G) < 1e-4 and abs(self._T - T_celsius) < 1e-4 and self._cached_mpp is not None:
            return
        self._G = G
        self._T = T_celsius
        self._cached_mpp = None
        self._update_model()

    # ── Model parameter computation ─────────────────────────────────────
    def _update_model(self) -> None:
        """Recompute single-diode parameters for current (G, T)."""
        p = self.params
        T_K = self._T + 273.15

        # Thermal voltage
        Vt = KB * T_K / Q
        self._a = p.n * p.Ns * Vt

        # Photo-current: proportional to G, linear in T
        alpha_abs = p.Isc * p.alpha_sc  # A/K
        self._Iph = (self._G / G_REF) * (p.Iph0 + alpha_abs * (T_K - T_REF))

        # Saturation current: exponential in T  (De Soto model)
        Eg = p.Eg0 * (1.0 + p.dEgdT * (T_K - T_REF))
        exp_arg = (Q / KB) * (p.Eg0 / T_REF - Eg / T_K)
        # Clip to avoid overflow
        exp_arg = np.clip(exp_arg, -500.0, 500.0)
        self._I0 = p.I0_0 * (T_K / T_REF) ** 3 * np.exp(exp_arg)

        # Series resistance: constant
        self._Rs = p.Rs

        # Shunt resistance: inversely proportional to G
        self._Rsh = p.Rsh * (G_REF / self._G)

    # ── I-V curve solving ───────────────────────────────────────────────
    def current_at_voltage(self, V: np.ndarray | float) -> np.ndarray:
        """Compute current I(V) using Lambert W analytical solution.

        The Lambert W approach avoids iterative solving and is fully
        vectorized.  For numerical stability, the argument is computed
        in log-domain when it becomes large.
        """
        V = np.atleast_1d(np.asarray(V, dtype=np.float64))
        Iph, I0, Rs, Rsh, a = self._Iph, self._I0, self._Rs, self._Rsh, self._a

        if I0 <= 0 or a <= 0:
            return np.full_like(V, 0.0)

        Rs_Rsh = Rs + Rsh

        # Argument to Lambert W, computed in log space for safety
        log_prefix = np.log(Rs * Rsh * I0 / (a * Rs_Rsh))
        theta = Rsh * (Rs * (Iph + I0) + V) / (a * Rs_Rsh)

        log_arg = log_prefix + theta

        # For very large arguments, use asymptotic expansion
        I = np.empty_like(V)
        large = log_arg > 500.0
        small = ~large

        if np.any(small):
            arg_w = np.exp(log_arg[small])
            w = np.real(lambertw(arg_w))
            I[small] = (Rsh * (Iph + I0) - V[small]) / Rs_Rsh - (a / Rs) * w

        if np.any(large):
            # Asymptotic: W(z) ≈ ln(z) - ln(ln(z)) for large z
            ln_z = log_arg[large]
            ln_ln_z = np.log(np.maximum(ln_z, 1e-30))
            w_approx = ln_z - ln_ln_z + ln_ln_z / ln_z
            I[large] = (Rsh * (Iph + I0) - V[large]) / Rs_Rsh - (a / Rs) * w_approx

        # Clip to physical range
        I = np.clip(I, 0.0, Iph * 1.05)
        return I

    def current_at_voltage_newton(
        self, V: float, I_guess: Optional[float] = None,
        max_iter: int = 50, tol: float = 1e-10
    ) -> float:
        """Solve I(V) via Newton-Raphson.  Scalar version."""
        Iph, I0, Rs, Rsh, a = self._Iph, self._I0, self._Rs, self._Rsh, self._a

        if I0 <= 0 or a <= 0:
            return 0.0

        # Initial guess
        if I_guess is None:
            if V < 0.8 * self.params.Voc:
                I = Iph
            else:
                I = max(0.0, Iph * (1.0 - V / self.params.Voc))
        else:
            I = I_guess

        for _ in range(max_iter):
            arg = np.clip((V + I * Rs) / a, -50.0, 700.0)
            exp_val = np.exp(arg)

            f = I - Iph + I0 * (exp_val - 1.0) + (V + I * Rs) / Rsh
            fp = 1.0 + (I0 * Rs / a) * exp_val + Rs / Rsh

            step = f / fp
            I_new = I - step
            I_new = max(-0.5, min(Iph * 1.2, I_new))

            if abs(step) < tol:
                return max(0.0, I_new)
            I = I_new

        return max(0.0, I)

    # ── I-V / P-V curves ───────────────────────────────────────────────
    def get_iv_curve(self, num_points: int = 500) -> Tuple[np.ndarray, np.ndarray]:
        """Generate the full I-V curve from 0 to Voc.

        Returns:
            (V, I) arrays
        """
        Voc_est = self._estimate_voc()
        V = np.linspace(0, Voc_est, num_points)
        I = self.current_at_voltage(V)
        return V, I

    def get_pv_curve(self, num_points: int = 500) -> Tuple[np.ndarray, np.ndarray]:
        """Generate the P-V curve.

        Returns:
            (V, P) arrays
        """
        V, I = self.get_iv_curve(num_points)
        P = V * I
        return V, P

    def _estimate_voc(self) -> float:
        """Estimate open-circuit voltage for current conditions."""
        Iph, I0, Rs, Rsh, a = self._Iph, self._I0, self._Rs, self._Rsh, self._a

        if I0 <= 0:
            return self.params.Voc

        # Approximate Voc ≈ a * ln(Iph/I0 + 1)
        voc_approx = a * np.log(Iph / I0 + 1.0)

        # Refine with Newton: f(V) = I(V) = 0
        V = voc_approx
        for _ in range(20):
            I_val = self.current_at_voltage_newton(V)
            if abs(I_val) < 1e-8:
                break
            # dI/dV at V
            dV = 0.001
            I_plus = self.current_at_voltage_newton(V + dV)
            dIdV = (I_plus - I_val) / dV
            if abs(dIdV) < 1e-15:
                break
            V = V - I_val / dIdV
            V = max(0, V)

        return V

    # ── MPP calculation (independent, for validation) ──────────────────
    def find_mpp(self) -> Tuple[float, float, float]:
        """Find the Maximum Power Point by optimizing P(V) = V × I(V).

        Uses scipy.optimize.minimize_scalar (golden section + parabolic).
        This is an independent calculation for VALIDATION ONLY — it is
        NOT used by the MPPT controller.

        Returns:
            (Vmp, Imp, Pmax)
        """
        if self._cached_mpp is not None:
            return self._cached_mpp

        Voc_est = self._estimate_voc()

        def neg_power(V: float) -> float:
            I = self.current_at_voltage(np.array([V]))[0]
            return -(V * I)

        result = minimize_scalar(
            neg_power,
            bounds=(0.1, Voc_est * 0.99),
            method='bounded',
            options={'xatol': 1e-6}
        )

        Vmp = result.x
        Imp = self.current_at_voltage(np.array([Vmp]))[0]
        Pmax = Vmp * Imp

        self._cached_mpp = (Vmp, Imp, Pmax)
        return self._cached_mpp

    def get_isc(self) -> float:
        """Short-circuit current I(V=0)."""
        return self.current_at_voltage(np.array([0.0]))[0]

    def get_voc(self) -> float:
        """Open-circuit voltage (where I ≈ 0)."""
        return self._estimate_voc()

    # ── String representation ───────────────────────────────────────────
    def __repr__(self) -> str:
        Vmp, Imp, Pmax = self.find_mpp()
        return (
            f"PVModule(G={self._G:.0f} W/m², T={self._T:.1f} °C)\n"
            f"  Voc={self.get_voc():.2f} V, Isc={self.get_isc():.2f} A\n"
            f"  Vmp={Vmp:.2f} V, Imp={Imp:.2f} A, Pmax={Pmax:.1f} W"
        )


class PVArray:
    """PV array with N modules in series, supporting partial shading.

    Each module can have an independent irradiance level.  Bypass diodes
    are modeled: when a module produces negative voltage (i.e. acts as a
    load), the bypass diode conducts, limiting the voltage drop to ~0.7 V.
    """

    BYPASS_DIODE_VF: float = 0.7  # Bypass diode forward voltage [V]

    def __init__(
        self,
        n_modules: int = 3,
        params: Optional[PVModuleParams] = None,
    ) -> None:
        self.n_modules = n_modules
        self.modules = [PVModule(params or PVModuleParams()) for _ in range(n_modules)]
        self._cached_mpp: Optional[Tuple[float, float, float]] = None

    def set_conditions(
        self,
        irradiances: list[float],
        temperatures: list[float],
    ) -> None:
        """Set per-module irradiance and temperature."""
        if len(irradiances) != self.n_modules:
            raise ValueError(
                f"Expected {self.n_modules} irradiance values, got {len(irradiances)}"
            )
        if len(temperatures) != self.n_modules:
            raise ValueError(
                f"Expected {self.n_modules} temperature values, got {len(temperatures)}"
            )
        changed = False
        for mod, G, T in zip(self.modules, irradiances, temperatures):
            if abs(mod.G - G) > 1e-4 or abs(mod.T - T) > 1e-4:
                changed = True
            mod.set_conditions(G, T)
        if changed:
            self._cached_mpp = None

    def get_iv_curve(self, num_points: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Generate the aggregate I-V curve of series-connected modules."""
        # Find maximum Isc across modules
        isc_max = max(mod.get_isc() for mod in self.modules)

        I_array = np.linspace(isc_max, 0.0, num_points)
        V_total = np.zeros_like(I_array)

        for mod in self.modules:
            V_mod, I_mod = mod.get_iv_curve(num_points=1000)
            valid = np.ones(len(I_mod), dtype=bool)
            for i in range(1, len(I_mod)):
                if I_mod[i] >= I_mod[i - 1]:
                    valid[i] = False
            I_mod_clean = I_mod[valid]
            V_mod_clean = V_mod[valid]

            V_at_I = np.interp(
                I_array,
                I_mod_clean[::-1],
                V_mod_clean[::-1],
                left=0.0,
                right=V_mod_clean[-1],
            )
            V_at_I = np.maximum(V_at_I, -self.BYPASS_DIODE_VF)
            V_total += V_at_I

        return V_total, I_array

    def get_pv_curve(self, num_points: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Generate P-V curve for the array."""
        V, I = self.get_iv_curve(num_points)
        P = V * I
        return V, P

    def find_mpp(self) -> Tuple[float, float, float]:
        """Find global MPP of the array.

        Returns:
            (Vmp, Imp, Pmax)
        """
        if self._cached_mpp is not None:
            return self._cached_mpp

        V, I = self.get_iv_curve(num_points=1000)
        P = V * I
        idx = np.argmax(P)
        self._cached_mpp = (float(V[idx]), float(I[idx]), float(P[idx]))
        return self._cached_mpp

    def find_all_local_maxima(
        self, num_points: int = 2000
    ) -> list[Tuple[float, float, float]]:
        """Find all local maxima in the P-V curve.

        Returns:
            List of (V, I, P) tuples for each local maximum,
            sorted by descending power.
        """
        V, P = self.get_pv_curve(num_points)
        V_arr, I_arr = self.get_iv_curve(num_points)

        maxima = []
        for i in range(1, len(P) - 1):
            if P[i] > P[i - 1] and P[i] > P[i + 1] and P[i] > 0.01:
                maxima.append((V[i], I_arr[i], P[i]))

        # Sort by power descending
        maxima.sort(key=lambda x: x[2], reverse=True)
        return maxima

    def current_at_voltage(self, V_total: float) -> float:
        """Find array current at a given total voltage.

        For a series string, we need to find the current I such that
        the sum of individual module voltages equals V_total.
        This requires iterative solving.
        """
        V_arr, I_arr = self.get_iv_curve(num_points=2000)

        # Interpolate: I(V)
        # Sort by V ascending for interpolation
        sort_idx = np.argsort(V_arr)
        V_sorted = V_arr[sort_idx]
        I_sorted = I_arr[sort_idx]

        # Remove duplicate V values
        unique_mask = np.diff(V_sorted, prepend=-np.inf) > 1e-9
        V_unique = V_sorted[unique_mask]
        I_unique = I_sorted[unique_mask]

        if V_total < V_unique[0] or V_total > V_unique[-1]:
            return 0.0

        return float(np.interp(V_total, V_unique, I_unique))
