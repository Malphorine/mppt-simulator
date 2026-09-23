import numpy as np
import pandas as pd
from typing import Dict, Any, List

def compute_metrics(result: Any) -> Dict[str, Any]:
    """
    Compute engineering metrics from a SimulationResult.
    
    Args:
        result: SimulationResult containing data (DataFrame), config, scenario_name, and algorithm_name.
        
    Returns:
        Dictionary of computed metrics.
    """
    df = result.data
    time = df['time'].values
    
    # 1. max_theoretical_power
    max_theoretical_power = df['mpp_power'].max()
    
    # 2. max_tracked_power
    max_tracked_power = df['pv_power'].max()
    
    # 3. avg_tracked_power
    avg_tracked_power = df['pv_power'].mean()
    
    # 4. avg_tracking_efficiency
    avg_tracking_efficiency = df['tracking_efficiency'].mean()
    
    # 5. steady_state_tracking_efficiency
    idx_80 = int(len(df) * 0.8)
    steady_state_df = df.iloc[idx_80:]
    if len(steady_state_df) > 0:
        steady_state_tracking_efficiency = steady_state_df['tracking_efficiency'].mean()
        # 6. steady_state_error
        steady_state_error = np.mean(np.abs(steady_state_df['pv_power'] - steady_state_df['mpp_power']))
        # 9. power_oscillation
        power_oscillation = steady_state_df['pv_power'].std()
    else:
        steady_state_tracking_efficiency = 0.0
        steady_state_error = 0.0
        power_oscillation = 0.0
        
    # 7. settling_time
    target_mpp_power = df['mpp_power'].iloc[0]
    lower_bound = target_mpp_power * 0.98
    
    # Find last index out of bounds to determine when it "stays there"
    out_of_bounds_idx = np.where(df['pv_power'] < lower_bound)[0]
    if len(out_of_bounds_idx) == 0:
        settling_time = time[0]
    elif out_of_bounds_idx[-1] == len(df) - 1:
        settling_time = np.nan # Never settles
    else:
        settling_time = time[out_of_bounds_idx[-1] + 1]
        
    # 8. rise_time
    target_10 = target_mpp_power * 0.10
    target_90 = target_mpp_power * 0.90
    
    idx_10 = np.where(df['pv_power'] >= target_10)[0]
    idx_90 = np.where(df['pv_power'] >= target_90)[0]
    
    t_10 = time[idx_10[0]] if len(idx_10) > 0 else np.nan
    t_90 = time[idx_90[0]] if len(idx_90) > 0 else np.nan
    rise_time = t_90 - t_10 if (not np.isnan(t_10) and not np.isnan(t_90) and t_90 >= t_10) else np.nan
    
    # 10. energy_harvested
    energy_harvested = np.trapz(df['pv_power'], time)
    
    # 11. energy_theoretical
    energy_theoretical = np.trapz(df['mpp_power'], time)
    
    # 12. converter_loss_total
    converter_loss_total = np.trapz(df['converter_loss'], time)
    
    # 13. mppt_loss_total
    mppt_loss_total = energy_theoretical - energy_harvested
    
    # 14. avg_converter_efficiency
    avg_converter_efficiency = df['converter_efficiency'].mean()
    
    # 15. total_system_efficiency
    if energy_theoretical > 0:
        total_system_efficiency = (energy_harvested * avg_converter_efficiency) / energy_theoretical * 100
    else:
        total_system_efficiency = 0.0
        
    # Final values
    final_voltage = df['pv_voltage'].iloc[-1]
    final_current = df['pv_current'].iloc[-1]
    final_power = df['pv_power'].iloc[-1]
    final_duty_cycle = df['duty_cycle'].iloc[-1]
    
    return {
        "max_theoretical_power": float(max_theoretical_power),
        "max_tracked_power": float(max_tracked_power),
        "avg_tracked_power": float(avg_tracked_power),
        "avg_tracking_efficiency": float(avg_tracking_efficiency),
        "steady_state_tracking_efficiency": float(steady_state_tracking_efficiency),
        "steady_state_error": float(steady_state_error),
        "settling_time": float(settling_time),
        "rise_time": float(rise_time),
        "power_oscillation": float(power_oscillation),
        "energy_harvested": float(energy_harvested),
        "energy_theoretical": float(energy_theoretical),
        "converter_loss_total": float(converter_loss_total),
        "mppt_loss_total": float(mppt_loss_total),
        "avg_converter_efficiency": float(avg_converter_efficiency),
        "total_system_efficiency": float(total_system_efficiency),
        "final_voltage": float(final_voltage),
        "final_current": float(final_current),
        "final_power": float(final_power),
        "final_duty_cycle": float(final_duty_cycle)
    }


