"""
Automated Experiment Suite
==========================

Runs 7 pre-defined experiments comparing MPPT algorithms under
different environmental conditions. Each experiment produces:
  - CSV data file
  - Numerical summary (TXT)
  - PNG graphs
  - Comparison tables
"""

from __future__ import annotations

import os
import sys
import time as time_mod
from pathlib import Path

import numpy as np
import pandas as pd

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.pv_model import PVModule, PVModuleParams, PVArray
from models.converter import BoostConverter, BoostConverterParams
from models.load import ResistiveLoad
from mppt.perturb_observe import PerturbAndObserve
from mppt.incremental_conductance import IncrementalConductance
from mppt.global_mppt import ScanningGlobalMPPT
from simulation.engine import SimulationEngine, SimulationConfig
from simulation.scenarios import (
    ConstantConditions, IrradianceStep, TemperatureRamp,
    CombinedVariation, PartialShading, ScenarioConfig,
)
from analysis.metrics import compute_metrics, format_metrics, compare_algorithms
from analysis.validation import validate_simulation, format_validation_report
from visualization.plots import (
    plot_iv_curve, plot_pv_curve,
    plot_iv_curves_irradiance, plot_pv_curves_irradiance,
    plot_pv_curves_temperature,
    plot_mppt_power, plot_pv_voltage, plot_pv_current,
    plot_duty_cycle, plot_irradiance, plot_temperature,
    plot_mpp_comparison, plot_tracking_error, plot_tracking_efficiency,
    plot_convergence, plot_algorithm_comparison,
    plot_partial_shading_pv, plot_simulation_dashboard,
)


