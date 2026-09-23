#!/usr/bin/env python3
"""
MPPT Simulation Software — CLI Entry Point
============================================

Usage:
    python main.py                          # Run all experiments
    python main.py --quick                  # Quick single simulation
    python main.py --quick --algorithm INC  # Quick simulation with INC
    python main.py --validate               # Run validation only
"""

import argparse
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

import numpy as np

from models.pv_model import PVModule, PVModuleParams
from models.converter import BoostConverter, BoostConverterParams
from models.load import ResistiveLoad
from mppt.perturb_observe import PerturbAndObserve
from mppt.incremental_conductance import IncrementalConductance
from simulation.engine import SimulationEngine, SimulationConfig, run_quick_simulation
from simulation.scenarios import ConstantConditions, ScenarioConfig
from analysis.metrics import compute_metrics, format_metrics
from analysis.validation import validate_simulation, format_validation_report
from visualization.plots import (
    plot_iv_curve, plot_pv_curve, plot_simulation_dashboard,
    plot_pv_curves_irradiance, plot_pv_curves_temperature,
)


def run_quick(args):
    """Run a quick single simulation and print results."""
    print("=" * 60)
    print("MPPT Simulation — Quick Run")
    print("=" * 60)

    pv_params = PVModuleParams()
    pv = PVModule(pv_params)

    # Print PV module info
    pv.set_conditions(args.irradiance, args.temperature)
    Vmp, Imp, Pmax = pv.find_mpp()
    print(f"\nPV Module (at G={args.irradiance} W/m², T={args.temperature}°C):")
    print(f"  Voc  = {pv.get_voc():.2f} V")
    print(f"  Isc  = {pv.get_isc():.2f} A")
    print(f"  Vmp  = {Vmp:.2f} V")
    print(f"  Imp  = {Imp:.2f} A")
    print(f"  Pmax = {Pmax:.1f} W")

    # Run simulation
    print(f"\nRunning simulation ({args.algorithm}, {args.duration}s)...")
    result = run_quick_simulation(
        G=args.irradiance,
        T=args.temperature,
        algorithm=args.algorithm,
        duration=args.duration,
        dt=args.dt,
        mppt_period=args.mppt_period,
        D_step=args.d_step,
        D_init=args.d_init,
        R_load=args.r_load,
    )

    # Compute metrics
    metrics = compute_metrics(result)
    print(f"\n{'RESULTS':=^60}")
    print(format_metrics(metrics))

    # Validate
    validation = validate_simulation(result, pv)
    print(f"\n{'VALIDATION':=^60}")
    print(format_validation_report(validation))

    # Save outputs
    output_dir = os.path.join(str(project_root), 'experiments', 'results', 'quick_run')
    os.makedirs(output_dir, exist_ok=True)

    result.data.to_csv(os.path.join(output_dir, 'quick_data.csv'), index=False)
    plot_simulation_dashboard(result, save_path=os.path.join(output_dir, 'quick_dashboard.png'))
    plot_iv_curve(pv, args.irradiance, args.temperature,
                  save_path=os.path.join(output_dir, 'quick_iv.png'))
    plot_pv_curve(pv, args.irradiance, args.temperature,
                  save_path=os.path.join(output_dir, 'quick_pv.png'))

    print(f"\nOutputs saved to: {os.path.abspath(output_dir)}")


def run_experiments(args):
    """Run the full experiment suite."""
    from experiments.run_experiments import run_all_experiments
    output_dir = os.path.join(str(project_root), 'experiments', 'results')
    run_all_experiments(output_base=output_dir)


