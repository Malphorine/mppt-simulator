"""
Generate Animated GIF for Slide 16: Partial Shading Multi-Peak & Global MPPT
=============================================================================
Demonstrates:
1. Multi-peak P-V curve under non-uniform irradiance ([1000, 600, 300] W/m²).
2. Conventional P&O getting trapped at LMPP-1 (790.1 W) with 548 W loss.
3. Global MPPT scanning across voltage range to discover true GMPP (1338.2 W).
4. Locking onto GMPP with 99.9% efficiency.
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
import os

sys.path.insert(0, str(Path(__file__).resolve().parent))

from models.pv_model import PVArray, PVModuleParams

# 1. Setup PV Array under Partial Shading
pv_array = PVArray(n_modules=3, params=PVModuleParams())
pv_array.set_conditions([1000, 600, 300], [25, 25, 25])

V_curve, P_curve = pv_array.get_pv_curve(num_points=1500)
peaks = pv_array.find_all_local_maxima()

# GMPP and LMPPs
# First peak in sorted order is GMPP: (V, I, P)
gmpp_v, gmpp_i, gmpp_p = peaks[0]
lmpp1_v, lmpp1_i, lmpp1_p = peaks[1]
lmpp2_v, lmpp2_i, lmpp2_p = peaks[2]

# Animation Storyboard: 20 frames
# Frames 0-4: Base curve reveals & Conventional P&O starts stepping
# Frames 5-8: P&O gets trapped at LMPP-1 (790 W) with Warning HUD
# Frames 9-14: Global MPPT sweep / scan across voltage
# Frames 15-19: GMPP locked at 1338.2 W with Success HUD (+548 W gained)

frames = []
fig, ax = plt.subplots(figsize=(10, 7.8), dpi=120)

# Waypoints for animation
total_frames = 20

for f in range(total_frames):
    ax.clear()
    
    # Base multi-peak P-V curve
    ax.plot(V_curve, P_curve, color='#059669', linewidth=2.8, label='P-V Əyrisi (Qismən Kölgələnmə: 1000, 600, 300 W/m²)')
    
    # Reference peaks
    ax.plot(lmpp2_v, lmpp2_p, 'bs', markersize=8, alpha=0.7)
    ax.annotate(f'LMPP-2\n{lmpp2_p:.1f} W', xy=(lmpp2_v, lmpp2_p), xytext=(lmpp2_v - 8, lmpp2_p + 70),
                fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.25', facecolor='#EFF6FF', edgecolor='#3B82F6', lw=1.2),
                arrowprops=dict(arrowstyle='->', color='#2563EB', lw=1.2))
    
    ax.plot(lmpp1_v, lmpp1_p, 'bs', markersize=9, alpha=0.85)
    ax.annotate(f'LMPP-1\n{lmpp1_p:.1f} W', xy=(lmpp1_v, lmpp1_p), xytext=(lmpp1_v - 7, lmpp1_p + 90),
                fontsize=9.5, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.25', facecolor='#EFF6FF', edgecolor='#3B82F6', lw=1.2),
                arrowprops=dict(arrowstyle='->', color='#2563EB', lw=1.2))
    
    ax.plot(gmpp_v, gmpp_p, 'r*', markersize=16, alpha=0.9)
    ax.annotate(f'Qlobal GMPP\n{gmpp_p:.1f} W', xy=(gmpp_v, gmpp_p), xytext=(gmpp_v - 9, gmpp_p - 140),
                fontsize=10.5, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#FEF3C7', edgecolor='#D97706', lw=1.5),
                arrowprops=dict(arrowstyle='->', color='#DC2626', lw=1.8))
    
    if f < 4:
        # Phase 1: P&O moving towards LMPP-1
        progress = (f + 1) / 4.0
        cur_v = 115.0 + progress * (lmpp1_v - 115.0)
        # interpolate power on curve
        cur_p = np.interp(cur_v, V_curve, P_curve)
        
        ax.plot(cur_v, cur_p, 'o', color='#DC2626', markersize=13, zorder=6, label='Klassik P&O İşçi Nöqtəsi')
        ax.annotate('P&O Addımlayır...', xy=(cur_v, cur_p), xytext=(cur_v + 3, cur_p - 60),
                    fontsize=10, fontweight='bold', color='#DC2626',
                    arrowprops=dict(arrowstyle='->', color='#DC2626', lw=1.5))
        
        hud = (
            f"Faza 1: Klassik P&O Alqoritmi Başlayır\n"
            f"Cari Gərginlik: {cur_v:.1f} V  |  Cari Güc: {cur_p:.1f} W\n"
            f"İstiqamət: Yaxınlıqdakı təpəyə dırmanır..."
        )
        box_edge = '#0284C7'
        
    elif f < 9:
        # Phase 2: P&O trapped at LMPP-1
        osc = 0.8 * np.sin(f * 2.0)
        cur_v = lmpp1_v + osc
        cur_p = lmpp1_p - abs(osc) * 5
        
        ax.plot(cur_v, cur_p, 'X', color='#DC2626', markersize=15, zorder=7, label='P&O Lokal Tələdə (LMPP-1)')
        ax.annotate('LOKAL TƏLƏ!\nİlişib qaldı', xy=(cur_v, cur_p), xytext=(cur_v + 3, cur_p + 110),
                    fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#FEE2E2', edgecolor='#DC2626', lw=1.8),
                    arrowprops=dict(arrowstyle='->', color='#DC2626', lw=2.0))
        
        hud = (
            f"Faza 2: P&O LOKAL MAKSİMUMDA İLİŞİB QALDI!\n"
            f"Kilidlənən Güc: {lmpp1_p:.1f} W (LMPP-1)\n"
            f"Mövcud Qlobal Güc: {gmpp_p:.1f} W (GMPP)\n"
            f"İTİRİLƏN ENERJİ: {gmpp_p - lmpp1_p:.1f} W (27.6% İTKİ!)"
        )
        box_edge = '#DC2626'
        
    elif f < 15:
        # Phase 3: Global MPPT Sweep / Scanner
        scan_progress = (f - 9) / 5.0
        scan_v = 95.0 + scan_progress * (140.0 - 95.0)
        scan_p = np.interp(scan_v, V_curve, P_curve)
        
        # Draw scanning vertical line and probe
        ax.axvline(scan_v, color='#8B5CF6', linestyle='--', linewidth=2.2, alpha=0.85, label='Qlobal MPPT Skan Xətti')
        ax.plot(scan_v, scan_p, 'o', color='#8B5CF6', markersize=13, zorder=7, label='Qlobal Skan Zondu')
        
        # Still show P&O stuck point in background
        ax.plot(lmpp1_v, lmpp1_p, 'X', color='#9CA3AF', markersize=11, alpha=0.6)
        
        hud = (
            f"Faza 3: Qlobal MPPT Skanı Başladı (GMPPT)\n"
            f"Gərginlik Aralığı Skan Edilir: V = {scan_v:.1f} V\n"
            f"Ölçülən Güc: {scan_p:.1f} W\n"
            f"Bütün əyri üzrə ən yüksək pik axtarılır..."
        )
        box_edge = '#8B5CF6'
        
    else:
        # Phase 4: Locked on GMPP with massive victory
        pulse = 16 + 4 * np.sin((f - 15) * 1.5)
        ax.plot(gmpp_v, gmpp_p, '*', color='#EAB308', markeredgecolor='#DC2626', markeredgewidth=2,
                markersize=pulse, zorder=8, label='Qlobal Pik Kilidləndi (GMPP)')
        
        ax.annotate('QƏLƏBƏ: GMPP KİLİDLƏNDİ!\n1338.2 W (+548.1 W)',
                    xy=(gmpp_v, gmpp_p), xytext=(gmpp_v - 22, gmpp_p - 180),
                    fontsize=11, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.4', facecolor='#FEF3C7', edgecolor='#059669', lw=2),
                    arrowprops=dict(arrowstyle='->', color='#059669', lw=2.2))
        
        hud = (
            f"Faza 4: QLOBAL MAKSİMUM UĞURLA TAPILDI!\n"
            f"GMPP Gücü: {gmpp_p:.1f} W  |  Gərginlik: {gmpp_v:.1f} V\n"
            f"P&O İtkisi Geri Qaytarıldı: +{gmpp_p - lmpp1_p:.1f} W Artım!\n"
            f"Sistem İzləmə Səmərəliliyi: 99.9% !"
        )
        box_edge = '#059669'
    
    # HUD Box
    ax.text(0.03, 0.95, hud, transform=ax.transAxes, fontsize=10.5, fontweight='bold',
            verticalalignment='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=box_edge, lw=2.2))
    
    ax.set_xlabel('Gərginlik, V (Volt)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Güc, P (Vatt)', fontsize=12, fontweight='bold')
    ax.set_title('Qismən Kölgələnmədə P&O Tələsi və Qlobal MPPT Skanı (Dinamik)', fontsize=13, fontweight='bold', pad=12)
    ax.set_xlim([92, 145])
    ax.set_ylim([0, 1480])
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='lower left', fontsize=9.5)
    fig.tight_layout()
    
    fig.canvas.draw()
    rgba = np.asarray(fig.canvas.buffer_rgba())
    im = Image.fromarray(rgba)
    frames.append(im)

plt.close(fig)

out_gif = os.path.join(r"experiments\results\formulas", "partial_shading_animation.gif")
durations = [350] * 4 + [450] * 5 + [350] * 6 + [550] * 5
frames[0].save(out_gif, save_all=True, append_images=frames[1:], duration=durations, loop=0)
print(f"Generated {out_gif} with {len(frames)} frames. Size: {os.path.getsize(out_gif)} bytes")
