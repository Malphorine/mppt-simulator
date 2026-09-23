"""
MPPT Simulation Dashboard — Streamlit App
==========================================

Engineering dashboard for interactive MPPT simulation.
Run with: streamlit run app.py
"""

import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from models.pv_model import PVModule, PVModuleParams, PVArray
from models.converter import BoostConverter, BoostConverterParams
from models.load import ResistiveLoad
from mppt.perturb_observe import PerturbAndObserve
from mppt.incremental_conductance import IncrementalConductance
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


st.set_page_config(
    page_title="MPPT Simulator",
    page_icon="☀️",
    layout="wide",
)


def main():
    st.title("☀️ MPPT Simulation Dashboard")
    st.markdown("Engineering-grade Maximum Power Point Tracking simulator for PV systems")

    # ── Sidebar: Configuration ─────────────────────────────────────────
    st.sidebar.header("⚙️ Configuration")

    st.sidebar.subheader("Environmental Conditions")
    scenario_type = st.sidebar.selectbox(
        "Scenario",
        ["Constant", "Irradiance Step Down", "Irradiance Step Up",
         "Temperature Rise", "Combined", "Partial Shading"]
    )

    G = st.sidebar.slider("Irradiance G (W/m²)", 100, 1200, 1000, step=50)
    T = st.sidebar.slider("Temperature T (°C)", 0, 70, 25, step=1)

    if scenario_type in ["Irradiance Step Down", "Irradiance Step Up"]:
        G_end = st.sidebar.slider("G after change (W/m²)", 100, 1200, 600, step=50)
        t_change = st.sidebar.slider("Change time (s)", 1.0, 15.0, 10.0, step=0.5)

    if scenario_type == "Temperature Rise":
        T_end = st.sidebar.slider("T after change (°C)", 0, 70, 45, step=1)
        t_change_T = st.sidebar.slider("Change time (s)", 1.0, 15.0, 10.0, step=0.5)

    if scenario_type == "Partial Shading":
        st.sidebar.markdown("**Per-module irradiance:**")
        G1 = st.sidebar.slider("Module 1 G (W/m²)", 100, 1200, 1000, step=50)
        G2 = st.sidebar.slider("Module 2 G (W/m²)", 100, 1200, 600, step=50)
        G3 = st.sidebar.slider("Module 3 G (W/m²)", 100, 1200, 300, step=50)

    st.sidebar.subheader("PV Module")
    Ns = st.sidebar.number_input("Cells in series", 36, 144, 72)
    Voc = st.sidebar.number_input("Voc (V)", 20.0, 100.0, 48.6, step=0.1)
    Isc = st.sidebar.number_input("Isc (A)", 1.0, 20.0, 10.33, step=0.01)
    Vmp = st.sidebar.number_input("Vmp (V)", 15.0, 80.0, 40.8, step=0.1)
    Imp = st.sidebar.number_input("Imp (A)", 1.0, 20.0, 9.81, step=0.01)

    st.sidebar.subheader("Converter & Load")
    R_load = st.sidebar.slider("Load R (Ω)", 5.0, 100.0, 20.0, step=1.0)
    eta_conv = st.sidebar.slider("Converter efficiency", 0.80, 1.0, 0.95, step=0.01)

    st.sidebar.subheader("MPPT Algorithm")
    algorithm = st.sidebar.selectbox("Algorithm", ["P&O", "Incremental Conductance", "Compare Both"])
    D_step = st.sidebar.number_input("Perturbation step ΔD", 0.001, 0.05, 0.005, step=0.001, format="%.3f")
    D_init = st.sidebar.slider("Initial duty cycle", 0.1, 0.9, 0.5, step=0.05)

    st.sidebar.subheader("Simulation")
    duration = st.sidebar.slider("Duration (s)", 5.0, 60.0, 20.0, step=1.0)
    dt = st.sidebar.selectbox("Timestep (s)", [0.0005, 0.001, 0.002, 0.005], index=1)
    mppt_period = st.sidebar.selectbox("MPPT period (s)", [0.020, 0.050, 0.100, 0.200], index=1)

    # ── Run button ─────────────────────────────────────────────────────
    col_run, col_reset = st.sidebar.columns(2)
    run_sim = col_run.button("🚀 Run Simulation", use_container_width=True)
    reset = col_reset.button("🔄 Reset", use_container_width=True)

    if reset:
        st.session_state.clear()
        st.rerun()

    # ── Build PV params ────────────────────────────────────────────────
    pv_params = PVModuleParams(
        Ns=Ns, Voc=Voc, Isc=Isc, Vmp=Vmp, Imp=Imp,
        Pmax=Vmp * Imp
    )

    # ── Static curves tab ──────────────────────────────────────────────
    tab_static, tab_sim, tab_metrics, tab_export = st.tabs(
        ["📊 PV Characteristics", "📈 Simulation Results", "📋 Metrics & Validation", "💾 Export"]
    )

    with tab_static:
        st.subheader("PV Module Characteristics")
        pv_static = PVModule(pv_params)

        col1, col2 = st.columns(2)
        with col1:
            fig_iv = plot_iv_curve(pv_static, G, T)
            st.pyplot(fig_iv)
            plt.close(fig_iv)
        with col2:
            fig_pv = plot_pv_curve(pv_static, G, T)
            st.pyplot(fig_pv)
            plt.close(fig_pv)

        col3, col4 = st.columns(2)
        with col3:
            fig_irr = plot_pv_curves_irradiance(pv_static)
            st.pyplot(fig_irr)
            plt.close(fig_irr)
        with col4:
            fig_temp = plot_pv_curves_temperature(pv_static)
            st.pyplot(fig_temp)
            plt.close(fig_temp)

        # Show MPP info
        pv_static.set_conditions(G, T)
        vmp_val, imp_val, pmax_val = pv_static.find_mpp()
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Vmp", f"{vmp_val:.2f} V")
        col_m2.metric("Imp", f"{imp_val:.2f} A")
        col_m3.metric("Pmax", f"{pmax_val:.1f} W")
        col_m4.metric("Voc", f"{pv_static.get_voc():.2f} V")

    # ── Run simulation ─────────────────────────────────────────────────
    if run_sim:
        with st.spinner("Running simulation..."):
            # Build scenario
            if scenario_type == "Constant":
                scenario = ConstantConditions("Constant", f"G={G}, T={T}", G, T, duration)
            elif scenario_type == "Irradiance Step Down":
                scenario = IrradianceStep("Irr Drop", f"G: {G}→{G_end}", G, G_end, T, t_change, duration)
            elif scenario_type == "Irradiance Step Up":
                scenario = IrradianceStep("Irr Rise", f"G: {G}→{G_end}", G, G_end, T, t_change, duration)
            elif scenario_type == "Temperature Rise":
                scenario = TemperatureRamp("Temp Rise", f"T: {T}→{T_end}", G, T, T_end, t_change_T, duration)
            elif scenario_type == "Combined":
                scenario = CombinedVariation("Combined", "G+T variation", duration)
            elif scenario_type == "Partial Shading":
                scenario = PartialShading("Partial Shading", "Multi-module",
                                          duration, [G1, G2, G3], [T, T, T])

            config = SimulationConfig(duration=duration, dt=dt, mppt_period=mppt_period, D_init=D_init)
            conv_params = BoostConverterParams(efficiency_nominal=eta_conv)

            results = []

            algorithms_to_run = []
            if algorithm == "P&O":
                algorithms_to_run = [("P&O", PerturbAndObserve)]
            elif algorithm == "Incremental Conductance":
                algorithms_to_run = [("INC", IncrementalConductance)]
            else:
                algorithms_to_run = [("P&O", PerturbAndObserve), ("INC", IncrementalConductance)]

            for algo_name, algo_cls in algorithms_to_run:
                mppt = algo_cls(D_init=D_init, D_step=D_step)
                load = ResistiveLoad(R=R_load)
                converter = BoostConverter(conv_params, load)

                if scenario_type == "Partial Shading":
                    pv = PVArray(n_modules=3, params=pv_params)
                else:
                    pv = PVModule(pv_params)

                engine = SimulationEngine(pv, converter, mppt, scenario, config)
                result = engine.run()
                results.append(result)

            st.session_state['results'] = results
            st.session_state['scenario_type'] = scenario_type
            if scenario_type == "Partial Shading":
                pv_arr = PVArray(n_modules=3, params=pv_params)
                pv_arr.set_conditions([G1, G2, G3], [T, T, T])
                st.session_state['pv_array'] = pv_arr

    # ── Display results ────────────────────────────────────────────────
    if 'results' in st.session_state:
        results = st.session_state['results']

        with tab_sim:
            st.subheader("Simulation Results")

            for result in results:
                st.markdown(f"### {result.algorithm_name}")

                # Key metrics at top
                d = result.data
                last = d.iloc[-1]
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("PV Power", f"{last['pv_power']:.1f} W")
                col2.metric("PV Voltage", f"{last['pv_voltage']:.2f} V")
                col3.metric("PV Current", f"{last['pv_current']:.2f} A")
                col4.metric("Duty Cycle", f"{last['duty_cycle']:.4f}")
                col5.metric("η_MPPT", f"{last['tracking_efficiency']:.1f}%")

                # Dashboard plot
                fig_dash = plot_simulation_dashboard(result)
                st.pyplot(fig_dash)
                plt.close(fig_dash)

                # Additional plots in expander
                with st.expander("📊 Detailed Plots"):
                    c1, c2 = st.columns(2)
                    with c1:
                        fig = plot_mppt_power(result)
                        st.pyplot(fig)
                        plt.close(fig)
                        fig = plot_tracking_error(result)
                        st.pyplot(fig)
                        plt.close(fig)
                    with c2:
                        fig = plot_tracking_efficiency(result)
                        st.pyplot(fig)
                        plt.close(fig)
                        fig = plot_convergence(result)
                        st.pyplot(fig)
                        plt.close(fig)

            # Algorithm comparison
            if len(results) > 1:
                st.markdown("### Algorithm Comparison")
                fig_comp = plot_algorithm_comparison(results)
                st.pyplot(fig_comp)
                plt.close(fig_comp)

            # Partial shading P-V curve
            if st.session_state.get('scenario_type') == "Partial Shading" and 'pv_array' in st.session_state:
                st.markdown("### Partial Shading P-V Curve")
                fig_ps = plot_partial_shading_pv(st.session_state['pv_array'])
                st.pyplot(fig_ps)
                plt.close(fig_ps)

        with tab_metrics:
            st.subheader("Engineering Metrics & Validation")

            for result in results:
                st.markdown(f"### {result.algorithm_name}")
                metrics = compute_metrics(result)

                # Display metrics in columns
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown("**Power Metrics**")
                    st.write(f"Max Theoretical: {metrics['max_theoretical_power']:.1f} W")
                    st.write(f"Max Tracked: {metrics['max_tracked_power']:.1f} W")
                    st.write(f"Avg Tracked: {metrics['avg_tracked_power']:.1f} W")
                    st.write(f"Energy Harvested: {metrics['energy_harvested']:.1f} J")
                with c2:
                    st.markdown("**Tracking Performance**")
                    st.write(f"Avg Efficiency: {metrics['avg_tracking_efficiency']:.2f}%")
                    st.write(f"SS Efficiency: {metrics['steady_state_tracking_efficiency']:.2f}%")
                    st.write(f"SS Error: {metrics['steady_state_error']:.2f} W")
                    settle = metrics['settling_time']
                    st.write(f"Settling Time: {settle:.3f}s" if not np.isnan(settle) else "Settling Time: N/A")
                with c3:
                    st.markdown("**System Efficiency**")
                    st.write(f"Converter Eff: {metrics['avg_converter_efficiency']:.2f}")
                    st.write(f"Power Oscillation: {metrics['power_oscillation']:.2f} W")
                    st.write(f"Total System Eff: {metrics['total_system_efficiency']:.2f}%")

                # Validation
                pv_val = PVModule(pv_params)
                validation = validate_simulation(result, pv_val)
                with st.expander("🔍 Validation Report"):
                    st.text(format_validation_report(validation))

            # Comparison table
            if len(results) > 1:
                st.markdown("### Comparison Table")
                comp = compare_algorithms(results)
                st.dataframe(comp)

        with tab_export:
            st.subheader("Export Results")
            for i, result in enumerate(results):
                st.markdown(f"**{result.algorithm_name}**")
                csv = result.data.to_csv(index=False)
                st.download_button(
                    f"📥 Download CSV ({result.algorithm_name})",
                    csv, f"mppt_{result.algorithm_name.lower()}_data.csv",
                    "text/csv"
                )

                metrics = compute_metrics(result)
                summary = format_metrics(metrics)
                st.download_button(
                    f"📥 Download Summary ({result.algorithm_name})",
                    summary, f"mppt_{result.algorithm_name.lower()}_summary.txt",
                    "text/plain"
                )


if __name__ == '__main__':
    main()
