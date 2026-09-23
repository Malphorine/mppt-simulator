"""
Generate Animated GIF for Slide 13: P&O Climbing the P-V Curve
==============================================================
Demonstrates step-by-step operating point climbing up to MPP and steady-state 3-point oscillation.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import os

sys.path.insert(0, str(Path(__file__).resolve().parent))

from models.pv_model import PVModule, PVModuleParams

# Load real simulation trajectory data
df = pd.read_csv(r"experiments\results\01_constant_stc\exp1_po_data.csv")
# Sample at each MPPT update (every 50 ms)
mppt_data = df.iloc[::50].reset_index(drop=True)

# Generate static P-V curve for STC
pv = PVModule(PVModuleParams())
pv.set_conditions(1000, 25)
V_curve, I_curve = pv.get_iv_curve(num_points=1000)
P_curve = V_curve * I_curve

mpp_idx = np.argmax(P_curve)
v_mpp = V_curve[mpp_idx]
p_mpp = P_curve[mpp_idx]

# Select 20 key steps for the animation:
# 12 climbing steps + 8 oscillation steps
climb_steps = list(range(0, 12)) # from start up to MPP
osc_steps = list(range(12, 20))  # steady state oscillation
all_steps = climb_steps + osc_steps

frames = []
fig, ax = plt.subplots(figsize=(10, 6), dpi=120)

for step_num, idx in enumerate(all_steps):
    ax.clear()
    
    # 1. Base P-V curve
    ax.plot(V_curve, P_curve, color='#1E3A8A', linewidth=2.5, label='Canadian Solar 400W (STC: 1000 W/m², 25°C)')
    
    # 2. MPP line
    ax.axhline(p_mpp, color='#D97706', linestyle='--', linewidth=1.5, alpha=0.7, label=f'Teoretik MPP = {p_mpp:.2f} W')
    ax.axvline(v_mpp, color='#D97706', linestyle='--', linewidth=1.5, alpha=0.7)
    
    # 3. Trajectory up to current step
    past_v = mppt_data.loc[:idx, 'pv_voltage'].values
    past_p = mppt_data.loc[:idx, 'pv_power'].values
    
    if len(past_v) > 1:
        ax.plot(past_v, past_p, 'o--', color='#0284C7', linewidth=1.8, markersize=5, alpha=0.6, label='P&O Yaxınlaşma Trayektoriyası')
    
    # 4. Current operating point
    cur_v = mppt_data.loc[idx, 'pv_voltage']
    cur_p = mppt_data.loc[idx, 'pv_power']
    cur_d = mppt_data.loc[idx, 'duty_cycle']
    cur_t = mppt_data.loc[idx, 'time']
    
    is_at_mpp = (step_num >= 11)
    
    if is_at_mpp:
        # Pulsing star at MPP
        marker_color = '#DC2626' if step_num % 2 == 0 else '#EA580C'
        ax.plot(cur_v, cur_p, '*', color=marker_color, markersize=18, zorder=6, label='Cari İşçi Nöqtə (MPP-də)')
        status_text = "STATUS: MPP KİLİDLƏNDİ (±0.36W Dalğalanma)"
        status_color = '#059669'
    else:
        ax.plot(cur_v, cur_p, 'ro', markersize=12, zorder=6, label='Cari İşçi Nöqtə (Axtarışda)')
        status_text = "STATUS: TƏPƏYƏ DIRMANIR (P&O Addımlayır)"
        status_color = '#0284C7'
    
    # Arrow pointing to current point
    ax.annotate(f'k = {idx+1}\nV = {cur_v:.2f} V\nP = {cur_p:.1f} W\nD = {cur_d:.3f}',
                xy=(cur_v, cur_p), xytext=(cur_v - 9, cur_p - 45),
                fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.4', facecolor='#FEF3C7', edgecolor='#D97706', lw=1.5),
                arrowprops=dict(arrowstyle='->', color='#DC2626', lw=2.0))
    
    # Telemetry HUD Box in upper left
    hud_text = (
        f"Zaman: t = {cur_t:.2f} s  |  Addım: #{idx+1}\n"
        f"Gərginlik: {cur_v:.2f} V  |  Güc: {cur_p:.2f} W\n"
        f"Doluluq Əmsalı: D = {cur_d:.3f}\n"
        f"{status_text}"
    )
    ax.text(0.03, 0.95, hud_text, transform=ax.transAxes, fontsize=11, fontweight='bold',
            verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=status_color, lw=2))
    
    # Labels and layout
    ax.set_xlabel('Gərginlik, V (Volt)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Güc, P (Vatt)', fontsize=12, fontweight='bold')
    ax.set_title('P&O Alqoritminin P-V Əyrisi Üzrə Addım-Addım Yaxınlaşması (Canlı)', fontsize=13, fontweight='bold', pad=12)
    ax.set_xlim([15, 52])
    ax.set_ylim([150, 430])
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='lower left', fontsize=9.5)
    fig.tight_layout()
    
    # Canvas to PIL image
    fig.canvas.draw()
    rgba = np.asarray(fig.canvas.buffer_rgba())
    im = Image.fromarray(rgba)
    frames.append(im)

plt.close(fig)

# Save as animated GIF
out_gif = os.path.join(r"experiments\results\formulas", "po_climbing_animation.gif")
# 350ms per frame, last 5 frames paused longer
durations = [350] * 12 + [500] * 8
frames[0].save(out_gif, save_all=True, append_images=frames[1:], duration=durations, loop=0)
print(f"Generated {out_gif} with {len(frames)} frames. Size: {os.path.getsize(out_gif)} bytes")
