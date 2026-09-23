"""
DC-DC Boost Converter Averaged Model.

This module provides a physically-based, averaged model for a boost converter.
The averaged model approximates the high-frequency switching behavior by
calculating the average voltages and currents over a switching cycle.

The ideal continuous conduction mode (CCM) boost equation is:
V_out = V_in / (1 - D)
I_in = I_out / (1 - D)

Losses are modeled as:
- Inductor conduction loss: I_in^2 * R_L
- MOSFET conduction loss: I_in^2 * D * R_ds
- Diode conduction loss: V_diode * I_out = V_diode * I_in * (1 - D)
- Switching losses: approximated based on a fixed loss factor or efficiency.

Dynamic response is approximated using a first-order low-pass filter (exponential smoothing)
with a time constant tau, representing the L-C filter dynamics.
"""

from dataclasses import dataclass
import numpy as np

@dataclass
class BoostConverterParams:
    switching_frequency: float = 50_000.0  # 50 kHz
    L: float = 100e-6  # Inductor 100 μH
    C: float = 470e-6  # Capacitor 470 μF
    R_L: float = 0.05  # Inductor DCR [Ω]
    R_ds: float = 0.02  # MOSFET Rds(on) [Ω]
    V_diode: float = 0.7  # Diode forward voltage [V]
    D_min: float = 0.05  # Min duty cycle
    D_max: float = 0.90  # Max duty cycle
    efficiency_nominal: float = 0.95  # Nominal efficiency
    tau: float = 0.002  # Dynamic time constant [s]
    V_in_max: float = 60.0  # Max input voltage [V]
    V_out_max: float = 400.0  # Max output voltage [V]
    I_in_max: float = 15.0  # Max input current [A]

