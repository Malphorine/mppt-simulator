"""
Re-generate all experiment plots in Azerbaijani using updated visualization/plots.py
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from models.pv_model import PVModule, PVModuleParams, PVArray
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

RESULTS_DIR = r"C:\Users\ASUS\.gemini\antigravity\scratch\mppt_simulator\experiments\results"

pv = PVModule(PVModuleParams())

# 1. 00_pv_characteristics
dir0 = os.path.join(RESULTS_DIR, "00_pv_characteristics")
os.makedirs(dir0, exist_ok=True)
plot_iv_curve(pv, 1000, 25, save_path=os.path.join(dir0, "iv_curve_stc.png"))
plot_pv_curve(pv, 1000, 25, save_path=os.path.join(dir0, "pv_curve_stc.png"))
plot_iv_curves_irradiance(pv, save_path=os.path.join(dir0, "iv_curves_irradiance.png"))
plot_pv_curves_irradiance(pv, save_path=os.path.join(dir0, "pv_curves_irradiance.png"))
plot_pv_curves_temperature(pv, save_path=os.path.join(dir0, "pv_curves_temperature.png"))
print("Generated 00_pv_characteristics plots in Azerbaijani.")

# 2. 06_partial_shading
dir6 = os.path.join(RESULTS_DIR, "06_partial_shading")
os.makedirs(dir6, exist_ok=True)
pv_array = PVArray(n_modules=3, params=PVModuleParams())
pv_array.set_conditions([1000, 600, 300], [25, 25, 25])
plot_partial_shading_pv(pv_array, save_path=os.path.join(dir6, "partial_shading_pv.png"))
print("Generated 06_partial_shading plots in Azerbaijani.")

# Helper class to mock SimulationResult from saved CSV
class DummyConfig:
    def __init__(self, mppt_period=0.05, dt=0.001):
        self.mppt_period = mppt_period
        self.dt = dt

class DummyResult:
    def __init__(self, df, algo_name, scen_name):
        self.data = df
        self.algorithm_name = algo_name
        self.scenario_name = scen_name
        self.config = DummyConfig()

# Re-plot time domain results from existing CSVs
exp_dirs = [
    ("01_constant_stc", "exp1_po", "Perturb & Observe (P&O)", "Standart Test Şəraiti (STC)"),
    ("02_irradiance_drop", "exp2_po", "Perturb & Observe (P&O)", "Şüalanmanın Düşməsi (1000->700 W/m²)"),
    ("03_irradiance_rise", "exp3_po", "Perturb & Observe (P&O)", "Şüalanmanın Qalxması (700->1000 W/m²)"),
    ("04_temperature_rise", "exp4_po", "Perturb & Observe (P&O)", "Temperatur Artımı (25->45°C)"),
    ("05_combined", "exp5_po", "Perturb & Observe (P&O)", "Kombinə Dəyişən Hava Şəraiti"),
]

for dname, prefix, algo, scen in exp_dirs:
    csv_f = os.path.join(RESULTS_DIR, dname, f"{prefix}_data.csv")
    if os.path.exists(csv_f):
        df = pd.read_csv(csv_f)
        res = DummyResult(df, algo, scen)
        out_d = os.path.join(RESULTS_DIR, dname)
        plot_mppt_power(res, save_path=os.path.join(out_d, f"{prefix}_power.png"))
        plot_pv_voltage(res, save_path=os.path.join(out_d, f"{prefix}_voltage.png"))
        plot_pv_current(res, save_path=os.path.join(out_d, f"{prefix}_current.png"))
        plot_duty_cycle(res, save_path=os.path.join(out_d, f"{prefix}_duty_cycle.png"))
        plot_tracking_efficiency(res, save_path=os.path.join(out_d, f"{prefix}_efficiency.png"))
        plot_simulation_dashboard(res, save_path=os.path.join(out_d, f"{prefix}_dashboard.png"))
        plot_convergence(res, title_prefix=algo, save_path=os.path.join(out_d, f"{prefix}_convergence.png"))
        print(f"Generated {dname} plots in Azerbaijani.")

# 07_algorithm_comparison
dir7 = os.path.join(RESULTS_DIR, "07_algorithm_comparison")
csv_po = os.path.join(RESULTS_DIR, "07_algorithm_comparison", "exp7_po_data.csv")
csv_inc = os.path.join(RESULTS_DIR, "07_algorithm_comparison", "exp7_inc_data.csv")
if os.path.exists(csv_po) and os.path.exists(csv_inc):
    res_po = DummyResult(pd.read_csv(csv_po), "Perturb & Observe (P&O)", "Müqayisə")
    res_inc = DummyResult(pd.read_csv(csv_inc), "Incremental Conductance (INC)", "Müqayisə")
    plot_algorithm_comparison([res_po, res_inc], save_path=os.path.join(dir7, "algorithm_comparison.png"))
    print("Generated 07_algorithm_comparison plots in Azerbaijani.")

print("\nALL EXPERIMENT PLOTS RE-GENERATED IN AZERBAIJANI!")