def format_metrics(metrics: Dict[str, Any]) -> str:
    """
    Format metrics dictionary into a human-readable report string.
    """
    report = []
    report.append("="*40)
    report.append("MPPT SIMULATION METRICS REPORT")
    report.append("="*40)
    report.append("\n[Power Output]")
    report.append(f"Max Theoretical Power:     {metrics['max_theoretical_power']:.2f} W")
    report.append(f"Max Tracked Power:         {metrics['max_tracked_power']:.2f} W")
    report.append(f"Average Tracked Power:     {metrics['avg_tracked_power']:.2f} W")
    
    report.append("\n[Tracking Performance]")
    report.append(f"Avg Tracking Efficiency:   {metrics['avg_tracking_efficiency']:.2f} %")
    report.append(f"Steady-State Efficiency:   {metrics['steady_state_tracking_efficiency']:.2f} %")
    report.append(f"Steady-State Error:        {metrics['steady_state_error']:.2f} W")
    
    if np.isnan(metrics['settling_time']):
        report.append("Settling Time (2%):        Did not settle")
    else:
        report.append(f"Settling Time (2%):        {metrics['settling_time']:.4f} s")
        
    if np.isnan(metrics['rise_time']):
        report.append("Rise Time (10-90%):        N/A")
    else:
        report.append(f"Rise Time (10-90%):        {metrics['rise_time']:.4f} s")
        
    report.append(f"Power Oscillation (StdDev):{metrics['power_oscillation']:.2f} W")
    
    report.append("\n[Energy & Losses]")
    report.append(f"Energy Harvested:          {metrics['energy_harvested']:.2f} J")
    report.append(f"Theoretical Max Energy:    {metrics['energy_theoretical']:.2f} J")
    report.append(f"Total MPPT Loss:           {metrics['mppt_loss_total']:.2f} J")
    report.append(f"Total Converter Loss:      {metrics['converter_loss_total']:.2f} J")
    
    report.append("\n[System Efficiency]")
    report.append(f"Avg Converter Efficiency:  {metrics['avg_converter_efficiency'] * 100:.2f} %")
    report.append(f"Total System Efficiency:   {metrics['total_system_efficiency']:.2f} %")
    
    report.append("\n[Final State]")
    report.append(f"Voltage:                   {metrics['final_voltage']:.2f} V")
    report.append(f"Current:                   {metrics['final_current']:.2f} A")
    report.append(f"Power:                     {metrics['final_power']:.2f} W")
    report.append(f"Duty Cycle:                {metrics['final_duty_cycle']:.4f}")
    
    return "\n".join(report)


def compare_algorithms(results: List[Any]) -> pd.DataFrame:
    """
    Compare multiple algorithms across scenarios and return a DataFrame.
    """
    data = []
    for res in results:
        m = compute_metrics(res)
        data.append({
            'Scenario': getattr(res, 'scenario_name', 'Unknown'),
            'Algorithm': getattr(res, 'algorithm_name', 'Unknown'),
            'Energy Harvested (J)': m['energy_harvested'],
            'Tracking Eff (%)': m['avg_tracking_efficiency'],
            'Steady State Eff (%)': m['steady_state_tracking_efficiency'],
            'Settling Time (s)': m['settling_time'],
            'Rise Time (s)': m['rise_time'],
            'Oscillation (W)': m['power_oscillation'],
            'Total Sys Eff (%)': m['total_system_efficiency']
        })
    df = pd.DataFrame(data)
    return df
