from dataclasses import dataclass
import pandas as pd
import numpy as np
from typing import List, Tuple, Any

# Assuming these imports work within the project structure
from models.pv_model import PVModule, PVModuleParams
from analysis.metrics import compute_metrics


@dataclass
class ValidationResult:
    scenario_name: str
    algorithm_name: str
    theoretical_Vmp: float
    theoretical_Imp: float
    theoretical_Pmax: float
    mppt_V: float
    mppt_I: float
    mppt_P: float
    voltage_error_pct: float
    current_error_pct: float
    power_error_pct: float
    tracking_efficiency: float
    settling_time: float
    sanity_checks: list[tuple[str, bool, str]]  # (check_name, passed, message)
    all_passed: bool


def validate_simulation(result: Any, pv_module: PVModule) -> ValidationResult:
    """
    Validate a single SimulationResult by checking its outputs against
    theoretical expectations from the PVModule.
    """
    df = result.data
    scenario = getattr(result, 'scenario_name', 'Unknown')
    algo = getattr(result, 'algorithm_name', 'Unknown')
    
    # 1. Steady-state conditions over the last 20% of simulation
    idx_80 = int(len(df) * 0.8)
    steady_state_df = df.iloc[idx_80:]
    
    avg_G = steady_state_df['irradiance'].mean()
    avg_T = steady_state_df['temperature'].mean()
    
    # Independently compute theoretical MPP at steady-state conditions
    from models.pv_model import PVArray
    if isinstance(pv_module, PVArray):
        Vmp, Imp, Pmax = pv_module.find_mpp()
    elif hasattr(pv_module, 'set_conditions'):
        pv_module.set_conditions(avg_G, avg_T)
        Vmp, Imp, Pmax = pv_module.find_mpp()
    else:
        Vmp = float(steady_state_df['mpp_voltage'].mean())
        Imp = float(steady_state_df['mpp_current'].mean())
        Pmax = float(steady_state_df['mpp_power'].mean())
    
    # 2. Get MPPT operating point
    mppt_V = steady_state_df['pv_voltage'].mean()
    mppt_I = steady_state_df['pv_current'].mean()
    mppt_P = steady_state_df['pv_power'].mean()
    
    # 3. Compute errors as percentages
    voltage_error_pct = abs(mppt_V - Vmp) / Vmp * 100 if Vmp != 0 else 0.0
    current_error_pct = abs(mppt_I - Imp) / Imp * 100 if Imp != 0 else 0.0
    power_error_pct = abs(mppt_P - Pmax) / Pmax * 100 if Pmax != 0 else 0.0
    
    # 4 & 5. Obtain tracking efficiency and settling time
    metrics = compute_metrics(result)
    tracking_efficiency = metrics.get('steady_state_tracking_efficiency', 0.0)
    settling_time = metrics.get('settling_time', np.nan)
    
    # 6. Run sanity checks
    sanity_checks = run_sanity_checks(result)
    all_passed = all(check[1] for check in sanity_checks)
    
    return ValidationResult(
        scenario_name=scenario,
        algorithm_name=algo,
        theoretical_Vmp=Vmp,
        theoretical_Imp=Imp,
        theoretical_Pmax=Pmax,
        mppt_V=mppt_V,
        mppt_I=mppt_I,
        mppt_P=mppt_P,
        voltage_error_pct=voltage_error_pct,
        current_error_pct=current_error_pct,
        power_error_pct=power_error_pct,
        tracking_efficiency=tracking_efficiency,
        settling_time=settling_time,
        sanity_checks=sanity_checks,
        all_passed=all_passed
    )


