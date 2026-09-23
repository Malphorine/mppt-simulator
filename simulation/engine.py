"""
Time-Domain MPPT Simulation Engine
===================================

Runs a discrete-time simulation of the complete PV system:

    PV Module → DC-DC Boost Converter → MPPT Controller → Load

At every timestep the engine:
1. Gets environmental conditions (G, T) from the scenario
2. Updates the PV model
3. Determines the PV operating point from the converter/load
4. Runs the MPPT controller at its sampling rate
5. Updates the converter
6. Records all state variables
7. Independently computes the theoretical MPP for validation

All recorded data is stored in a pandas DataFrame for analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from models.pv_model import PVModule, PVModuleParams, PVArray
from models.converter import BoostConverter, BoostConverterParams
from models.load import ResistiveLoad, LoadBase
from mppt.base import MPPTBase
from mppt.perturb_observe import PerturbAndObserve
from mppt.incremental_conductance import IncrementalConductance
from simulation.scenarios import Scenario, ConstantConditions, ScenarioConfig


@dataclass
class SimulationConfig:
    """Configuration for the time-domain simulation."""

    # Timing
    duration: float = 20.0        # Total simulation time [s]
    dt: float = 0.001             # Simulation timestep [s]
    mppt_period: float = 0.050    # MPPT sampling period [s]

    # Initial conditions
    D_init: float = 0.5           # Initial duty cycle

    # Noise (disabled by default for reproducibility)
    noise_enabled: bool = False
    voltage_noise_std: float = 0.05   # Voltage noise standard deviation [V]
    current_noise_std: float = 0.02   # Current noise standard deviation [A]
    random_seed: int = 42             # Fixed seed for reproducibility


@dataclass
class SimulationResult:
    """Contains all recorded simulation data and metadata."""

    config: SimulationConfig
    scenario_name: str
    algorithm_name: str
    data: pd.DataFrame
    pv_params: PVModuleParams

    @property
    def time(self) -> np.ndarray:
        return self.data['time'].values

    @property
    def pv_power(self) -> np.ndarray:
        return self.data['pv_power'].values

    @property
    def mpp_power(self) -> np.ndarray:
        return self.data['mpp_power'].values

    @property
    def tracking_efficiency(self) -> np.ndarray:
        return self.data['tracking_efficiency'].values


class SimulationEngine:
    """Core simulation engine for PV MPPT systems.

    Runs a time-domain simulation with configurable components.
    """

    def __init__(
        self,
        pv: PVModule | PVArray,
        converter: BoostConverter,
        mppt: MPPTBase,
        scenario: Scenario,
        config: Optional[SimulationConfig] = None,
    ) -> None:
        self.pv = pv
        self.converter = converter
        self.mppt = mppt
        self.scenario = scenario
        self.config = config or SimulationConfig()

        # Random number generator for noise
        self._rng = np.random.default_rng(self.config.random_seed)

    def run(self) -> SimulationResult:
        """Execute the full time-domain simulation.

        Returns:
            SimulationResult containing all recorded data.
        """
        cfg = self.config
        n_steps = int(cfg.duration / cfg.dt) + 1
        times = np.linspace(0, cfg.duration, n_steps)

        # Pre-allocate recording arrays
        records = {
            'time': np.zeros(n_steps),
            'irradiance': np.zeros(n_steps),
            'temperature': np.zeros(n_steps),
            'pv_voltage': np.zeros(n_steps),
            'pv_current': np.zeros(n_steps),
            'pv_power': np.zeros(n_steps),
            'duty_cycle': np.zeros(n_steps),
            'out_voltage': np.zeros(n_steps),
            'out_current': np.zeros(n_steps),
            'out_power': np.zeros(n_steps),
            'mpp_voltage': np.zeros(n_steps),
            'mpp_current': np.zeros(n_steps),
            'mpp_power': np.zeros(n_steps),
            'tracking_error': np.zeros(n_steps),
            'tracking_efficiency': np.zeros(n_steps),
            'converter_efficiency': np.zeros(n_steps),
            'converter_loss': np.zeros(n_steps),
        }

        # Initial state
        D = cfg.D_init
        next_mppt_time = 0.0
        V_pv = 0.0
        I_pv = 0.0
        last_D = None
        last_G = None
        last_T = None

        # Reset converter
        self.converter.reset()
        self.mppt.reset()

        is_array = isinstance(self.pv, PVArray)

        for i, t in enumerate(times):
            # ── 1. Get environmental conditions ───────────────────────
            G, T = self.scenario.get_conditions(t)

            env_changed = (last_G is None or abs(G - last_G) > 1e-4 or abs(T - last_T) > 1e-4)
            if env_changed:
                last_G = G
                last_T = T
                # Update PV model
                if is_array:
                    from simulation.scenarios import PartialShading
                    if isinstance(self.scenario, PartialShading):
                        G_list, T_list = self.scenario.get_module_conditions(t)
                        self.pv.set_conditions(G_list, T_list)
                    else:
                        G_list = [G] * self.pv.n_modules
                        T_list = [T] * self.pv.n_modules
                        self.pv.set_conditions(G_list, T_list)
                else:
                    self.pv.set_conditions(G, T)

            # ── 2. Get PV operating point ─────────────────────────────
            if env_changed or last_D is None or abs(D - last_D) > 1e-6:
                if is_array:
                    V_pv, I_pv = self._get_array_operating_point(D)
                else:
                    V_pv, I_pv = self.converter.get_pv_operating_point(self.pv, D)
                last_D = D

            P_pv = V_pv * I_pv

            # ── 3. Add measurement noise if enabled ───────────────────
            V_measured = V_pv
            I_measured = I_pv
            if cfg.noise_enabled:
                V_measured += self._rng.normal(0, cfg.voltage_noise_std)
                I_measured += self._rng.normal(0, cfg.current_noise_std)
                V_measured = max(0.0, V_measured)
                I_measured = max(0.0, I_measured)

            # ── 4. MPPT controller (runs at its own sampling rate) ────
            if t >= next_mppt_time:
                D = self.mppt.step(V_measured, I_measured, D)
                D = self.converter.clamp_duty_cycle(D)
                next_mppt_time = t + cfg.mppt_period

            # ── 5. Update converter ───────────────────────────────────
            conv_result = self.converter.update(V_pv, D, cfg.dt, I_in=I_pv)

            # ── 6. Independent MPP calculation (validation) ───────────
            if is_array:
                Vmp, Imp, Pmp = self.pv.find_mpp()
            else:
                Vmp, Imp, Pmp = self.pv.find_mpp()

            # ── 7. Record all state variables ─────────────────────────
            tracking_error = abs(P_pv - Pmp)
            tracking_eff = (P_pv / Pmp * 100.0) if Pmp > 0 else 0.0

            records['time'][i] = t
            records['irradiance'][i] = G
            records['temperature'][i] = T
            records['pv_voltage'][i] = V_pv
            records['pv_current'][i] = I_pv
            records['pv_power'][i] = P_pv
            records['duty_cycle'][i] = D
            records['out_voltage'][i] = conv_result['V_out']
            records['out_current'][i] = conv_result['I_out']
            records['out_power'][i] = conv_result['P_out']
            records['mpp_voltage'][i] = Vmp
            records['mpp_current'][i] = Imp
            records['mpp_power'][i] = Pmp
            records['tracking_error'][i] = tracking_error
            records['tracking_efficiency'][i] = tracking_eff
            records['converter_efficiency'][i] = conv_result['efficiency']
            records['converter_loss'][i] = conv_result['P_loss']

        # Build DataFrame
        df = pd.DataFrame(records)

        # Determine PV params
        if is_array:
            pv_params = self.pv.modules[0].params
        else:
            pv_params = self.pv.params

        return SimulationResult(
            config=cfg,
            scenario_name=self.scenario.name,
            algorithm_name=self.mppt.name,
            data=df,
            pv_params=pv_params,
        )

    def _get_array_operating_point(self, D: float) -> tuple[float, float]:
        """Find operating point for a PV array.

        For arrays, we use the array's aggregate I-V curve
        and find where it intersects the converter load line.
        """
        D = self.converter.clamp_duty_cycle(D)

        if hasattr(self.converter.load, 'R'):
            R_load = self.converter.load.R
        else:
            R_load = 100.0

        eta = self.converter.params.efficiency_nominal
        R_in_eff = R_load * ((1 - D) ** 2) / eta
        R_in_eff = min(R_in_eff, 1e4)
        R_in_eff = max(R_in_eff, 0.1)

        # Get array I-V curve
        V_arr, I_arr = self.pv.get_iv_curve(num_points=500)

        # Load line: I = V / R_in_eff
        I_load = V_arr / R_in_eff

        # Find intersection
        residual = I_arr - I_load
        sign_changes = np.where(np.diff(np.sign(residual)))[0]

        if len(sign_changes) > 0:
            # Multiple crossings possible under partial shading
            # Find the one with maximum power
            best_P = 0
            best_V = 0
            best_I = 0
            for idx in sign_changes:
                V_mid = (V_arr[idx] + V_arr[idx + 1]) / 2
                I_mid = (I_arr[idx] + I_arr[idx + 1]) / 2
                P_mid = V_mid * I_mid
                if P_mid > best_P:
                    best_P = P_mid
                    best_V = V_mid
                    best_I = I_mid
            return best_V, best_I
        else:
            # No crossing; use minimum residual
            idx = np.argmin(np.abs(residual))
            return float(V_arr[idx]), float(I_arr[idx])


def run_quick_simulation(
    G: float = 1000.0,
    T: float = 25.0,
    algorithm: str = 'P&O',
    duration: float = 20.0,
    dt: float = 0.001,
    mppt_period: float = 0.050,
    D_step: float = 0.005,
    D_init: float = 0.5,
    R_load: float = 20.0,
    pv_params: Optional[PVModuleParams] = None,
) -> SimulationResult:
    """Convenience function to run a simulation with minimal setup.

    Args:
        G: Irradiance [W/m²]
        T: Temperature [°C]
        algorithm: 'P&O' or 'INC'
        duration: Simulation time [s]
        dt: Timestep [s]
        mppt_period: MPPT sampling period [s]
        D_step: Perturbation step for MPPT
        D_init: Initial duty cycle
        R_load: Load resistance [Ω]
        pv_params: PV module parameters (default: CS3U-400MS)

    Returns:
        SimulationResult
    """
    pv = PVModule(pv_params or PVModuleParams())
    load = ResistiveLoad(R=R_load)
    converter = BoostConverter(BoostConverterParams(), load)

    if algorithm.upper() in ('P&O', 'PO', 'PERTURB'):
        mppt = PerturbAndObserve(D_init=D_init, D_step=D_step)
    elif algorithm.upper() in ('INC', 'INCCOND', 'INCREMENTAL'):
        mppt = IncrementalConductance(D_init=D_init, D_step=D_step)
    else:
        raise ValueError(f"Unknown MPPT algorithm: {algorithm}")

    scenario = ConstantConditions(
        name=f"G={G}, T={T}",
        description=f"Constant irradiance {G} W/m², temperature {T} °C",
        G=G, T=T, duration=duration
    )

    config = SimulationConfig(
        duration=duration, dt=dt, mppt_period=mppt_period, D_init=D_init
    )

    engine = SimulationEngine(pv, converter, mppt, scenario, config)
    return engine.run()