def _ensure_dir(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return path


def _run_single_experiment(
    name: str,
    scenario,
    pv,
    mppt_cls,
    mppt_kwargs: dict,
    output_dir: str,
    config: SimulationConfig,
    is_array: bool = False,
) -> dict:
    """Run a single experiment and save all outputs."""
    print(f"  Running {name} with {mppt_cls.__name__}...")

    mppt = mppt_cls(**mppt_kwargs)
    load = ResistiveLoad(R=20.0)
    converter = BoostConverter(BoostConverterParams(), load)

    engine = SimulationEngine(pv, converter, mppt, scenario, config)

    t0 = time_mod.perf_counter()
    result = engine.run()
    elapsed = time_mod.perf_counter() - t0

    # Compute metrics
    metrics = compute_metrics(result)
    metrics['wall_time_s'] = elapsed

    # Validate
    validation = validate_simulation(result, pv)

    # Save CSV
    csv_path = os.path.join(output_dir, f"{name}_data.csv")
    result.data.to_csv(csv_path, index=False)

    # Save summary
    summary_path = os.path.join(output_dir, f"{name}_summary.txt")
    with open(summary_path, 'w') as f:
        f.write(f"Experiment: {name}\n")
        f.write(f"Algorithm: {result.algorithm_name}\n")
        f.write(f"Scenario: {result.scenario_name}\n")
        f.write(f"Simulation Time: {elapsed:.2f}s\n")
        f.write("=" * 60 + "\n\n")
        f.write("METRICS\n")
        f.write("-" * 40 + "\n")
        f.write(format_metrics(metrics))
        f.write("\n\n")
        f.write("VALIDATION\n")
        f.write("-" * 40 + "\n")
        f.write(format_validation_report(validation))

    # Save key plots
    plot_mppt_power(result, save_path=os.path.join(output_dir, f"{name}_power.png"))
    plot_pv_voltage(result, save_path=os.path.join(output_dir, f"{name}_voltage.png"))
    plot_duty_cycle(result, save_path=os.path.join(output_dir, f"{name}_duty_cycle.png"))
    plot_tracking_efficiency(result, save_path=os.path.join(output_dir, f"{name}_efficiency.png"))
    plot_tracking_error(result, save_path=os.path.join(output_dir, f"{name}_error.png"))
    plot_mpp_comparison(result, save_path=os.path.join(output_dir, f"{name}_mpp_comparison.png"))
    plot_convergence(result, save_path=os.path.join(output_dir, f"{name}_convergence.png"))
    plot_simulation_dashboard(result, save_path=os.path.join(output_dir, f"{name}_dashboard.png"))

    return {
        'result': result,
        'metrics': metrics,
        'validation': validation,
    }


def run_all_experiments(output_base: str = None) -> dict:
    """Run the complete experiment suite.

    Returns a dictionary of experiment results.
    """
    if output_base is None:
        output_base = os.path.join(os.path.dirname(__file__), 'results')

    _ensure_dir(output_base)

    pv_params = PVModuleParams()
    config = SimulationConfig(duration=20.0, dt=0.001, mppt_period=0.050, D_init=0.5)
    mppt_kwargs = {'D_init': 0.5, 'D_step': 0.005}

    all_results = {}

    print("=" * 70)
    print("MPPT Simulation -- Automated Experiment Suite")
    print("=" * 70)

    # ── Static PV curves (not time-domain) ─────────────────────────────
    print("\n[0] Generating static PV characteristic curves...")
    static_dir = _ensure_dir(os.path.join(output_base, '00_pv_characteristics'))
    pv_static = PVModule(pv_params)

    plot_iv_curve(pv_static, G=1000, T=25,
                  save_path=os.path.join(static_dir, 'iv_curve_stc.png'))
    plot_pv_curve(pv_static, G=1000, T=25,
                  save_path=os.path.join(static_dir, 'pv_curve_stc.png'))
    plot_iv_curves_irradiance(pv_static,
                              save_path=os.path.join(static_dir, 'iv_curves_irradiance.png'))
    plot_pv_curves_irradiance(pv_static,
                              save_path=os.path.join(static_dir, 'pv_curves_irradiance.png'))
    plot_pv_curves_temperature(pv_static,
                               save_path=os.path.join(static_dir, 'pv_curves_temperature.png'))
    print("  [OK] Saved 5 static characteristic curves")

    # ── Experiment 1: Constant STC ─────────────────────────────────────
    print("\n[1] Experiment 1: Constant 1000 W/m2, 25 deg C")
    exp1_dir = _ensure_dir(os.path.join(output_base, '01_constant_stc'))
    scenario1 = ConstantConditions('STC', 'Constant 1000 W/m2, 25 deg C', 1000, 25, 20.0)
    pv1 = PVModule(pv_params)
    all_results['exp1_po'] = _run_single_experiment(
        'exp1_po', scenario1, pv1, PerturbAndObserve, mppt_kwargs, exp1_dir, config)
    pv1b = PVModule(pv_params)
    all_results['exp1_inc'] = _run_single_experiment(
        'exp1_inc', scenario1, pv1b, IncrementalConductance, mppt_kwargs, exp1_dir, config)

    # ── Experiment 2: Irradiance drop ──────────────────────────────────
    print("\n[2] Experiment 2: Irradiance 1000 -> 700 W/m2")
    exp2_dir = _ensure_dir(os.path.join(output_base, '02_irradiance_drop'))
    scenario2 = IrradianceStep('Irr Drop', 'G: 1000->700 at t=10s', 1000, 700, 25, 10.0, 20.0)
    pv2 = PVModule(pv_params)
    all_results['exp2'] = _run_single_experiment(
        'exp2_po', scenario2, pv2, PerturbAndObserve, mppt_kwargs, exp2_dir, config)
    plot_irradiance(all_results['exp2']['result'],
                    save_path=os.path.join(exp2_dir, 'exp2_irradiance.png'))

    # ── Experiment 3: Irradiance rise ──────────────────────────────────
    print("\n[3] Experiment 3: Irradiance 700 -> 1000 W/m2")
    exp3_dir = _ensure_dir(os.path.join(output_base, '03_irradiance_rise'))
    scenario3 = IrradianceStep('Irr Rise', 'G: 700->1000 at t=10s', 700, 1000, 25, 10.0, 20.0)
    pv3 = PVModule(pv_params)
    all_results['exp3'] = _run_single_experiment(
        'exp3_po', scenario3, pv3, PerturbAndObserve, mppt_kwargs, exp3_dir, config)
    plot_irradiance(all_results['exp3']['result'],
                    save_path=os.path.join(exp3_dir, 'exp3_irradiance.png'))

    # ── Experiment 4: Temperature rise ─────────────────────────────────
    print("\n[4] Experiment 4: Temperature 25 -> 45 deg C")
    exp4_dir = _ensure_dir(os.path.join(output_base, '04_temperature_rise'))
    scenario4 = TemperatureRamp('Temp Rise', 'T: 25->45 deg C at t=10s', 1000, 25, 45, 10.0, 20.0)
    pv4 = PVModule(pv_params)
    all_results['exp4'] = _run_single_experiment(
        'exp4_po', scenario4, pv4, PerturbAndObserve, mppt_kwargs, exp4_dir, config)
    plot_temperature(all_results['exp4']['result'],
                     save_path=os.path.join(exp4_dir, 'exp4_temperature.png'))

    # ── Experiment 5: Combined variation ───────────────────────────────
    print("\n[5] Experiment 5: Combined irradiance + temperature")
    exp5_dir = _ensure_dir(os.path.join(output_base, '05_combined'))
    config5 = SimulationConfig(duration=30.0, dt=0.001, mppt_period=0.050, D_init=0.5)
    scenario5 = CombinedVariation('Combined', 'G: 1000->700 at t=10s, T: 25->40 at t=15s', 30.0)
    pv5 = PVModule(pv_params)
    all_results['exp5'] = _run_single_experiment(
        'exp5_po', scenario5, pv5, PerturbAndObserve, mppt_kwargs, exp5_dir, config5)
    plot_irradiance(all_results['exp5']['result'],
                    save_path=os.path.join(exp5_dir, 'exp5_irradiance.png'))
    plot_temperature(all_results['exp5']['result'],
                     save_path=os.path.join(exp5_dir, 'exp5_temperature.png'))

    # ── Experiment 6: Partial shading ──────────────────────────────────
    print("\n[6] Experiment 6: Partial shading")
    exp6_dir = _ensure_dir(os.path.join(output_base, '06_partial_shading'))

    # Create PV array with 3 modules
    pv_array = PVArray(n_modules=3, params=pv_params)
    pv_array.set_conditions([1000, 600, 300], [25, 25, 25])

    # Plot the multi-peak P-V curve
    plot_partial_shading_pv(pv_array,
                            save_path=os.path.join(exp6_dir, 'partial_shading_pv.png'))

    # Run simulation with P&O (will likely get trapped at local max)
    scenario6 = PartialShading(
        'Partial Shading', 'Modules at [1000, 600, 300] W/m2',
        20.0, [1000, 600, 300], [25, 25, 25]
    )
    pv_array_sim = PVArray(n_modules=3, params=pv_params)
    all_results['exp6_po'] = _run_single_experiment(
        'exp6_po', scenario6, pv_array_sim, PerturbAndObserve, mppt_kwargs,
        exp6_dir, config, is_array=True)

    # Document partial shading behavior
    gmpp = pv_array.find_mpp()
    maxima = pv_array.find_all_local_maxima()
    with open(os.path.join(exp6_dir, 'partial_shading_analysis.txt'), 'w') as f:
        f.write("Partial Shading Analysis\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Module irradiances: [1000, 600, 300] W/m2\n")
        f.write(f"Module temperatures: [25, 25, 25]  deg C\n\n")
        f.write(f"Global Maximum Power Point (GMPP):\n")
        f.write(f"  V = {gmpp[0]:.2f} V, I = {gmpp[1]:.2f} A, P = {gmpp[2]:.1f} W\n\n")
        f.write(f"All local maxima (sorted by power):\n")
        for i, (v, I, p) in enumerate(maxima):
            label = "GMPP" if i == 0 else f"LMPP-{i}"
            f.write(f"  {label}: V = {v:.2f} V, I = {I:.2f} A, P = {p:.1f} W\n")
        f.write(f"\nTotal peaks found: {len(maxima)}\n\n")
        f.write("NOTE: Conventional P&O can become trapped around a local maximum\n")
        f.write("under partial shading. It does NOT always find the global maximum.\n")
        f.write("A scanning-based or global MPPT algorithm is needed for reliable\n")
        f.write("global MPP tracking under partial shading conditions.\n")

    # ── Experiment 7: P&O vs INC comparison ────────────────────────────
    print("\n[7] Experiment 7: P&O vs Incremental Conductance comparison")
    exp7_dir = _ensure_dir(os.path.join(output_base, '07_algorithm_comparison'))

    # Run both algorithms on the same scenario
    scenario7 = IrradianceStep('Comparison', 'G: 1000->600 at t=10s', 1000, 600, 25, 10.0, 20.0)

    pv7a = PVModule(pv_params)
    all_results['exp7_po'] = _run_single_experiment(
        'exp7_po', scenario7, pv7a, PerturbAndObserve, mppt_kwargs, exp7_dir, config)

    pv7b = PVModule(pv_params)
    all_results['exp7_inc'] = _run_single_experiment(
        'exp7_inc', scenario7, pv7b, IncrementalConductance, mppt_kwargs, exp7_dir, config)

    # Comparison plot
    plot_algorithm_comparison(
        [all_results['exp7_po']['result'], all_results['exp7_inc']['result']],
        save_path=os.path.join(exp7_dir, 'algorithm_comparison.png')
    )

    # Comparison table
    comp_table = compare_algorithms([
        all_results['exp7_po']['result'],
        all_results['exp7_inc']['result'],
    ])
    comp_table.to_csv(os.path.join(exp7_dir, 'comparison_table.csv'))
    with open(os.path.join(exp7_dir, 'comparison_table.txt'), 'w') as f:
        f.write("Algorithm Comparison\n")
        f.write("=" * 60 + "\n\n")
        f.write(comp_table.to_string())

    # ── Print overall summary ──────────────────────────────────────────
    print("\n" + "=" * 70)
    print("EXPERIMENT SUITE COMPLETE")
    print("=" * 70)
    print(f"\nResults saved to: {os.path.abspath(output_base)}")
    print(f"\nTotal experiments: {len(all_results)}")

    # Print quick summary of key metrics
    print("\n" + "-" * 70)
    print(f"{'Experiment':<25} {'Algorithm':<20} {'Eff_MPPT (%)':<15} {'Settling (s)':<15}")
    print("-" * 70)
    for key, data in all_results.items():
        m = data['metrics']
        name = data['result'].scenario_name
        algo = data['result'].algorithm_name
        eta = m.get('steady_state_tracking_efficiency', 0)
        settle = m.get('settling_time', float('nan'))
        settle_str = f"{settle:.3f}" if not np.isnan(settle) else "N/A"
        print(f"{name:<25} {algo:<20} {eta:<15.2f} {settle_str:<15}")
    print("-" * 70)

    return all_results


if __name__ == '__main__':
    run_all_experiments()