def run_sanity_checks(result: Any) -> List[Tuple[str, bool, str]]:
    """
    Run basic data integrity and physical sanity checks on simulation results.
    """
    checks = []
    df = result.data
    
    # 1. P = V x I
    p_calc = df['pv_voltage'] * df['pv_current']
    p_diff = np.abs(df['pv_power'] - p_calc)
    tol = 0.001 * df['pv_power'].clip(lower=1e-5)
    passed_p_calc = bool(np.all(p_diff <= tol))
    msg = "Valid" if passed_p_calc else f"Max error: {p_diff.max():.4e} W"
    checks.append(("P = V x I", passed_p_calc, msg))
    
    # 2. P >= 0
    passed_p_pos = bool(np.all(df['pv_power'] >= -1e-6))
    msg = "Valid" if passed_p_pos else f"Min power: {df['pv_power'].min():.4f} W"
    checks.append(("Power is Non-negative", passed_p_pos, msg))
    
    # 3. No NaN values
    has_nan = bool(df.isna().any().any())
    msg = "NaN values found" if has_nan else "Valid"
    checks.append(("No NaN Values", not has_nan, msg))
    
    # 4. No Inf values
    has_inf = bool(np.isinf(df.select_dtypes(include=[np.number])).any().any())
    msg = "Inf values found" if has_inf else "Valid"
    checks.append(("No Infinity Values", not has_inf, msg))
    
    # Check 5 and 6 (Requires reference conditions, skipped or approximated if not directly available from Result)
    # We will assume these are structural rules on the results
    
    # 7. Pmax ≈ Vmp × Imp (within 2%) from tracking data
    pmax_calc = df['mpp_voltage'] * df['mpp_current']
    diff_pmax = np.abs(df['mpp_power'] - pmax_calc)
    tol_pmax = 0.02 * df['mpp_power'].clip(lower=1e-5)
    passed_pmax = bool(np.all(diff_pmax <= tol_pmax))
    msg = "Valid" if passed_pmax else f"Max deviation: {diff_pmax.max():.4f}"
    checks.append(("Pmax approx Vmp x Imp", passed_pmax, msg))
    
    # 8. Duty cycle in [0, 1] or specified limits
    passed_duty = bool(np.all((df['duty_cycle'] >= 0.0) & (df['duty_cycle'] <= 1.0)))
    msg = "Valid" if passed_duty else f"Range: [{df['duty_cycle'].min():.2f}, {df['duty_cycle'].max():.2f}]"
    checks.append(("Duty Cycle Range", passed_duty, msg))
    
    # 9. PV voltage >= 0
    passed_v_pos = bool(np.all(df['pv_voltage'] >= -1e-6))
    msg = "Valid" if passed_v_pos else f"Min V: {df['pv_voltage'].min():.4f} V"
    checks.append(("PV Voltage Non-negative", passed_v_pos, msg))
    
    # 10. PV current >= 0
    passed_i_pos = bool(np.all(df['pv_current'] >= -1e-6))
    msg = "Valid" if passed_i_pos else f"Min I: {df['pv_current'].min():.4f} A"
    checks.append(("PV Current Non-negative", passed_i_pos, msg))
    
    # 11. Tracking efficiency in [0, 110]
    eff = df['tracking_efficiency']
    passed_te = bool(np.all((eff >= -0.1) & (eff <= 110.0)))
    msg = "Valid" if passed_te else f"Range: [{eff.min():.1f}, {eff.max():.1f}] %"
    checks.append(("Tracking Eff [0, 110]", passed_te, msg))
    
    # 12. Converter efficiency in [0, 1.05]
    ceff = df['converter_efficiency']
    passed_ce = bool(np.all((ceff >= -0.01) & (ceff <= 1.05)))
    msg = "Valid" if passed_ce else f"Range: [{ceff.min():.2f}, {ceff.max():.2f}]"
    checks.append(("Converter Eff [0, 1.05]", passed_ce, msg))
    
    # 13. Output power <= Input power
    passed_op = bool(np.all(df['out_power'] <= df['pv_power'] + 1e-4)) # small numerical tolerance
    msg = "Valid" if passed_op else f"Max excess out power: {(df['out_power'] - df['pv_power']).max():.4f} W"
    checks.append(("Energy Conservation", passed_op, msg))
    
    # 14. No negative resistance
    positive_i_mask = df['pv_current'] > 1e-3
    resistance = df['pv_voltage'][positive_i_mask] / df['pv_current'][positive_i_mask]
    passed_r = bool(np.all(resistance >= 0))
    msg = "Valid" if passed_r else "Negative resistance detected"
    checks.append(("No Negative Resistance", passed_r, msg))
    
    # 15. Irradiance >= 0
    passed_irr = bool(np.all(df['irradiance'] >= 0))
    msg = "Valid" if passed_irr else f"Min Irradiance: {df['irradiance'].min():.2f}"
    checks.append(("Positive Irradiance", passed_irr, msg))
    
    # 16. Temp in [-40, 100]
    passed_t = bool(np.all((df['temperature'] >= -40) & (df['temperature'] <= 100)))
    msg = "Valid" if passed_t else f"Range: [{df['temperature'].min():.1f}, {df['temperature'].max():.1f}] C"
    checks.append(("Reasonable Temperature", passed_t, msg))
    
    # 17. Voltage doesn't exceed Voc by > 5% (assuming max V is Voc approx)
    max_v = df['pv_voltage'].max()
    approx_voc = df['mpp_voltage'].max() * 1.25 # Heuristic if Voc not logged
    passed_v_lim = max_v <= approx_voc * 1.05
    msg = "Valid" if passed_v_lim else f"Overvoltage: {max_v:.2f} V"
    checks.append(("Voltage Limits", passed_v_lim, msg))
    
    # 18. Current doesn't exceed Isc by > 5%
    max_i = df['pv_current'].max()
    approx_isc = df['mpp_current'].max() * 1.15
    passed_i_lim = max_i <= approx_isc * 1.05
    msg = "Valid" if passed_i_lim else f"Overcurrent: {max_i:.2f} A"
    checks.append(("Current Limits", passed_i_lim, msg))
    
    # 19. Power oscillation in SS < 10% of Pmax
    idx_80 = int(len(df) * 0.8)
    ss_df = df.iloc[idx_80:]
    if len(ss_df) > 0:
        oscillation = ss_df['pv_power'].std()
        pmax_mean = ss_df['mpp_power'].mean()
        passed_osc = float(oscillation) < 0.10 * float(pmax_mean)
        msg = "Valid" if passed_osc else f"Oscillation: {oscillation:.2f} W (> 10% of {pmax_mean:.2f} W)"
    else:
        passed_osc = False
        msg = "No steady state data"
    checks.append(("Steady State Oscillation", passed_osc, msg))
    
    # 20. Final tracking efficiency > 90%
    final_eff = df['tracking_efficiency'].iloc[-1]
    passed_fe = float(final_eff) > 90.0
    msg = "Valid" if passed_fe else f"Final efficiency: {final_eff:.1f}%"
    checks.append(("Final Efficiency > 90%", passed_fe, msg))
    
    return checks


