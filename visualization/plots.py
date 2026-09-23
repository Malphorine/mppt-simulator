"""
Engineering Visualization Module for MPPT Simulation (Azerbaijani Localized)
=============================================================================

Generates all 18+ engineering graphs using matplotlib with Azerbaijani labels,
units, grid, and legend.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from models.pv_model import PVModule, PVModuleParams, PVArray


def _mark_change_times(ax, result):
    """Add vertical lines at environmental change times."""
    data = result.data
    for col in ['irradiance', 'temperature']:
        vals = data[col].values
        diff = np.abs(np.diff(vals))
        if len(diff) == 0:
            continue
        threshold = np.median(diff) + 5 * max(np.std(diff), 0.1)
        change_idx = np.where(diff > threshold)[0]
        for idx in change_idx:
            t = data['time'].iloc[idx + 1]
            ax.axvline(x=t, color='red', linestyle='--', alpha=0.5,
                       linewidth=1.5, label='_nolegend_')


def _get_iv_at_conditions(pv: PVModule, G: float, T: float):
    """Helper: set PV conditions and return (V, I) arrays."""
    pv.set_conditions(G, T)
    return pv.get_iv_curve()


# ═══════════════════════════════════════════════════════════════════════════
# 1. I-V Curve (single condition)
# ═══════════════════════════════════════════════════════════════════════════
def plot_iv_curve(pv: PVModule, G=1000, T=25, save_path=None) -> plt.Figure:
    """Plot I-V characteristic curve with Isc and Voc markers."""
    fig, ax = plt.subplots(figsize=(10, 6))
    V, I = _get_iv_at_conditions(pv, G, T)
    ax.plot(V, I, 'b-', linewidth=2.5, label=f'STC: G = {G} W/m², T = {T}°C')

    # Mark Isc and Voc
    isc = I[0]
    voc_idx = np.argmin(np.abs(I))
    voc = V[voc_idx]
    ax.plot(0, isc, 'ro', markersize=8, zorder=5)
    ax.annotate(f'I_sc = {isc:.2f} A\n(Qısa Qapanma)', xy=(0, isc), xytext=(3, isc * 0.88),
                fontsize=11, arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#FEF3C7', edgecolor='#D97706'))
    ax.plot(voc, 0, 'go', markersize=8, zorder=5)
    ax.annotate(f'V_oc = {voc:.2f} V\n(Açıq Dövrə)', xy=(voc, 0), xytext=(voc * 0.70, isc * 0.20),
                fontsize=11, arrowprops=dict(arrowstyle='->', color='green', lw=1.5),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#ECFDF5', edgecolor='#059669'))

    ax.set_xlabel('Gərginlik, V (Volt)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cərəyan, I (Amper)', fontsize=12, fontweight='bold')
    ax.set_title('PV Modulunun Cərəyan-Gərginlik (I-V) Xarakteristikası', fontsize=14, fontweight='bold', pad=12)
    ax.set_xlim([0, voc * 1.05])
    ax.set_ylim([0, isc * 1.1])
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11, loc='upper right')
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# 2. P-V Curve (single condition)
# ═══════════════════════════════════════════════════════════════════════════
def plot_pv_curve(pv: PVModule, G=1000, T=25, save_path=None) -> plt.Figure:
    """Plot P-V curve with MPP annotation."""
    fig, ax = plt.subplots(figsize=(10, 6))
    V, I = _get_iv_at_conditions(pv, G, T)
    P = V * I
    ax.plot(V, P, 'g-', linewidth=2.5, label=f'STC: G = {G} W/m², T = {T}°C')

    # Find and mark MPP
    idx = np.argmax(P)
    vmp, imp, pmax = V[idx], I[idx], P[idx]
    ax.plot(vmp, pmax, 'r*', markersize=16, zorder=5, label='MPP (Maksimum Güc Nöqtəsi)')
    ax.annotate(f'MPP (Maksimum Güc Nöqtəsi)\nV_mp = {vmp:.2f} V\nI_mp = {imp:.2f} A\nP_max = {pmax:.1f} W',
                xy=(vmp, pmax), xytext=(vmp * 0.45, pmax * 0.70),
                fontsize=11, bbox=dict(boxstyle='round,pad=0.4', facecolor='#FEF3C7', edgecolor='#D97706'),
                arrowprops=dict(arrowstyle='->', color='red', lw=1.5))

    ax.set_xlabel('Gərginlik, V (Volt)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Güc, P (Vatt)', fontsize=12, fontweight='bold')
    ax.set_title('PV Modulunun Güc-Gərginlik (P-V) Xarakteristikası', fontsize=14, fontweight='bold', pad=12)
    ax.set_xlim([0, V[-1] * 1.05])
    ax.set_ylim([0, pmax * 1.15])
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11, loc='upper left')
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# 3. I-V Curves for multiple irradiance levels
# ═══════════════════════════════════════════════════════════════════════════
def plot_iv_curves_irradiance(pv: PVModule, G_values=None, T=25,
                              save_path=None) -> plt.Figure:
    """Multiple I-V curves overlaid at different irradiance levels."""
    if G_values is None:
        G_values = [200, 400, 600, 800, 1000]
    fig, ax = plt.subplots(figsize=(10, 6))
    for G in G_values:
        V, I = _get_iv_at_conditions(pv, G, T)
        ax.plot(V, I, linewidth=2.0, label=f'G = {G} W/m²')
    ax.set_xlabel('Gərginlik, V (Volt)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cərəyan, I (Amper)', fontsize=12, fontweight='bold')
    ax.set_title(f'Müxtəlif Şüalanma Səviyyələrində I-V Əyriləri (T = {T}°C)', fontsize=14, fontweight='bold', pad=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=10, loc='upper right')
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# 4. P-V Curves for multiple irradiance levels
# ═══════════════════════════════════════════════════════════════════════════
def plot_pv_curves_irradiance(pv: PVModule, G_values=None, T=25,
                              save_path=None) -> plt.Figure:
    """Multiple P-V curves with MPP markers at different irradiance levels."""
    if G_values is None:
        G_values = [200, 400, 600, 800, 1000]
    fig, ax = plt.subplots(figsize=(10, 6))
    for G in G_values:
        V, I = _get_iv_at_conditions(pv, G, T)
        P = V * I
        line, = ax.plot(V, P, linewidth=2.0, label=f'G = {G} W/m²')
        idx = np.argmax(P)
        ax.plot(V[idx], P[idx], '*', color=line.get_color(), markersize=12)
    ax.plot([], [], 'k*', markersize=12, label='MPP (Pik Nöqtəsi)')
    ax.set_xlabel('Gərginlik, V (Volt)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Güc, P (Vatt)', fontsize=12, fontweight='bold')
    ax.set_title(f'Müxtəlif Şüalanma Səviyyələrində P-V Əyriləri (T = {T}°C)', fontsize=14, fontweight='bold', pad=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=10, loc='upper left')
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# 5. P-V Curves for multiple temperatures
# ═══════════════════════════════════════════════════════════════════════════
def plot_pv_curves_temperature(pv: PVModule, T_values=None, G=1000,
                               save_path=None) -> plt.Figure:
    """Multiple P-V curves with MPP markers at different temperatures."""
    if T_values is None:
        T_values = [15, 25, 35, 45, 55]
    fig, ax = plt.subplots(figsize=(10, 6))
    for T in T_values:
        V, I = _get_iv_at_conditions(pv, G, T)
        P = V * I
        line, = ax.plot(V, P, linewidth=2.0, label=f'T = {T}°C')
        idx = np.argmax(P)
        ax.plot(V[idx], P[idx], '*', color=line.get_color(), markersize=12)
    ax.plot([], [], 'k*', markersize=12, label='MPP (Pik Nöqtəsi)')
    ax.set_xlabel('Gərginlik, V (Volt)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Güc, P (Vatt)', fontsize=12, fontweight='bold')
    ax.set_title(f'Müxtəlif Temperatur Rejimlərində P-V Əyriləri (G = {G} W/m²)', fontsize=14, fontweight='bold', pad=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=10, loc='upper right')
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# 6–11. Time-domain plots
# ═══════════════════════════════════════════════════════════════════════════
def plot_mppt_power(result, save_path=None) -> plt.Figure:
    """PV power vs time with theoretical MPP reference."""
    fig, ax = plt.subplots(figsize=(10, 6))
    d = result.data
    ax.plot(d['time'], d['pv_power'], 'b-', linewidth=1.6, label='Faktiki İzlənən Güc')
    ax.plot(d['time'], d['mpp_power'], 'r--', linewidth=1.6, label='Teoretik Maksimum (MPP)')
    _mark_change_times(ax, result)
    ax.set_xlabel('Zaman (s)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Güc, P (Vatt)', fontsize=12, fontweight='bold')
    ax.set_title(f'MPPT Güc İzlənməsi — {result.algorithm_name}', fontsize=14, fontweight='bold', pad=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11, loc='lower right')
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
    return fig


def plot_pv_voltage(result, save_path=None) -> plt.Figure:
    """PV voltage vs time with theoretical MPP voltage reference."""
    fig, ax = plt.subplots(figsize=(10, 6))
    d = result.data
    ax.plot(d['time'], d['pv_voltage'], 'b-', linewidth=1.6, label='PV Gərginliyi')
    ax.plot(d['time'], d['mpp_voltage'], 'r--', linewidth=1.6, label='V_mp (Teoretik)')
    _mark_change_times(ax, result)
    ax.set_xlabel('Zaman (s)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Gərginlik, V (Volt)', fontsize=12, fontweight='bold')
    ax.set_title('PV Gərginliyinin Zamana Görə Dəyişməsi', fontsize=14, fontweight='bold', pad=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11)
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
    return fig


def plot_pv_current(result, save_path=None) -> plt.Figure:
    """PV current vs time with theoretical MPP current reference."""
    fig, ax = plt.subplots(figsize=(10, 6))
    d = result.data
    ax.plot(d['time'], d['pv_current'], 'b-', linewidth=1.6, label='PV Cərəyanı')
    ax.plot(d['time'], d['mpp_current'], 'r--', linewidth=1.6, label='I_mp (Teoretik)')
    _mark_change_times(ax, result)
    ax.set_xlabel('Zaman (s)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cərəyan, I (Amper)', fontsize=12, fontweight='bold')
    ax.set_title('PV Cərəyanının Zamana Görə Dəyişməsi', fontsize=14, fontweight='bold', pad=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11)
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
    return fig


def plot_duty_cycle(result, save_path=None) -> plt.Figure:
    """Duty cycle vs time."""
    fig, ax = plt.subplots(figsize=(10, 6))
    d = result.data
    ax.plot(d['time'], d['duty_cycle'], 'purple', linewidth=1.6, label='Doluluq Əmsalı (D)')
    _mark_change_times(ax, result)
    ax.set_xlabel('Zaman (s)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Doluluq Əmsalı, D', fontsize=12, fontweight='bold')
    ax.set_title('Çeviricinin Doluluq Əmsalının Dəyişməsi', fontsize=14, fontweight='bold', pad=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11)
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
    return fig


def plot_irradiance(result, save_path=None) -> plt.Figure:
    """Irradiance vs time."""
    fig, ax = plt.subplots(figsize=(10, 6))
    d = result.data
    ax.plot(d['time'], d['irradiance'], 'orange', linewidth=2, label='Günəş Şüalanması')
    ax.set_xlabel('Zaman (s)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Şüalanma (W/m²)', fontsize=12, fontweight='bold')
    ax.set_title('Günəş Radiasiyasının Zamana Görə Dəyişməsi', fontsize=14, fontweight='bold', pad=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11)
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
    return fig


def plot_temperature(result, save_path=None) -> plt.Figure:
    """Temperature vs time."""
    fig, ax = plt.subplots(figsize=(10, 6))
    d = result.data
    ax.plot(d['time'], d['temperature'], 'r-', linewidth=2, label='Modul Temperaturu')
    ax.set_xlabel('Zaman (s)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Temperatur (°C)', fontsize=12, fontweight='bold')
    ax.set_title('Modul Temperaturunun Zamana Görə Dəyişməsi', fontsize=14, fontweight='bold', pad=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11)
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# 12–14. Comparison & efficiency plots
# ═══════════════════════════════════════════════════════════════════════════
def plot_mpp_comparison(result, save_path=None) -> plt.Figure:
    """Theoretical MPP power vs actual operating power."""
    fig, ax = plt.subplots(figsize=(10, 6))
    d = result.data
    ax.plot(d['time'], d['mpp_power'], 'r--', linewidth=1.6, label='Teoretik MPP Gücü')
    ax.plot(d['time'], d['pv_power'], 'b-', linewidth=1.6, alpha=0.85,
            label='Faktiki İşçi Güc')
    ax.fill_between(d['time'], d['pv_power'], d['mpp_power'],
                    alpha=0.18, color='red', label='İzləmə İtkisi')
    _mark_change_times(ax, result)
    ax.set_xlabel('Zaman (s)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Güc (Vatt)', fontsize=12, fontweight='bold')
    ax.set_title('Teoretik MPP və Faktiki İşçi Nöqtənin Müqayisəsi', fontsize=14, fontweight='bold', pad=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11)
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
    return fig


def plot_tracking_error(result, save_path=None) -> plt.Figure:
    """|P_actual - P_mpp| vs time."""
    fig, ax = plt.subplots(figsize=(10, 6))
    d = result.data
    ax.plot(d['time'], d['tracking_error'], 'r-', linewidth=1.6, label='İzləmə Xətası')
    _mark_change_times(ax, result)
    ax.set_xlabel('Zaman (s)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Güc Xətası (Vatt)', fontsize=12, fontweight='bold')
    ax.set_title('MPPT İzləmə Xətasının Zamana Görə Dəyişməsi', fontsize=14, fontweight='bold', pad=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11)
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
    return fig


def plot_tracking_efficiency(result, save_path=None) -> plt.Figure:
    """Tracking efficiency (%) vs time."""
    fig, ax = plt.subplots(figsize=(10, 6))
    d = result.data
    ax.plot(d['time'], d['tracking_efficiency'], 'g-', linewidth=1.6,
            label='İzləmə Səmərəliliyi')
    ax.axhline(100, color='black', linestyle=':', linewidth=1.2, label='100% İdeal Səviyyə')
    _mark_change_times(ax, result)
    ax.set_xlabel('Zaman (s)', fontsize=12, fontweight='bold')
    ax.set_ylabel('İzləmə Səmərəliliyi (%)', fontsize=12, fontweight='bold')
    ax.set_title('MPPT İzləmə Səmərəliliyi Dinamikası', fontsize=14, fontweight='bold', pad=12)
    y_min = max(0, d['tracking_efficiency'].min() - 10)
    ax.set_ylim([y_min, 105])
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11)
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# 15–16. Convergence & algorithm comparison
# ═══════════════════════════════════════════════════════════════════════════
def plot_convergence(result, title_prefix='', save_path=None) -> plt.Figure:
    """Convergence plot: power vs MPPT step index."""
    fig, ax = plt.subplots(figsize=(10, 6))
    d = result.data

    # Subsample at MPPT period intervals
    mppt_period = result.config.mppt_period
    dt = result.config.dt
    step_every = max(1, int(mppt_period / dt))
    mppt_data = d.iloc[::step_every].reset_index(drop=True)

    steps = np.arange(len(mppt_data))
    ax.plot(steps, mppt_data['pv_power'], 'b-', linewidth=1.6, label='Faktiki Güc')
    ax.plot(steps, mppt_data['mpp_power'], 'r--', linewidth=1.6, label='Teoretik MPP')

    ax.set_xlabel('MPPT Addım Nömrəsi', fontsize=12, fontweight='bold')
    ax.set_ylabel('Güc (Vatt)', fontsize=12, fontweight='bold')
    title = f'{title_prefix} Yaxınlaşma Qrafiki' if title_prefix else f'{result.algorithm_name} Yaxınlaşma Trayektoriyası'
    ax.set_title(title, fontsize=14, fontweight='bold', pad=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11)
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
    return fig


def plot_algorithm_comparison(results: list, save_path=None) -> plt.Figure:
    """Compare P&O vs INC: subplots showing power vs time for each."""
    n = len(results)
    fig, axes = plt.subplots(n, 1, figsize=(10, 4 * n), sharex=True)
    if n == 1:
        axes = [axes]

    for ax, res in zip(axes, results):
        d = res.data
        ax.plot(d['time'], d['pv_power'], 'b-', linewidth=1.6, label='Faktiki İzlənən Güc')
        ax.plot(d['time'], d['mpp_power'], 'r--', linewidth=1.6, label='Teoretik MPP')
        _mark_change_times(ax, res)
        ax.set_ylabel('Güc (Vatt)', fontsize=12, fontweight='bold')
        ax.set_title(f'Alqoritm: {res.algorithm_name}', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(fontsize=10)

    axes[-1].set_xlabel('Zaman (s)', fontsize=12, fontweight='bold')
    fig.suptitle('MPPT Alqoritmlərinin Dinamik İzləmə Müqayisəsi', fontsize=15, fontweight='bold', y=1.01)
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# 17. Partial Shading P-V curve
# ═══════════════════════════════════════════════════════════════════════════
def plot_partial_shading_pv(array: PVArray, save_path=None) -> plt.Figure:
    """P-V curve with multiple peaks. Mark GMPP and LMPP points."""
    fig, ax = plt.subplots(figsize=(10, 6))

    V, P = array.get_pv_curve(num_points=2000)
    ax.plot(V, P, 'g-', linewidth=2.5, label='P-V Əyrisi (Qismən Kölgələnmə Şəraiti)')

    # Find all local maxima: returns list of (V, I, P) tuples
    peaks = array.find_all_local_maxima()

    gmpp_labeled = False
    lmpp_labeled = False
    if peaks:
        # First peak is GMPP (sorted by descending power)
        for i, (vp, ip, pp) in enumerate(peaks):
            if i == 0:
                ax.plot(vp, pp, 'r*', markersize=18, zorder=5,
                        label='Qlobal Maksimum (GMPP)' if not gmpp_labeled else '_nolegend_')
                gmpp_labeled = True
                ax.annotate(f'Qlobal Pik (GMPP)\nV = {vp:.1f} V\nP = {pp:.1f} W',
                            xy=(vp, pp), xytext=(vp + 5, pp * 0.95),
                            fontsize=10, fontweight='bold',
                            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FEF3C7', edgecolor='#D97706'),
                            arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
            else:
                ax.plot(vp, pp, 'bs', markersize=10, zorder=5,
                        label='Lokal Maksimum (LMPP)' if not lmpp_labeled else '_nolegend_')
                lmpp_labeled = True
                ax.annotate(f'Lokal Pik (LMPP-{i})\nV = {vp:.1f} V\nP = {pp:.1f} W',
                            xy=(vp, pp), xytext=(vp + 5, pp + 15),
                            fontsize=9,
                            bbox=dict(boxstyle='round,pad=0.3', facecolor='#EFF6FF', edgecolor='#3B82F6'),
                            arrowprops=dict(arrowstyle='->', color='blue', lw=1.2))

    ax.set_xlabel('Gərginlik, V (Volt)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Güc, P (Vatt)', fontsize=12, fontweight='bold')
    ax.set_title('Qismən Kölgələnmədə P-V Əyrisi — Çoxzirvəli Xarakteristika', fontsize=14, fontweight='bold', pad=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11, loc='upper left')
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
    return fig


# ═══════════════════════════════════════════════════════════════════════════
# 18. Dashboard
# ═══════════════════════════════════════════════════════════════════════════
def plot_simulation_dashboard(result, save_path=None) -> plt.Figure:
    """3×2 grid dashboard: power, voltage, current, duty cycle, efficiency, irradiance."""
    fig = plt.figure(figsize=(14, 10))
    gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.3)
    d = result.data
    t = d['time']

    panels = [
        (gs[0, 0], 'pv_power', 'mpp_power', 'Güc (Vatt)', 'Güc İzlənməsi', 'b', 'r', 'Faktiki Güc', 'Teoretik MPP'),
        (gs[0, 1], 'pv_voltage', 'mpp_voltage', 'Gərginlik (Volt)', 'Gərginlik Dinamikası', 'b', 'r', 'PV Gərginliyi', 'V_mp (Teoretik)'),
        (gs[1, 0], 'pv_current', 'mpp_current', 'Cərəyan (Amper)', 'Cərəyan Dinamikası', 'b', 'r', 'PV Cərəyanı', 'I_mp (Teoretik)'),
        (gs[1, 1], 'duty_cycle', None, 'Doluluq Əmsalı, D', 'Doluluq Əmsalı Dinamikası', 'purple', None, 'D Əmsalı', None),
        (gs[2, 0], 'tracking_efficiency', None, 'Səmərəlilik (%)', 'İzləmə Səmərəliliyi', 'g', None, 'Səmərəlilik (%)', None),
        (gs[2, 1], 'irradiance', None, 'Şüalanma (W/m²)', 'Günəş Şüalanması Səviyyəsi', 'orange', None, 'G (W/m²)', None),
    ]

    for spec, col1, col2, ylabel, title, c1, c2, l1, l2 in panels:
        ax = fig.add_subplot(spec)
        ax.plot(t, d[col1], color=c1, linewidth=1.4, label=l1)
        if col2:
            ax.plot(t, d[col2], '--', color=c2, linewidth=1.4, label=l2)
            ax.legend(fontsize=9, loc='lower right')
        _mark_change_times(ax, result)
        ax.set_ylabel(ylabel, fontsize=10, fontweight='bold')
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_xlabel('Zaman (s)', fontsize=9, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.tick_params(labelsize=8)

    fig.suptitle(f'MPPT Simulyasiya İdarəetmə Paneli — {result.algorithm_name}\n'
                 f'Ssenari: {result.scenario_name}', fontsize=14, fontweight='bold', y=0.98)
    fig.subplots_adjust(top=0.90)
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
    return fig