def run_validate(args):
    """Run validation checks on the PV model."""
    print("=" * 60)
    print("MPPT Simulation — PV Model Validation")
    print("=" * 60)

    pv_params = PVModuleParams()
    pv = PVModule(pv_params)
    issues = pv_params.validate()

    print(f"\nPV Module Parameters:")
    print(f"  Ns    = {pv_params.Ns}")
    print(f"  Voc   = {pv_params.Voc:.2f} V")
    print(f"  Isc   = {pv_params.Isc:.2f} A")
    print(f"  Vmp   = {pv_params.Vmp:.2f} V")
    print(f"  Imp   = {pv_params.Imp:.2f} A")
    print(f"  Pmax  = {pv_params.Pmax:.2f} W (datasheet)")
    print(f"  Rs    = {pv_params.Rs:.4f} Ohm")
    print(f"  Rsh   = {pv_params.Rsh:.1f} Ohm")
    print(f"  n     = {pv_params.n:.3f}")
    print(f"  Iph0  = {pv_params.Iph0:.4f} A")
    print(f"  I0_0  = {pv_params.I0_0:.4e} A")

    if issues:
        print(f"\n[!] Parameter warnings:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print(f"\n[OK] All parameter checks passed")

    # Validate at different conditions
    conditions = [
        (1000, 25, "STC"),
        (800, 25, "800 W/m2"),
        (600, 25, "600 W/m2"),
        (1000, 40, "40 C"),
        (1000, 55, "55 C"),
    ]

    print(f"\n{'Condition':<15} {'Voc (V)':<10} {'Isc (A)':<10} {'Vmp (V)':<10} "
          f"{'Imp (A)':<10} {'Pmax (W)':<10}")
    print("-" * 65)

    for G, T, label in conditions:
        pv.set_conditions(G, T)
        voc = pv.get_voc()
        isc = pv.get_isc()
        vmp, imp, pmax = pv.find_mpp()
        print(f"{label:<15} {voc:<10.2f} {isc:<10.2f} {vmp:<10.2f} {imp:<10.2f} {pmax:<10.1f}")

    # Verify physical trends
    print(f"\nPhysical trend checks:")
    pv.set_conditions(1000, 25)
    _, _, p1000 = pv.find_mpp()
    pv.set_conditions(800, 25)
    _, _, p800 = pv.find_mpp()
    pv.set_conditions(1000, 45)
    _, _, p_hot = pv.find_mpp()

    check1 = p1000 > p800
    check2 = p1000 > p_hot
    print(f"  {'[OK]' if check1 else '[FAIL]'} Higher irradiance -> higher power ({p1000:.1f} > {p800:.1f})")
    print(f"  {'[OK]' if check2 else '[FAIL]'} Higher temperature -> lower power ({p1000:.1f} > {p_hot:.1f})")


def main():
    parser = argparse.ArgumentParser(
        description='MPPT Simulation Software for Photovoltaic Systems',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          Run all 7 experiments
  python main.py --quick                  Quick simulation at STC
  python main.py --quick -G 800 -T 35     Custom conditions
  python main.py --quick --algorithm INC  Use Incremental Conductance
  python main.py --validate               Validate PV model
        """
    )

    parser.add_argument('--quick', action='store_true',
                        help='Run a quick single simulation')
    parser.add_argument('--validate', action='store_true',
                        help='Run PV model validation only')

    # Quick-run parameters
    parser.add_argument('-G', '--irradiance', type=float, default=1000.0,
                        help='Irradiance [W/m²] (default: 1000)')
    parser.add_argument('-T', '--temperature', type=float, default=25.0,
                        help='Cell temperature [°C] (default: 25)')
    parser.add_argument('--algorithm', type=str, default='P&O',
                        choices=['P&O', 'INC'],
                        help='MPPT algorithm (default: P&O)')
    parser.add_argument('--duration', type=float, default=20.0,
                        help='Simulation duration [s] (default: 20)')
    parser.add_argument('--dt', type=float, default=0.001,
                        help='Timestep [s] (default: 0.001)')
    parser.add_argument('--mppt-period', type=float, default=0.050,
                        help='MPPT sampling period [s] (default: 0.05)')
    parser.add_argument('--d-step', type=float, default=0.005,
                        help='Duty cycle perturbation step (default: 0.005)')
    parser.add_argument('--d-init', type=float, default=0.5,
                        help='Initial duty cycle (default: 0.5)')
    parser.add_argument('--r-load', type=float, default=20.0,
                        help='Load resistance [Ω] (default: 20)')

    args = parser.parse_args()

    if args.validate:
        run_validate(args)
    elif args.quick:
        run_quick(args)
    else:
        run_experiments(args)


if __name__ == '__main__':
    main()
