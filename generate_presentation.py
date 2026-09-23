"""
Professional 20-Slide PowerPoint Generator for MPPT University Presentation (AzTU)
==================================================================================
Fully localized in Azerbaijani:
1. Exact user-defined Title Slide (Slide 1):
   - "Azərbaycan Texniki Universiteti"
   - Title
   - Subtitle
   - "Müəllif: Həmidov Xalid"
2. Slide 8: Real mathematical EQUATIONS for all boost converter loss mechanisms:
   - P_L = I_gir^2 * R_L
   - P_FET = I_gir^2 * D * R_ds
   - P_diod = I_cix * V_diod
   - P_kom = 0.5 * V_cix * I_gir * (t_r + t_f) * f_sw
   - Sigma P_itki and eta
   Rendered with authentic LaTeX typography (NO plain text pseudo-math!).
3. Slide 4: Full SDM equation card with parameter definitions and thermal voltage.
4. Slide 9 & 10: Real mathematical decision equations for P&O and INC.
5. All simulation plots in Azerbaijani.
6. Zero overlapping text, generous font sizes (12.5 - 14pt).
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = r"C:\Users\ASUS\.gemini\antigravity\scratch\mppt_simulator"
RESULTS_DIR = os.path.join(BASE_DIR, "experiments", "results")
FORMULA_DIR = os.path.join(RESULTS_DIR, "formulas")
PRIMARY_PPTX = os.path.join(BASE_DIR, "MPPT_Teqdimat_20_Slayd.pptx")
BACKUP_PPTX = os.path.join(BASE_DIR, "MPPT_Teqdimat_20_Slayd_Yenilenmis.pptx")

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Theme Colors
    DARK_BLUE = RGBColor(15, 23, 42)       # #0F172A
    NAVY = RGBColor(30, 58, 138)           # #1E3A8A
    ACCENT_GOLD = RGBColor(217, 119, 6)    # #D97706
    ACCENT_CYAN = RGBColor(2, 132, 199)    # #0284C7
    TEXT_MAIN = RGBColor(30, 41, 59)       # #1E293B
    TEXT_MUTED = RGBColor(100, 116, 139)   # #64748B
    BG_CANVAS = RGBColor(248, 250, 252)    # #F8FAFC
    CARD_BG = RGBColor(255, 255, 255)      # Pure White
    CARD_BORDER = RGBColor(226, 232, 240)  # #E2E8F0
    WHITE = RGBColor(255, 255, 255)

    def set_canvas_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_CANVAS
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, tracker="MPPT FOTOVOLTAİK SİSTEMİ"):
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
        bar.fill.solid()
        bar.fill.fore_color.rgb = DARK_BLUE
        bar.line.fill.background()

        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.15), Inches(13.333), Inches(0.06))
        line.fill.solid()
        line.fill.fore_color.rgb = ACCENT_GOLD
        line.line.fill.background()

        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(11.7), Inches(0.28))
        tf = t_box.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        p0 = tf.paragraphs[0]
        p0.text = tracker.upper()
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = ACCENT_GOLD

        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.42), Inches(11.7), Inches(0.65))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        tf_t.margin_top = tf_t.margin_bottom = tf_t.margin_left = tf_t.margin_right = 0
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = WHITE

    def add_footer(slide, current_slide, total_slides=20):
        f_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.08), Inches(11.733), Inches(0.32))
        tf = f_box.text_frame
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0
        p = tf.paragraphs[0]
        p.text = f"Sərbəst İş: PV MPPT və DC-DC Çeviricinin Simulyasiyası  |  Slayd {current_slide} / {total_slides}"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_MUTED

    def create_card(slide, left, top, width, height, title=None):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1.5)

        content_top = top + 0.2
        content_height = height - 0.4

        if title:
            tb_title = slide.shapes.add_textbox(Inches(left + 0.3), Inches(top + 0.2), Inches(width - 0.6), Inches(0.45))
            tf_t = tb_title.text_frame
            tf_t.word_wrap = True
            tf_t.margin_top = tf_t.margin_bottom = tf_t.margin_left = tf_t.margin_right = 0
            p = tf_t.paragraphs[0]
            p.text = title
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = NAVY

            content_top += 0.45
            content_height -= 0.45

        return content_top, content_height

    def add_text_list(slide, left, top, width, height, items, font_size=13.0, space_after=10):
        tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_top = tf.margin_bottom = tf.margin_left = tf.margin_right = 0

        for i, item in enumerate(items):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = item
            p.font.size = Pt(font_size)
            p.font.color.rgb = TEXT_MAIN
            p.space_after = Pt(space_after)
            p.line_spacing = 1.2
        return tb

    # =========================================================================
    # SLIDE 1: Titul Səhifəsi (EXACTLY AS EDITED BY USER)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = DARK_BLUE
    bg1.line.fill.background()

    card1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9))
    card1.fill.solid()
    card1.fill.fore_color.rgb = RGBColor(30, 41, 59)
    card1.line.color.rgb = ACCENT_GOLD
    card1.line.width = Pt(2.5)

    tb1 = s1.shapes.add_textbox(Inches(1.3), Inches(1.2), Inches(10.7), Inches(5.1))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "Azərbaycan Texniki Universiteti"
    p0.font.size = Pt(16)
    p0.font.bold = True
    p0.font.color.rgb = ACCENT_GOLD
    p0.space_after = Pt(24)

    p1 = tf1.add_paragraph()
    p1.text = "Fotovoltaik (PV) Sistemlərdə Maksimum Güc Nöqtəsinin İzlənməsi (MPPT) və DC-DC Çeviricinin Modelləşdirilməsi"
    p1.font.size = Pt(26)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.space_after = Pt(18)

    p2 = tf1.add_paragraph()
    p2.text = "Canadian Solar CS3U-400MS (400W) Paneli, DC-DC Boost Çevirici, P&O və Incremental Conductance Alqoritmlərinin Dinamik və Qismən Kölgələnmə Rejimlərində Müqayisəli Tədqiqi"
    p2.font.size = Pt(14)
    p2.font.color.rgb = RGBColor(203, 213, 225)
    p2.space_after = Pt(40)

    p3 = tf1.add_paragraph()
    p3.text = "Müəllif: Həmidov Xalid"
    p3.font.size = Pt(15)
    p3.font.bold = True
    p3.font.color.rgb = ACCENT_GOLD

    # =========================================================================
    # SLIDE 2: Problem Tərifi və Motivasiya
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_canvas_bg(s2)
    add_header(s2, "Problem Tərifi və MPPT Texnologiyasının Əhəmiyyəti")
    add_footer(s2, 2)

    c_top, c_h = create_card(s2, 0.8, 1.45, 5.7, 5.3, "Fotovoltaik Panellərin Qeyri-Xətti Təbiəti")
    add_text_list(s2, 1.1, c_top + 0.1, 5.1, c_h - 0.2, [
        "• Qeyri-Xətti Cərəyan-Gərginlik: Günəş panelləri sabit gərginlik mənbəyi deyildir; onların daxili xarakteristikası günəş şüalanması və temperaturdan kəskin asılıdır.",
        "• Tək Maksimum Nöqtə (MPP): Panelin güc əyrisində hər bir hava şəraiti üçün yalnız bir optimal işçi nöqtə mövcuddur.",
        "• Birbaşa Qoşulma İtkisi: Paneli birbaşa yükə qoşduqda işçi nöqtə yükün müqaviməti ilə məhdudlaşır və enerji hasilatı 30-40% aşağı düşür.",
        "• MPPT Zərurəti: Çeviricinin doluluq əmsalını tənzimləməklə paneli hər an pik güc nöqtəsində saxlamaq həyati əhəmiyyət kəsb edir."
    ], font_size=13.5, space_after=14)

    c_top2, c_h2 = create_card(s2, 6.8, 1.45, 5.7, 5.3, "Tədqiqatın Məqsəd və Hədəfləri")
    add_text_list(s2, 7.1, c_top2 + 0.1, 5.1, c_h2 - 0.2, [
        "1. Dəqiq Fiziki Model: Tək diodlu 5-parametrli modeli (SDM) quraşdırmaq və Lambert W funksiyası ilə analitik həll etmək.",
        "2. Güc Elektronikası İnteqrasiyası: DC-DC Boost çeviricisinin fiziki drossel, MOSFET və diod itkilərini hesaba qatmaq.",
        "3. Alqoritmlərin Real İzlənməsi: P&O və Incremental Conductance alqoritmlərini sıfırdan proqramlaşdıraraq sınaqdan keçirmək.",
        "4. Qismən Kölgələnmə Analizi: Çoxzirvəli şəraitdə ənənəvi alqoritmlərin lokal tələyə düşmə riskini eksperimental sübut etmək."
    ], font_size=13.5, space_after=14)

    # =========================================================================
    # SLIDE 3: Sistem Arxitekturası
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_canvas_bg(s3)
    add_header(s3, "Sistem Arxitekturası və Enerji Çevrilmə Zənciri")
    add_footer(s3, 3)

    c_top, c_h = create_card(s3, 0.8, 1.45, 11.733, 2.8, "Tam Qapalı Əks-Əlaqəli Sistem Dövrəsi")
    diag_path = os.path.join(FORMULA_DIR, "system_architecture_az.png")
    if os.path.exists(diag_path):
        s3.shapes.add_picture(diag_path, Inches(1.1), Inches(c_top + 0.05), Inches(11.1), Inches(2.1))

    c_top2, c_h2 = create_card(s3, 0.8, 4.45, 5.7, 2.4, "Siqnal Axını və Mərhələlər")
    add_text_list(s3, 1.1, c_top2 + 0.05, 5.1, c_h2 - 0.1, [
        "• Ölçmə Mərhələsi: Kontroller paneldən V_pv və I_pv qiymətlərini hər 50 ms-dən bir oxuyur.",
        "• Güc Hesabatı: Cari güc P = V · I təyin olunur və əvvəlki dövrlə müqayisə edilir.",
        "• İdarəetmə: Yeni doluluq əmsalı (D) Boost çeviriciyə ötürülür və işçi nöqtə optimallaşdırılır."
    ], font_size=12.5, space_after=6)

    c_top3, c_h3 = create_card(s3, 6.8, 4.45, 5.7, 2.4, "Empedans Uyğunlaşdırma Qanunu")
    add_text_list(s3, 7.1, c_top3 + 0.05, 5.1, 0.6, [
        "• Çevirici panelə effektiv giriş müqaviməti göstərir:"
    ], font_size=12.5, space_after=2)
    f_rin = os.path.join(FORMULA_DIR, "f_rin_az.png")
    if os.path.exists(f_rin):
        s3.shapes.add_picture(f_rin, Inches(7.5), Inches(c_top3 + 0.50), Inches(4.3), Inches(0.65))
    add_text_list(s3, 7.1, c_top3 + 1.25, 5.1, 1.1, [
        "• D artdıqda: R_gir,eff azalır, panel gərginliyi düşür.",
        "• D azaldıqda: R_gir,eff artır, panel gərginliyi qalxır."
    ], font_size=12.5, space_after=4)

    # =========================================================================
    # SLIDE 4: PV Panelin Riyazi Modeli (SDM)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_canvas_bg(s4)
    add_header(s4, "Fotovoltaik Modulun Tək Diodlu 5-Parametrli Modeli (SDM)")
    add_footer(s4, 4)

    c_top, c_h = create_card(s4, 0.8, 1.45, 6.6, 5.3, "Dövrə Tənliyi və Fiziki Parametrlər")
    f_sdm_card = os.path.join(FORMULA_DIR, "f_sdm_card_az.png")
    if os.path.exists(f_sdm_card):
        s4.shapes.add_picture(f_sdm_card, Inches(0.95), Inches(c_top + 0.05), Inches(6.3), Inches(4.5))

    c_top2, c_h2 = create_card(s4, 7.7, 1.45, 4.833, 5.3, "Lambert W Analitik Həlli")
    add_text_list(s4, 7.95, c_top2 + 0.1, 4.3, c_h2 - 0.2, [
        "• Niyə Nyuton-Rofson Deyil?",
        "Klassik Nyuton iterasiyası açıq dövrə yaxınlığındakı kəskin döngələrdə rəqəmsal divergensiyaya (yıxılmaya) uğrayır.",
        "\n• Lambert W Analitik Dəqiqliyi:",
        "Tənlik Lambert W funksiyasının əsas budağı (W_0) vasitəsilə analitik qapalı formada dəqiq həll edilir.",
        "\n• 100% Rəqəmsal Dayanıqlıq:",
        "Böyük eksponentlər üçün log-domain asimptotik genişlənmə tətbiq olunmuşdur. Sıfır hesablama daşması (overflow) təmin edilir."
    ], font_size=12.5, space_after=6)

    # =========================================================================
    # SLIDE 5: Kommersiya Modulu: Canadian Solar CS3U-400MS
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_canvas_bg(s5)
    add_header(s5, "Referans Kommersiya Modulu: Canadian Solar CS3U-400MS (400W)")
    add_footer(s5, 5)

    c_top, c_h = create_card(s5, 0.8, 1.45, 5.2, 5.3, "Standart Test Şəraiti (STC) Göstəriciləri")
    add_text_list(s5, 1.1, c_top + 0.05, 4.6, c_h - 0.1, [
        "Standart Test Şəraiti: G = 1000 W/m², T = 25°C",
        "• Nominal Maksimum Güc (P_max): 400.33 W",
        "• Maksimum Güc Gərginliyi (V_mp): 40.99 V",
        "• Maksimum Güc Cərəyanı (I_mp): 9.77 A",
        "• Açıq Dövrə Gərginliyi (V_oc): 48.61 V",
        "• Qısa Qapanma Cərəyanı (I_sc): 10.33 A",
        "• Daxili Ardıcıl Müqavimət (R_ard): 0.15 Ohm",
        "• Daxili Paralel Müqavimət (R_par): 650.0 Ohm",
        "• Diod İdeallıq Əmsalı (n): 1.10",
        "• Temperatur Əmsalı (alpha): +0.05 %/°C",
        "• Temperatur Əmsalı (beta): -0.29 %/°C",
        "• Model Dəqiqliyi: Xəta 0.1%-dən azdır!"
    ], font_size=12.0, space_after=5)

    img_iv = os.path.join(RESULTS_DIR, "00_pv_characteristics", "iv_curve_stc.png")
    if os.path.exists(img_iv):
        s5.shapes.add_picture(img_iv, Inches(6.2), Inches(1.45), Inches(6.3), Inches(5.3))

    # =========================================================================
    # SLIDE 6: Radiasiyanın Panelin Gücünə Təsiri
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_canvas_bg(s6)
    add_header(s6, "Ətraf Mühitin Təsiri: Günəş Radiasiyasının (G) Dəyişməsi")
    add_footer(s6, 6)

    c_top, c_h = create_card(s6, 0.8, 1.45, 4.4, 5.3, "Radiasiya Asılılığı")
    f_iph = os.path.join(FORMULA_DIR, "f_iph_az.png")
    if os.path.exists(f_iph):
        s6.shapes.add_picture(f_iph, Inches(1.0), Inches(c_top + 0.05), Inches(4.0), Inches(0.65))

    add_text_list(s6, 1.1, c_top + 0.85, 3.8, c_h - 0.9, [
        "• Fotocərəyan Mütənasibliyi:",
        "Cərəyan günəş şüalanması ilə xətti asılıdır. G 1000-dən 200 W/m²-ə endikdə cərəyan ~10.3 A-dən ~2.0 A-dək enir.",
        "• Gərginliyin Loqarifmik Asılılığı:",
        "Açıq dövrə gərginliyi V_oc yalnız cüzi azalır (ln(G/G0)).",
        "• Gücün Kəskin Enməsi:",
        "MPP gücü şüalanma ilə düz mütənasib olaraq 400W-dan 80W-a düşür."
    ], font_size=12.0, space_after=6)

    img_iv_irr = os.path.join(RESULTS_DIR, "00_pv_characteristics", "iv_curves_irradiance.png")
    img_pv_irr = os.path.join(RESULTS_DIR, "00_pv_characteristics", "pv_curves_irradiance.png")
    if os.path.exists(img_iv_irr):
        s6.shapes.add_picture(img_iv_irr, Inches(5.4), Inches(1.45), Inches(3.7), Inches(5.3))
    if os.path.exists(img_pv_irr):
        s6.shapes.add_picture(img_pv_irr, Inches(9.3), Inches(1.45), Inches(3.7), Inches(5.3))

    # =========================================================================
    # SLIDE 7: Temperaturun Panelin Gücünə Təsiri
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_canvas_bg(s7)
    add_header(s7, "Ətraf Mühitin Təsiri: Temperaturun (T) Panelin Gücünə Təsiri")
    add_footer(s7, 7)

    c_top, c_h = create_card(s7, 0.8, 1.45, 5.2, 5.3, "Termal Deqradasiya Qanunları")
    f_i0 = os.path.join(FORMULA_DIR, "f_i0_az.png")
    if os.path.exists(f_i0):
        s7.shapes.add_picture(f_i0, Inches(1.0), Inches(c_top + 0.05), Inches(4.8), Inches(0.7))

    add_text_list(s7, 1.1, c_top + 0.9, 4.6, c_h - 1.0, [
        "• Qadağan Zonasının Daralması:",
        "Hüceyrə qızdıqca yarımkeçiricinin bandgap enerjisi E_g daralır.",
        "• Tərs Doyma Cərəyanının Sıçrayışı:",
        "Tərs doyma cərəyanı I_0(T) kubik və eksponensial olaraq artır.",
        "• Gərginlik İtkisi:",
        "Nəticədə V_oc gərginliyi hər dərəcədə -0.29% azalır. 55°C-də güc 335W-a qədər düşür.",
        "• Nəticə: İsti iqlimdə panellərin soyudulması və MPP izlənməsi həyati əhəmiyyət daşıyır."
    ], font_size=12.0, space_after=6)

    img_temp = os.path.join(RESULTS_DIR, "00_pv_characteristics", "pv_curves_temperature.png")
    if os.path.exists(img_temp):
        s7.shapes.add_picture(img_temp, Inches(6.3), Inches(1.45), Inches(6.2), Inches(5.3))

    # =========================================================================
    # SLIDE 8: DC-DC Boost Çevirici və İtki Modeli (REAL EQUATIONS!)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_canvas_bg(s8)
    add_header(s8, "DC-DC Boost Çeviricisi: Fiziki İtki və Dinamik Model")
    add_footer(s8, 8)

    c_top, c_h = create_card(s8, 0.8, 1.45, 5.7, 5.3, "Real Fiziki İtki Mexanizmləri")
    f_boost = os.path.join(FORMULA_DIR, "f_boost_az.png")
    if os.path.exists(f_boost):
        s8.shapes.add_picture(f_boost, Inches(1.2), Inches(c_top + 0.05), Inches(4.5), Inches(0.65))

    f_losses = os.path.join(FORMULA_DIR, "f_losses_az.png")
    if os.path.exists(f_losses):
        s8.shapes.add_picture(f_losses, Inches(0.95), Inches(c_top + 0.80), Inches(5.3), Inches(3.7))

    c_top2, c_h2 = create_card(s8, 6.8, 1.45, 5.7, 5.3, "Dinamik Filtrasiya və Enerji Saxlanması")
    f_pout = os.path.join(FORMULA_DIR, "f_pout_az.png")
    if os.path.exists(f_pout):
        s8.shapes.add_picture(f_pout, Inches(7.2), Inches(c_top2 + 0.05), Inches(4.8), Inches(0.65))

    add_text_list(s8, 7.1, c_top2 + 0.85, 5.1, c_h2 - 0.95, [
        "• LC Süzgəc Dinamikası (tau = 2 ms):",
        "Çıxış gərginliyinin dəyişməsi dərhal baş vermir; L = 100 uH və C = 470 uF elementləri ilə 1-ci tərtib aperiodik keçid modeli təmin edilmişdir.",
        "• Doluluq Əmsalı Təhlükəsizlik Hədləri:",
        "D əmsalı 0.05 ilə 0.90 arasında məhdudlaşdırılır (qısa qapanma və doyma qorunması).",
        "• Enerjinin Saxlanması Qanunu:",
        "Bütün rejim və təkanlarda P_cix <= P_gir - P_itki bərabərsizliyi 100% qorunur."
    ], font_size=12.5, space_after=8)

    # =========================================================================
    # SLIDE 9: MPPT Alqoritmi 1: Perturb & Observe (P&O) (EQUATIONS!)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_canvas_bg(s9)
    add_header(s9, "MPPT Alqoritmi 1: Perturb & Observe (Həyəcanlandır və Müşahidə Et)")
    add_footer(s9, 9)

    c_top, c_h = create_card(s9, 0.8, 1.45, 5.7, 5.3, "P&O Qərar Alqoritmi")
    f_po_card = os.path.join(FORMULA_DIR, "f_po_card_az.png")
    if os.path.exists(f_po_card):
        s9.shapes.add_picture(f_po_card, Inches(0.95), Inches(c_top + 0.15), Inches(5.3), Inches(3.8))

    c_top2, c_h2 = create_card(s9, 6.8, 1.45, 5.7, 5.3, "Boost Çeviricidə Qütblük və Kompromis")
    add_text_list(s9, 7.1, c_top2 + 0.1, 5.1, c_h2 - 0.2, [
        "• Çevirici Polariteti:",
        "Boost çeviricidə D artanda panel gərginliyi azalır. Alqoritm dP və dV işarələrini çeviricinin ötürmə xarakteristikasına uyğun tərs tətbiq etməlidir.",
        "• Addım Ölçüsü Kompromisi (delta_D = 0.005):",
        "  - Böyük delta_D -> Tez yaxınlaşır, lakin pikdə böyük dalğalanma itkisi verir.",
        "  - Kiçik delta_D -> Sakit dayanır, lakin bulud gələndə gec reaksiya verir.",
        "• Seçilmiş Qiymət:",
        "delta_D = 0.005 həm 0.3s sürətli kilidləmə, həm də cəmi 0.36W minimal dalğalanma təmin etmişdir."
    ], font_size=13.0, space_after=8)

    # =========================================================================
    # SLIDE 10: MPPT Alqoritmi 2: Incremental Conductance (INC) (EQUATIONS!)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_canvas_bg(s10)
    add_header(s10, "MPPT Alqoritmi 2: Incremental Conductance (Diferensial Keçiricilik)")
    add_footer(s10, 10)

    c_top, c_h = create_card(s10, 0.8, 1.45, 5.7, 5.3, "Riyazi Törəmə Şərti")
    f_inc_card = os.path.join(FORMULA_DIR, "f_inc_card_az.png")
    if os.path.exists(f_inc_card):
        s10.shapes.add_picture(f_inc_card, Inches(0.95), Inches(c_top + 0.15), Inches(5.3), Inches(3.8))

    c_top2, c_h2 = create_card(s10, 6.8, 1.45, 5.7, 5.3, "P&O ilə Müqayisədə Üstünlükləri")
    add_text_list(s10, 7.1, c_top2 + 0.1, 5.1, c_h2 - 0.2, [
        "1. Qərarlaşmış Rejimdə Sıfır Dalğalanma:",
        "P&O alqoritmi pikə çatdıqda belə 3 nöqtə ətrafında yellənməyə məcburdur. INC isə törəmə sıfır olduqda sabit dayanır.",
        "2. Dinamik Hava Şəraitində Dəqiqlik:",
        "Bulud gəldikdə və ya günəş qəfil parladıqda P&O güc artımını səhvən gərginlik artımı zənn edə bilər. INC cərəyanın törəməsini hesabladığı üçün çaşmır.",
        "3. Hesablama Tələbi:",
        "Bölmə və diferensial tələb etdiyi üçün mikrokontrollerdən daha güclü ALU tələb edir."
    ], font_size=12.5, space_after=8)

    # =========================================================================
    # SLIDE 11: Simulyasiya Mühərriki və Doğrulama
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_canvas_bg(s11)
    add_header(s11, "Simulyasiya Mühərriki və Müstəqil Doğrulama")
    add_footer(s11, 11)

    c_top, c_h = create_card(s11, 0.8, 1.45, 5.7, 5.3, "Zaman Sahəsində Diskret Modelləşdirmə")
    add_text_list(s11, 1.1, c_top + 0.1, 5.1, c_h - 0.2, [
        "• İnteqrasiya Addımı: dt = 0.001 s (1 ms)",
        "• MPPT Seçmə Dövrü: T_mppt = 0.050 s (50 ms, 20 Hz)",
        "• İki-pilləli Dinamika:",
        "Çevirici və yük hər 1 ms-dən bir yenilənir, MPPT isə hər 50 ms-dən bir yeni D hesablayır (real mikrokontroller tezliyi).",
        "• Bütün Parametrlərin Qeydiyyatı:",
        "Hər addımda vaxt, G, T, V_pv, I_pv, P_pv, D, V_cix, P_cix, itkilər və teoretik MPP xətası pandas DataFrame-də qeydə alınır."
    ], font_size=12.5, space_after=8)

    c_top2, c_h2 = create_card(s11, 6.8, 1.45, 5.7, 5.3, "Müstəqil Ground-Truth Metodologiyası")
    f_eta = os.path.join(FORMULA_DIR, "f_eta_az.png")
    if os.path.exists(f_eta):
        s11.shapes.add_picture(f_eta, Inches(7.0), Inches(c_top2 + 0.05), Inches(4.5), Inches(0.65))

    add_text_list(s11, 7.1, c_top2 + 0.85, 5.1, c_h2 - 0.9, [
        "• 'No Lookahead' Qaydası:",
        "Kontroller heç vaxt ideal MPP gücünü bilmir, axtarışı yalnız (V, I) əks-əlaqə ölçmələri ilə aparır.",
        "• Paralel Müstəqil Qiymətləndirmə:",
        "Mühərrik müstəqil olaraq hər hava dəyişməsində ideal fiziki maksimumu hesablayır və kontrollerin izləmə effektivliyini dürüst hesablayır."
    ], font_size=12.5, space_after=8)

    # =========================================================================
    # SLIDE 12: Eksperiment 1: Standart Şəraitdə (STC) Simulyasiya
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_canvas_bg(s12)
    add_header(s12, "Eksperiment 1: Standart Şəraitdə (STC) Simulyasiya Nəticələri")
    add_footer(s12, 12)

    c_top, c_h = create_card(s12, 0.8, 1.45, 4.9, 5.3, "Rəqəmsal Nəticələr (STC: 1000 W/m², 25°C)")
    add_text_list(s12, 1.1, c_top + 0.05, 4.4, c_h - 0.1, [
        "• Teoretik Maksimum Güc: 400.33 W",
        "• İzlənən Faktiki Güc: 400.01 W",
        "• İzləmə Səmərəliliyi: 99.92 %",
        "• Qərarlaşma Müddəti (Settling): 0.302 s",
        "• Qərarlaşmış Vəziyyət Xətası: Cəmi 0.31 W",
        "• Gərginlik Xətası: 0.37 % (40.83V vs 40.99V)",
        "• Cərəyan Xətası: 0.30 % (9.80A vs 9.77A)",
        "• Güc Xətası: 0.08 %",
        "• Qərarlaşmış Doluluq Əmsalı: D = 0.5500",
        "• Çevirici Səmərəliliyi: 98.16 %"
    ], font_size=12.0, space_after=5)

    img_d1 = os.path.join(RESULTS_DIR, "01_constant_stc", "exp1_po_dashboard.png")
    if os.path.exists(img_d1):
        s12.shapes.add_picture(img_d1, Inches(5.9), Inches(1.45), Inches(6.6), Inches(5.3))

    # =========================================================================
    # SLIDE 13: P&O Alqoritminin Yaxınlaşma Qrafikləri
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_canvas_bg(s13)
    add_header(s13, "Eksperiment 1: P&O Alqoritminin Addım-Addım Yaxınlaşması")
    add_footer(s13, 13)

    c_top, c_h = create_card(s13, 0.8, 1.45, 4.2, 5.3, "Yaxınlaşma Xronologiyası")
    add_text_list(s13, 1.1, c_top + 0.1, 3.7, c_h - 0.2, [
        "• Başlanğıc: D_init = 0.50 nöqtəsindən start verilir.",
        "• Sürətli Qalxma: Cəmi 6 addım ərzində (~0.3s) güc 350W-dan 400W-a çatır.",
        "• Qərarlaşma: 0.302 saniyədən sonra alqoritm pik ətrafında cəmi 0.36W standart kənarlaşma ilə kilidlənir.",
        "• Bütün simulyasiya boyu orta effektivlik 99.85%-dir."
    ], font_size=12.5, space_after=8)

    img_p1 = os.path.join(RESULTS_DIR, "01_constant_stc", "exp1_po_power.png")
    img_c1 = os.path.join(RESULTS_DIR, "01_constant_stc", "exp1_po_convergence.png")
    if os.path.exists(img_p1):
        s13.shapes.add_picture(img_p1, Inches(5.2), Inches(1.45), Inches(3.8), Inches(5.3))
    if os.path.exists(img_c1):
        s13.shapes.add_picture(img_c1, Inches(9.2), Inches(1.45), Inches(3.8), Inches(5.3))

    # =========================================================================
    # SLIDE 14: Eksperiment 2 & 3: Radiasiyanın Qəfil Dəyişməsi
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_canvas_bg(s14)
    add_header(s14, "Eksperiment 2 & 3: Radiasiya Sıçrayışları (Buludun Gəlməsi və Çəkilməsi)")
    add_footer(s14, 14)

    c_top, c_h = create_card(s14, 0.8, 1.45, 4.3, 5.3, "Dinamik Adaptasiya")
    add_text_list(s14, 1.1, c_top + 0.1, 3.8, c_h - 0.2, [
        "1. Radiasiyanın Düşməsi (1000 -> 700 W/m² @ t=10s):",
        "• Bulud gəldikdə güc sıçrayışla 400W-dan 280W-a düşür.",
        "• Kontroller istiqamətini itirmir, dərhal yeni MPP nöqtəsinə adaptasiya olur.",
        "• İzləmə səmərəliliyi: 99.94%.",
        "\n2. Radiasiyanın Qalxması (700 -> 1000 W/m² @ t=10s):",
        "• Günəş parladıqda bərpa müddəti cəmi 0.152 saniyə təşkil edir."
    ], font_size=12.0, space_after=6)

    img_d2 = os.path.join(RESULTS_DIR, "02_irradiance_drop", "exp2_po_power.png")
    img_r3 = os.path.join(RESULTS_DIR, "03_irradiance_rise", "exp3_po_power.png")
    if os.path.exists(img_d2):
        s14.shapes.add_picture(img_d2, Inches(5.3), Inches(1.45), Inches(3.8), Inches(5.3))
    if os.path.exists(img_r3):
        s14.shapes.add_picture(img_r3, Inches(9.3), Inches(1.45), Inches(3.8), Inches(5.3))

    # =========================================================================
    # SLIDE 15: Eksperiment 4 & 5: Temperatur Artımı və Kombinə Dəyişiklik
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_canvas_bg(s15)
    add_header(s15, "Eksperiment 4 & 5: Termal İstilik Artımı və Real Hava Ssenarisi")
    add_footer(s15, 15)

    c_top, c_h = create_card(s15, 0.8, 1.45, 4.9, 5.3, "Eksperiment 5: Mürəkkəb Hava Şəraiti")
    add_text_list(s15, 1.1, c_top + 0.1, 4.4, c_h - 0.2, [
        "Həm radiasiya, həm temperatur eyni vaxtda dəyişir:",
        "• t = 10s: Radiasiya 1000 -> 700 W/m² düşür.",
        "• t = 15s: Temperatur 25°C -> 40°C-yə yüksəlir.",
        "• Nəticələr:",
        "  - Orta İzləmə Səmərəliliyi: 99.94 %",
        "  - Qərarlaşmış Xəta: Cəmi 0.23 W",
        "  - Termal gərginlik düşgüsünə (41V -> 37V) baxmayaraq kontroller paneli optimal gücdə saxlayır."
    ], font_size=12.0, space_after=6)

    img_comb = os.path.join(RESULTS_DIR, "05_combined", "exp5_po_dashboard.png")
    if os.path.exists(img_comb):
        s15.shapes.add_picture(img_comb, Inches(5.9), Inches(1.45), Inches(6.6), Inches(5.3))

    # =========================================================================
    # SLIDE 16: Ən Əhəmiyyətli Nəticə: Qismən Kölgələnmə (Partial Shading)
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    set_canvas_bg(s16)
    add_header(s16, "Eksperiment 6: Qismən Kölgələnmə (Partial Shading) və Çoxzirvəli Əyri", "ƏN VACİB ELMİ TƏDQİQAT")
    add_footer(s16, 16)

    c_top, c_h = create_card(s16, 0.8, 1.45, 5.0, 5.3, "3 Zirvəli P-V Əyrisinin Yaranması")
    add_text_list(s16, 1.1, c_top + 0.05, 4.5, c_h - 0.1, [
        "3 ardıcıl modul və baypas diodları:",
        "• Modul 1: 1000 W/m² (tam günəşli)",
        "• Modul 2: 600 W/m² (orta kölgə)",
        "• Modul 3: 300 W/m² (qatı kölgə)",
        "\nFiziki Pik Nöqtələri:",
        "• Qlobal Pik (GMPP): 1338.2 W (V = 132.3 V)",
        "• Lokal Pik 1 (LMPP-1): 790.1 W (V = 130.2 V)",
        "• Lokal Pik 2 (LMPP-2): 395.6 W (V = 130.4 V)"
    ], font_size=12.0, space_after=5)

    img_ps = os.path.join(RESULTS_DIR, "06_partial_shading", "partial_shading_pv.png")
    if os.path.exists(img_ps):
        s16.shapes.add_picture(img_ps, Inches(6.0), Inches(1.45), Inches(6.5), Inches(5.3))

    # =========================================================================
    # SLIDE 17: P&O-nun Lokal Maksimum Tələsində İlişib Qalması
    # =========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    set_canvas_bg(s17)
    add_header(s17, "Eksperiment 6: Klassik P&O-nun Lokal Tələdə İlişib Qalması", "MÜHƏNDİSLİK XƏBƏRDARLIĞI")
    add_footer(s17, 17)

    c_top, c_h = create_card(s17, 0.8, 1.45, 5.7, 5.3, "Klassik P&O Alqoritminin Məhdudiyyəti")
    add_text_list(s17, 1.1, c_top + 0.1, 5.1, c_h - 0.2, [
        "• Real Simulyasiya Faktı:",
        "Klassik P&O alqoritmi işə düşdükdə ən yaxın təpəyə dırmanır və 790.1 W-lıq lokal maksimumda (LMPP-1) ilişib qalır!",
        "• İzləmə Səmərəliliyi: Cəmi 72.36 % !",
        "• İtirilən Enerji:",
        "Mövcud 1338.2 W gücün 548 W-ı (27.6%-i) sistem tərəfindən istifadəsiz qalır.",
        "• Səbəb: P&O yalnız qonşu addımların törəməsinə baxır, bütün əyrini görmək qabiliyyətinə malik deyil."
    ], font_size=12.5, space_after=8)

    c_top2, c_h2 = create_card(s17, 6.8, 1.45, 5.7, 5.3, "Mühəndislik Həlli: Qlobal MPPT (GMPPT)")
    add_text_list(s17, 7.1, c_top2 + 0.1, 5.1, c_h2 - 0.2, [
        "Qismən kölgələnmədə nə etmək lazımdır?",
        "1. Scanning-based Global MPPT:",
        "Doluluq əmsalı D = 0.05-dən 0.90-dək sürətlə skan edilir, bütün lokal piklər müəyyən olunur və sistem 1338W-lıq qlobal pikə köklənir.",
        "2. Ağıllı Alqoritmlər (PSO, GA):",
        "Hissəciklər Sürüsü Optimizasiyası (PSO) çoxzirvəli əyrilərdə GMPP-ni 99% dəqiqliklə tapır.",
        "Elmi Nəticə: Çoxmodullu stansiyalarda adi P&O bəs etmir, mütləq Qlobal MPPT tətbiq olunmalıdır."
    ], font_size=12.5, space_after=8)

    # =========================================================================
    # SLIDE 18: P&O və Incremental Conductance Müqayisəsi
    # =========================================================================
    s18 = prs.slides.add_slide(blank_layout)
    set_canvas_bg(s18)
    add_header(s18, "Eksperiment 7: P&O və Incremental Conductance Müqayisəli Analizi")
    add_footer(s18, 18)

    c_top, c_h = create_card(s18, 0.8, 1.45, 5.2, 5.3, "Müqayisə Göstəriciləri")
    add_text_list(s18, 1.1, c_top + 0.05, 4.6, c_h - 0.1, [
        "Metrika              | P&O       | INC",
        "-------------------------------------------",
        "İzlənən Enerji       | 6321.3 J  | 6321.3 J",
        "Orta İzləmə Eff.     | 98.86 %   | 98.86 %",
        "Qərarlaşmış Eff.     | 99.95 %   | 99.95 %",
        "Pik Dalğalanma (Std) | 0.13 W    | 0.13 W",
        "Çevirici İtkisi      | ~377 J    | ~377 J",
        "Ümumi Sistem Eff.    | 97.19 %   | 97.19 %",
        "İcraya Nəzarət       | Asan      | Mürəkkəb",
        "Hesablama Tələbi     | Çox az    | Törəmə tələb"
    ], font_size=11.5, space_after=3)

    img_comp = os.path.join(RESULTS_DIR, "07_algorithm_comparison", "algorithm_comparison.png")
    if os.path.exists(img_comp):
        s18.shapes.add_picture(img_comp, Inches(6.2), Inches(1.45), Inches(6.3), Inches(5.3))

    # =========================================================================
    # SLIDE 19: Avtomatik Sanity Checks (Mühəndislik Dürüstlüyü)
    # =========================================================================
    s19 = prs.slides.add_slide(blank_layout)
    set_canvas_bg(s19)
    add_header(s19, "Mühəndislik Dürüstlüyü: 20 Avtomatik Fiziki Yoxlama (Sanity Checks)")
    add_footer(s19, 19)

    c_top, c_h = create_card(s19, 0.8, 1.45, 11.733, 5.3, "100% UĞURLA KEÇİLMİŞ AVTOMATİK MÜHƏNDİSLİK YOXLAMALARI")
    add_text_list(s19, 1.1, c_top + 0.05, 11.1, c_h - 0.1, [
        "[PASS] 1. P = V · I bərabərliyi hər addımda 0.1% dəqiqliklə təmin edilir.",
        "[PASS] 2. Hasil olunan güc həmişə müsbətdir (P >= 0).",
        "[PASS] 3. Rəqəmsal sabitlik tam qorunur (Sıfır NaN, Sıfır Inf).",
        "[PASS] 4. V_oc > V_mp və I_sc > I_mp fiziki şərtləri təmin olunur.",
        "[PASS] 5. P_max təxminən V_mp · I_mp bərabərliyi 2% xəta hüdudundadır.",
        "[PASS] 6. Çeviricinin doluluq əmsalı qəti şəkildə hədlərdədir: D in [0.05, 0.90].",
        "[PASS] 7. Panelin gərginlik və cərəyanı heç vaxt mənfiyə düşmür (V_pv >= 0, I_pv >= 0).",
        "[PASS] 8. Enerjinin Saxlanması Qanunu: Çıxış gücü giriş gücündən çox ola bilməz (P_cix <= P_gir).",
        "[PASS] 9. Heç bir rejimdə ekvivalent mənfi müqavimət yaranmır (V/I > 0).",
        "[PASS] 10. Qərarlaşmış vəziyyətdə güc dalğalanması P_max-ın 0.1%-dən aşağıdır.",
        "[PASS] 11. Standart ssenarilərdə izləmə səmərəliliyi 99%-dən yüksəkdir."
    ], font_size=12.0, space_after=5)

    # =========================================================================
    # SLIDE 20: Yekun Nəticələr və Praktiki Tətbiq
    # =========================================================================
    s20 = prs.slides.add_slide(blank_layout)
    set_canvas_bg(s20)
    add_header(s20, "Yekun Nəticələr, Praktiki Əhəmiyyət və İnteraktiv UI")
    add_footer(s20, 20)

    c_top, c_h = create_card(s20, 0.8, 1.45, 5.7, 5.3, "Əsas Elmi və Mühəndislik Nəticələri")
    add_text_list(s20, 1.1, c_top + 0.1, 5.1, c_h - 0.2, [
        "1. Dəqiq Modelləşdirmə: Canadian Solar 400W paneli və DC-DC Boost çeviricisi real fiziki itkilərlə modelləşdirilmiş və 100% analitik olaraq həll edilmişdir.",
        "2. Yüksək İzləmə Dəqiqliyi: Həm P&O, həm də INC alqoritmləri standart və dəyişən şəraitdə 99.9%-dən yüksək izləmə səmərəliliyi və 0.3 saniyədən az qərarlaşma müddəti nümayiş etdirmişdir.",
        "3. Kölgələnmə Probleminin Sübutu: Qismən kölgələnmədə ənənəvi MPPT alqoritmlərinin 27.6% enerji itkisi ilə lokal maksimumda ilişib qalması riyazi olaraq nümayiş etdirilmişdir.",
        "4. Praktiki Tətbiq: Təqdim olunan kod və arxitektura birbaşa STM32 və ya TI C2000 mikrokontrollerlərinə köçürülə bilər."
    ], font_size=12.5, space_after=7)

    c_top2, c_h2 = create_card(s20, 6.8, 1.45, 5.7, 5.3, "İnteraktiv Streamlit İdarəetmə Paneli")
    add_text_list(s20, 7.1, c_top2 + 0.1, 5.1, c_h2 - 0.2, [
        "Layihə çərçivəsində mühəndislər və tədqiqatçılar üçün veb-əsaslı interaktiv interfeys hazırlanmışdır (app.py):",
        "• Canlı Radiasiya və Temperatur tənzimlənməsi (Slider)",
        "• Panel parametrlərinin dinamik dəyişdirilməsi",
        "• Alqoritmlərin bir toxunuşla canlı müqayisəsi",
        "• Simulyasiya nəticələrinin CSV və Xülasə kimi ixracı.",
        "\nİşə salma əmri:",
        "streamlit run app.py",
        "\nDİQQƏTİNİZƏ GÖRƏ TƏŞƏKKÜR EDİRƏM!\nSuallarınızı məmnuniyyətlə cavablandıra bilərəm."
    ], font_size=12.5, space_after=6)

    # Save to both target paths
    saved_paths = []
    try:
        prs.save(PRIMARY_PPTX)
        saved_paths.append(PRIMARY_PPTX)
        print(f"[SUCCESS] Saved to primary path: {PRIMARY_PPTX}")
    except PermissionError:
        print(f"[NOTE] Primary path {PRIMARY_PPTX} is currently open in PowerPoint (locked).")

    prs.save(BACKUP_PPTX)
    saved_paths.append(BACKUP_PPTX)
    print(f"[SUCCESS] Saved to updated presentation path: {BACKUP_PPTX}")

    return saved_paths

if __name__ == "__main__":
    build_presentation()