class BoostConverter:
    def __init__(self, params: BoostConverterParams, load):
        """
        Initialize the BoostConverter.

        Args:
            params: BoostConverterParams instance.
            load: A LoadBase instance representing the load connected to the output.
        """
        self.params = params
        self.load = load
        self._V_out_state = 0.0
        self._I_out_state = 0.0

    def clamp_duty_cycle(self, D: float) -> float:
        """Clamps the duty cycle to [D_min, D_max]."""
        return float(np.clip(D, self.params.D_min, self.params.D_max))

    def compute_losses(self, V_in: float, I_in: float, D: float) -> dict:
        """
        Computes the power losses in the converter.
        
        Args:
            V_in: Input voltage [V]
            I_in: Input current [A]
            D: Duty cycle
            
        Returns:
            A dictionary containing various loss components in Watts.
        """
        # Inductor conduction loss
        P_cond_L = (I_in ** 2) * self.params.R_L
        
        # MOSFET conduction loss
        P_cond_mosfet = (I_in ** 2) * D * self.params.R_ds
        
        # Diode conduction loss
        I_out_approx = I_in * (1 - D)
        P_cond_diode = I_out_approx * self.params.V_diode
        
        # Approximate switching loss based on nominal efficiency shortfall
        P_in_approx = V_in * I_in
        P_sw = P_in_approx * (1.0 - self.params.efficiency_nominal) * 0.5 # rough approx
        
        P_loss = P_cond_L + P_cond_mosfet + P_cond_diode + P_sw
        
        return {
            'P_cond_L': P_cond_L,
            'P_cond_mosfet': P_cond_mosfet,
            'P_cond_diode': P_cond_diode,
            'P_sw': P_sw,
            'P_total': P_loss
        }

    def update(self, V_in: float, D: float, dt: float, I_in: float = None) -> dict:
        """
        Main update method for the averaged model.
        
        Args:
            V_in: Input voltage [V]
            D: Duty cycle (will be clamped)
            dt: Time step [s]
            I_in: Input current [A] (optional, from PV operating point)
            
        Returns:
            Dictionary with V_out, I_out, I_in, P_in, P_out, P_loss, efficiency.
        """
        D = self.clamp_duty_cycle(D)
        
        if I_in is None:
            I_in = self._I_out_state / (1 - D) if D < 1.0 else 0.0
        
        # Compute losses
        losses = self.compute_losses(V_in, I_in, D)
        P_loss = losses['P_total']
        
        P_in = max(0.0, V_in * I_in)
        # Power available to output after losses
        P_out_max = max(0.0, P_in - P_loss)
        
        # Ideal output voltage
        V_out_ideal = V_in / (1 - D)
        
        # Subtract voltage drops
        V_drop_R = I_in * (self.params.R_L + D * self.params.R_ds) / (1 - D)
        V_out_steady = max(0.0, V_out_ideal - V_drop_R - self.params.V_diode)
        
        # First-order dynamic response
        alpha = dt / (self.params.tau + dt)
        self._V_out_state = (1 - alpha) * self._V_out_state + alpha * V_out_steady
        
        # Get load current
        self._I_out_state = self.load.get_current(self._V_out_state)
        
        P_out = self._V_out_state * self._I_out_state
        # Strict energy conservation: output power cannot exceed input power minus losses
        if P_out > P_in and P_in > 0:
            P_out = min(P_out, P_out_max)
            if hasattr(self.load, 'R') and self.load.R > 0:
                self._V_out_state = np.sqrt(P_out * self.load.R)
                self._I_out_state = self._V_out_state / self.load.R
        
        eta = P_out / P_in if P_in > 0 else 0.0
        
        return {
            'V_out': self._V_out_state,
            'I_out': self._I_out_state,
            'I_in': I_in,
            'P_in': P_in,
            'P_out': P_out,
            'P_loss': P_loss,
            'efficiency': eta,
            'losses': losses
        }

    def get_pv_operating_point(self, pv_module, D: float) -> tuple[float, float]:
        """
        Given a PVModule and a duty cycle D, find the operating voltage/current
        on the PV I-V curve.

        The boost converter presents an effective input resistance to the PV:
            R_in_eff = R_load * (1 - D)^2 / eta

        The operating point is where the PV I-V curve intersects the load line
        I = V / R_in_eff.

        Args:
            pv_module: An instance providing `current_at_voltage(V)`.
            D: Duty cycle.

        Returns:
            Tuple of (V_pv, I_pv).
        """
        D = self.clamp_duty_cycle(D)

        if hasattr(self.load, 'R'):
            R_load = self.load.R
        else:
            if self._I_out_state > 1e-3:
                R_load = self._V_out_state / self._I_out_state
            else:
                R_load = 100.0  # Nominal assumption

        eta = self.params.efficiency_nominal
        R_in_eff = R_load * ((1 - D) ** 2) / eta

        # Avoid infinite or very large R_in (would put PV near Voc with ~0 current)
        R_in_eff = min(R_in_eff, 1e4)
        R_in_eff = max(R_in_eff, 0.1)

        def f(V):
            """Residual: I_pv(V) - V / R_in_eff = 0"""
            I_pv = float(pv_module.current_at_voltage(np.atleast_1d(V))[0])
            return I_pv - V / R_in_eff

        # Find operating point via bisection (more robust than Newton for I-V curves)
        V_oc_est = getattr(pv_module.params, 'Voc', 50.0)

        # Sweep to find bracket
        V_test = np.linspace(0.1, V_oc_est * 0.99, 200)
        I_pv_test = pv_module.current_at_voltage(V_test)
        I_load_test = V_test / R_in_eff
        residual = I_pv_test - I_load_test

        # Find sign change (crossing point)
        sign_changes = np.where(np.diff(np.sign(residual)))[0]

        if len(sign_changes) > 0:
            # Use the last crossing (closest to MPP typically)
            idx = sign_changes[-1]
            V_lo, V_hi = V_test[idx], V_test[idx + 1]

            # Refine with bisection
            for _ in range(50):
                V_mid = (V_lo + V_hi) / 2
                f_mid = f(V_mid)
                if abs(f_mid) < 1e-8:
                    break
                if f_mid > 0:
                    V_lo = V_mid
                else:
                    V_hi = V_mid
            V_pv = (V_lo + V_hi) / 2
        else:
            # No crossing found; use the minimum residual point
            idx = np.argmin(np.abs(residual))
            V_pv = float(V_test[idx])

        V_pv = float(np.clip(V_pv, 0.0, V_oc_est))
        I_pv = float(pv_module.current_at_voltage(np.atleast_1d(V_pv))[0])
        return V_pv, I_pv
        
    def reset(self):
        """Reset the dynamic state of the converter."""
        self._V_out_state = 0.0
        self._I_out_state = 0.0
