import matplotlib.pyplot as plt
import os

formula_dir = r'C:\Users\ASUS\.gemini\antigravity\scratch\mppt_simulator\experiments\results\formulas'
os.makedirs(formula_dir, exist_ok=True)

# Azerbaijani formulas
# In matplotlib mathtext, \mathrm{...} can format text subscripts nicely
az_formulas = {
    # 1. SDM with Ardıcıl (ard) and Paralel (par) resistances
    'f_sdm_az.png': r'$I = I_{ph} - I_0 \cdot \left[ \exp\left(\frac{V + I \cdot R_{ard}}{n \cdot N_s \cdot V_t}\right) - 1 \right] - \frac{V + I \cdot R_{ard}}{R_{par}}$',
    # 2. Thermal voltage
    'f_vt_az.png': r'$V_t = \frac{k_B \cdot T}{q} \approx 25.69\ \mathrm{mV} \quad (T = 25^\circ\mathrm{C})$',
    # 3. Rin -> Rgiris, Rload -> Ryuk
    'f_rin_az.png': r'$R_{\mathrm{gir},\mathrm{eff}} = R_{\mathrm{y\ddot{u}k}} \cdot \frac{(1 - D)^2}{\eta}$',
    # 4. Vout -> Vcix, Vin -> Vgir
    'f_boost_az.png': r'$V_{\mathrm{\c{c}\imath x}} = \frac{V_{\mathrm{gir}}}{1 - D} \cdot \eta$',
    # 5. INC
    'f_inc_az.png': r'$\frac{dP}{dV} = 0 \quad \Rightarrow \quad \frac{dI}{dV} = -\frac{I}{V}$',
    # 6. Iph
    'f_iph_az.png': r'$I_{ph}(G, T) = \frac{G}{G_0} \cdot \left[ I_{ph,0} + \alpha_{sc} \cdot (T - T_0) \right]$',
    # 7. I0
    'f_i0_az.png': r'$I_0(T) = I_{0,0} \cdot \left(\frac{T}{T_0}\right)^3 \cdot \exp\left[\frac{q}{k_B} \left(\frac{E_{g,0}}{T_0} - \frac{E_g(T)}{T}\right)\right]$',
    # 8. Eta with P_izlenen / P_teoretik
    'f_eta_az.png': r'$\eta_{\mathrm{MPPT}} = \frac{P_{\mathrm{izl\ddot{o}n\ddot{o}n}}}{P_{\mathrm{teoretik}}} \times 100\%$',
    # 9. Pout -> Pcix, Pin -> Pgir, Ploss -> Pitki
    'f_pout_az.png': r'$P_{\mathrm{\c{c}\imath x}} = V_{\mathrm{\c{c}\imath x}} \cdot I_{\mathrm{\c{c}\imath x}} \leq P_{\mathrm{gir}} - P_{\mathrm{itki}}$'
}

for fname, expr in az_formulas.items():
    fig = plt.figure(figsize=(9, 1.6), dpi=300)
    fig.patch.set_alpha(0.0)
    plt.text(0.5, 0.5, expr, fontsize=20, color='#1E3A8A', ha='center', va='center', weight='bold')
    plt.axis('off')
    out_file = os.path.join(formula_dir, fname)
    plt.savefig(out_file, bbox_inches='tight', transparent=True, dpi=300)
    plt.close()
    print(f'Rendered {fname}: {os.path.getsize(out_file)} bytes')

print('All Azerbaijani formulas successfully rendered!')