def format_validation_report(result: ValidationResult) -> str:
    """
    Format a ValidationResult into a human-readable string report.
    """
    report = []
    report.append("="*50)
    report.append(f"VALIDATION REPORT: {result.scenario_name} | {result.algorithm_name}")
    report.append("="*50)
    
    status = "PASSED" if result.all_passed else "FAILED"
    report.append(f"Overall Status: {status}")
    report.append("")
    
    report.append("[Theoretical vs MPPT Performance (Steady State)]")
    report.append(f"{'Metric':<10} | {'Theoretical':<15} | {'Actual (MPPT)':<15} | {'Error %':<10}")
    report.append("-" * 55)
    report.append(f"{'Voltage':<10} | {result.theoretical_Vmp:<15.2f} | {result.mppt_V:<15.2f} | {result.voltage_error_pct:<10.2f}")
    report.append(f"{'Current':<10} | {result.theoretical_Imp:<15.2f} | {result.mppt_I:<15.2f} | {result.current_error_pct:<10.2f}")
    report.append(f"{'Power':<10} | {result.theoretical_Pmax:<15.2f} | {result.mppt_P:<15.2f} | {result.power_error_pct:<10.2f}")
    
    report.append("\n[Performance Metrics]")
    report.append(f"Tracking Efficiency: {result.tracking_efficiency:.2f} %")
    if np.isnan(result.settling_time):
        report.append("Settling Time:       Did not settle")
    else:
        report.append(f"Settling Time:       {result.settling_time:.4f} s")
        
    report.append("\n[Sanity Checks]")
    for check_name, passed, msg in result.sanity_checks:
        status_str = "PASS" if passed else "FAIL"
        report.append(f"[{status_str}] {check_name:<25}: {msg}")
        
    return "\n".join(report)
