# -*- coding: utf-8 -*-
r"""
Generate comprehensive Word Document (.docx) for Streamlit MPPT Demo & Presentation Guide.
Target: C:\Users\ASUS\Desktop\MPPT_Streamlit_Canli_Numayis_ve_Teqdimat_Rehberi.docx
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

doc = docx.Document()

# Page Setup: Standard A4 or Letter, 1 inch margins
for section in doc.sections:
    section.top_margin = Inches(0.9)
    section.bottom_margin = Inches(0.9)
    section.left_margin = Inches(0.9)
    section.right_margin = Inches(0.9)

# Colors
NAVY = RGBColor(30, 58, 138)      # #1E3A8A
TEAL = RGBColor(13, 148, 136)     # #0D9488
DARK = RGBColor(31, 41, 55)       # #1F2937
MUTED = RGBColor(107, 114, 128)   # #6B7280
GOLD = RGBColor(180, 83, 9)       # #B45309

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=140, bottom=140, left=200, right=200):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def add_styled_heading(text, level=1):
    h = doc.add_heading(level=level)
    h.paragraph_format.keep_with_next = True
    run = h.add_run(text)
    run.font.name = 'Calibri'
    if level == 1:
        run.font.size = Pt(17)
        run.font.bold = True
        run.font.color.rgb = NAVY
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(6)
    elif level == 2:
        run.font.size = Pt(13.5)
        run.font.bold = True
        run.font.color.rgb = TEAL
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
    elif level == 3:
        run.font.size = Pt(11.5)
        run.font.bold = True
        run.font.color.rgb = GOLD
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(2)
    return h

def add_p(text, bold=False, italic=False, space_after=5, color=DARK, bullet=False):
    if bullet:
        p = doc.add_paragraph(style='List Bullet')
    else:
        p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(text)
    run.font.name = 'Calibri'
    run.font.size = Pt(10.5)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return p

def add_callout(text_list, title="ÇIXIŞ / İZAH MƏTNİ (Nümunə Ssenari)", border_color="1E3A8A", bg_color="F8FAFC"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.7)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=160, bottom=160, left=240, right=200)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>
            <w:top w:val="none"/>
            <w:right w:val="none"/>
            <w:bottom w:val="none"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(4)
    r_t = p.add_run(f"🗣️  {title}\n")
    r_t.font.name = 'Calibri'
    r_t.font.size = Pt(10.5)
    r_t.font.bold = True
    r_t.font.color.rgb = NAVY
    
    for item in text_list:
        p_item = cell.add_paragraph()
        p_item.paragraph_format.space_after = Pt(3)
        p_item.paragraph_format.line_spacing = 1.12
        r = p_item.add_run(item)
        r.font.name = 'Calibri'
        r.font.size = Pt(10)
        r.font.color.rgb = DARK
        if item.startswith("“") or item.startswith('"'):
            r.font.italic = True
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

# =========================================================================
# TITLE BLOCK
# =========================================================================
p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_title.paragraph_format.space_after = Pt(2)
run_title = p_title.add_run("GÜNƏŞ FOTOELEKTRİK SİSTEMLƏRİNDƏ MPPT İDARƏETMƏSİ")
run_title.font.name = 'Calibri'
run_title.font.size = Pt(22)
run_title.font.bold = True
run_title.font.color.rgb = NAVY

p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_sub.paragraph_format.space_after = Pt(12)
run_sub = p_sub.add_run("Streamlit Canlı Simulyasiya Veb Tətbiqinin Nümayişi, Real İstifadə Sahələri və Müəllimə Təqdimat Bələdçisi")
run_sub.font.name = 'Calibri'
run_sub.font.size = Pt(13)
run_sub.font.bold = True
run_sub.font.color.rgb = TEAL

# Info Box Table
t_info = doc.add_table(rows=4, cols=2)
t_info.alignment = WD_TABLE_ALIGNMENT.CENTER
info_data = [
    ("Canlı Veb Tətbiq Linki:", "https://mppt-simulator.streamlit.app/"),
    ("Açıq Mənbə GitHub Repozitoriyası:", "https://github.com/Malphorine/mppt-simulator"),
    ("Tədqiqatçı / Müəllif:", "Xalid Həmidov"),
    ("Məqsəd:", "Müəllim / Elmi heyət qarşısında canlı, interaktiv və inandırıcı 5-10 dəqiqəlik texniki nümayiş")
]
for row_idx, (k, v) in enumerate(info_data):
    cell_k = t_info.cell(row_idx, 0)
    cell_v = t_info.cell(row_idx, 1)
    cell_k.width = Inches(2.3)
    cell_v.width = Inches(4.4)
    set_cell_background(cell_k, "F1F5F9")
    set_cell_background(cell_v, "FFFFFF")
    set_cell_margins(cell_k, 80, 80, 100, 100)
    set_cell_margins(cell_v, 80, 80, 100, 100)
    
    pk = cell_k.paragraphs[0]
    rk = pk.add_run(k)
    rk.font.name = 'Calibri'
    rk.font.size = Pt(9.5)
    rk.font.bold = True
    rk.font.color.rgb = NAVY
    
    pv = cell_v.paragraphs[0]
    rv = pv.add_run(v)
    rv.font.name = 'Calibri'
    rv.font.size = Pt(9.5)
    rv.font.color.rgb = DARK
    if "http" in v:
        rv.font.bold = True
        rv.font.color.rgb = TEAL

p_div = doc.add_paragraph()
p_div.paragraph_format.space_after = Pt(10)

# =========================================================================
# SECTION 1: GİRİŞ VƏ İLK TƏƏSSÜRAT
# =========================================================================
add_styled_heading("1. Müəllim Qarşısında Giriş və Layihənin Fəlsəfəsi (İlk 1 Dəqiqə)", level=1)

add_p("Təqdimatın ilk 60 saniyəsi müəllimdə güclü professional təəssürat yaratmaq üçün ən vacib andır. Çox vaxt tələbələr sadəcə slayd oxuyur və ya kod parçaları göstərir. Sizin üstünlüyünüz ondan ibarətdir ki, siz nəzəriyyəni birbaşa canlı işləyən, real vaxt mühəndislik simulatoruna çevirmisiniz və istənilən brauzerdən daxil olmaq mümkündür.")

add_callout([
    "“Hörmətli müəllim, mən diplom / tədqiqat işim çərçivəsində təkcə nəzəri tənlikləri və statik PowerPoint slaydlarını təhlil etməklə kifayətlənmədim. Həqiqi mühəndislik yanaşması nümayiş etdirmək üçün sistemin bütün fiziki və idarəetmə zəncirini əks etdirən canlı, interaktiv veb simulator proqram təminatı hazırladım və qlobal buludda yerləşdirdim.”",
    "“Bu tətbiq (mppt-simulator.streamlit.app) birbaşa real vaxtda tək diodlu 5-parametrlik fotovoltaik paneli, DC-DC gücləndirici (Boost) çeviricisini və iki ən müasir MPPT alqoritmini — Perturb & Observe (P&O) və İnkremental Keçiricilik (INC) metodlarını simulyasiya edir.”",
    "“İcazənizlə, tətbiq üzərində canlı olaraq günəş şüalanması və temperatur dəyişdikdə sistemin necə davrandığını, eləcə də qismən kölgələnmə zamanı ənənəvi alqoritmlərin niyə iflas etdiyini sizə əyani şəkildə nümayiş etdirim.”"
], title="Müəllimə Giriş Danışıq Nitqi (Bunu əminliklə söyləyin)")

# =========================================================================
# SECTION 2: CANLI NÜMAYİŞ ADDIMLARI (LIVE DEMO WORKFLOW)
# =========================================================================
add_styled_heading("2. Müəllimə Addım-Addım Canlı Nümayiş Ssenarisi (Addımbaaddım Klik Bələdçisi)", level=1)

add_p("Tətbiqi açdıqda (https://mppt-simulator.streamlit.app/) ekranı aşağıdakı 5 məntiqi addımla nümayiş etdirin:")

# Step 1
add_styled_heading("Addım 1: PV Panelin Fiziki Xarakteristikaları (Tab 1: 📊 PV Characteristics)", level=2)
add_p("Nə etməli:", bold=True)
add_p("1. Brauzerdə ilk sekməyə daxil olun: '📊 PV Characteristics'.", bullet=True)
add_p("2. Sol paneldə (Sidebar) 'Irradiance G' slaydını 1000-dən 600 W/m²-ə çəkin.", bullet=True)
add_p("3. Sonra 'Temperature T' slaydını 25°C-dən 50°C-yə qaldırın.", bullet=True)

add_callout([
    "“Müəllim, birinci bölmədə biz kommersiya tipli Canadian Solar 400W mono-kristal panelinin fiziki xarakteristikalarını görürük.”",
    "“Diqqət yetirsəniz, mən şüalanmanı azaltdıqda cərəyan (I_sc) kəskin şəkildə proporsional düşür, lakin gərginlik cüzi dəyişir. Əksinə, temperaturu 25-dən 50 dərəcəyə qaldırdıqda qadağan olunmuş zonanın eni (Bandgap Eg) kiçilir və açıq dövrə gərginliyi Voc nəzərəçarpacaq dərəcədə azalır. Simulatorumuz bu dəyişiklikləri De Soto tənlikləri və analitik Lambert W funksiyası vasitəsilə 100% fiziki dəqiqliklə hesablayır.”"
], title="Addım 1 üçün Danışıq Mətni")

# Step 2
add_styled_heading("Addım 2: P&O Alqoritminin MPP-yə Çatması və 3 Nöqtəli Dalğalanma (Tab 2)", level=2)
add_p("Nə etməli:", bold=True)
add_p("1. İkinci sekməyə keçin: '📈 Simulation Results'.", bullet=True)
add_p("2. Sol paneldə Ssenari olaraq 'Constant' seçin (G = 1000 W/m², T = 25°C).", bullet=True)
add_p("3. 'Algorithm' bölməsində 'P&O' seçin və yaşıl '🚀 Run Simulation' düyməsini basın.", bullet=True)

add_callout([
    "“İndi isə sistemi 20 saniyəlik dinamik rejimdə işə salırıq. Gördüyünüz kimi, sistem D = 0.50 başlanğıc doluluq əmsalı ilə başlayır.”",
    "“P&O alqoritmi addım-addım dövrəni tənzimləyərək cəmi 0.3 saniyə ərzində panelin 400.3 Vt-lıq Maksimum Güc Nöqtəsinə (MPP) çatır.”",
    "“Müəllim, qrafiki böyütdükdə görünür ki, MPP-yə çatdıqdan sonra güc sabit qalmır, ±0.36 Vt diapazonunda davamlı dalğalanır. Bu, P&O alqoritminin məşhur '3-Point Limit Cycle Oscillation' xüsusiyyətidir, çünki alqoritm hər zaman dP/dV törəməsini yoxlamaq üçün kiçik həyəcanlandırma siqnalı verməyə məcburdur.”"
], title="Addım 2 üçün Danışıq Mətni")

# Step 3
add_styled_heading("Addım 3: P&O və İnkremental Keçiricilik (INC) Müqayisəsi", level=2)
add_p("Nə etməli:", bold=True)
add_p("1. Sol paneldə 'Algorithm' menyusundan 'Compare Both' bəndini seçin.", bullet=True)
add_p("2. '🚀 Run Simulation' düyməsini təkrar basın.", bullet=True)
add_p("3. Aşağıdakı 'Algorithm Comparison' qrafikinə və müqayisə cədvəlinə baxın.", bullet=True)

add_callout([
    "“Burada biz iki böyük sənaye alqoritmini — P&O və Incremental Conductance-ı eyni qrafikdə çarpaz müqayisə edirik.”",
    "“İnkremental Keçiricilik alqoritmi riyazi dI/dV = -I/V şərtini tələb etdiyi üçün MPP nöqtəsində dP/dV = 0 olduqda addımı dondurur. Nəticədə qərarlaşmış vəziyyətdə güc itkisi azalır. Lakin INC daha çox hesablama gücü tələb edir. Cədvəldə hər iki alqoritmin EN 50530 standartı üzrə izləmə səmərəliliyi 99.9%-dən yüksəkdir.”"
], title="Addım 3 üçün Danışıq Mətni")

# Step 4
add_styled_heading("Addım 4: Dinamik Bulud Keçidi (Ssenari: Irradiance Step Down)", level=2)
add_p("Nə etməli:", bold=True)
add_p("1. Sol paneldə 'Scenario' bölməsindən 'Irradiance Step Down' seçin.", bullet=True)
add_p("2. G after change: 600 W/m², Change time: 10.0 s qoyun və simulyasiyanı işə salın.", bullet=True)

add_callout([
    "“İndi isə günəşli günün 10-cu saniyəsində qəfil bulud keçidini simulyasiya edirik (1000-dən 600 Vt/m²-ə ani eniş).”",
    "“Gördüyünüz kimi, 10-cu saniyədə güc dərhal 400 Vt-dan 240 Vt-a düşür. Lakin idarəetmə dövrəmiz çaşqınlığa düşmür; boost çeviricisinin doluluq əmsalını D = 0.44-dən dərhal 0.35-ə uyğunlaşdırır və cəmi 0.15 saniyə ərzində yeni MPP nöqtəsini kilidləyir!”"
], title="Addım 4 üçün Danışıq Mətni")

# Step 5
add_styled_heading("Addım 5: Şah Əsər — Qismən Kölgələnmə Fəlakəti və Çoxzirvəli Əyri (Partial Shading)", level=2)
add_p("Nə etməli:", bold=True)
add_p("1. 'Scenario' menyusundan 'Partial Shading' seçin.", bullet=True)
add_p("2. 3 modul üçün fərqli şüalanma qoyun: Modul 1 = 1000, Modul 2 = 600, Modul 3 = 300 W/m².", bullet=True)
add_p("3. Simulyasiyanı işə salın və 'Partial Shading P-V Curve' qrafikinə baxın.", bullet=True)

add_callout([
    "“Hörmətli müəllim, bu layihənin ən mühüm elmi töhfəsi qismən kölgələnmənin (Partial Shading) aşkarlanmasıdır.”",
    "“Real həyatda bir ağacın və ya binanın kölgəsi silsiləyə düşdükdə baypas diodları aktivləşir və P-V əyrisi tək zirvəli olmaqdan çıxıb 3 fərqli pik nöqtəsi yaradır: 1338 Vt-lıq Qlobal Pik (GMPP) və 790 Vt-lıq Lokal Pik (LMPP-1).”",
    "“Klassik P&O alqoritmi işə düşdükdə ən yaxın lokal təpəyə dırmanır və 790 Vt-da ilişib qalır! Nəticədə 548 Vt enerji — yəni stansiyanın 27.6%-i itirilir! Mən həmçinin tədqiqatımda sübut etdim ki, bu problemin həlli üçün bütün diapazonu skan edən Qlobal MPPT (GMPPT) mexanizmi tətbiq olunmalıdır.”"
], title="Addım 5 üçün Danışıq Mətni (Müəllim üçün ən təsirli hissə)")

# Step 6
add_styled_heading("Addım 6: Mühəndislik Hesabatı və Məlumatların İxracı (Tab 3 və Tab 4)", level=2)
add_p("Nə etməli:", bold=True)
add_p("1. '📋 Metrics & Validation' tabına keçin və 20 mühəndislik yoxlama testini (Sanity Checks) göstərin.", bullet=True)
add_p("2. '💾 Export' tabına keçin və bir kliklə CSV və TXT formatında tam zaman sıralarını yükləyə bildiyinizi nümayiş etdirin.", bullet=True)

add_callout([
    "“Sonuncu iki sekmədə sistem EN 50530 Avropa Standartı üzrə avtomatlaşdırılmış 20 fərqli riyazi və fiziki yoxlama hesabatı təqdim edir: enerjinin saxlanması qanunu, gücün müsbətliyi, qərarlaşma xətası və s. Bütün nəticələri tədqiqat və MATLAB/Excel analizi üçün CSV formatında dərhal yükləmək mümkündür.”"
], title="Addım 6 üçün Danışıq Mətni")

# =========================================================================
# SECTION 3: REAL İSTİFADƏ SAHƏLƏRİ (REAL-WORLD USE CASES)
# =========================================================================
add_styled_heading("3. Real Həyat Tətbiqləri və Sənaye İstifadə Sahələri (Real Use Cases)", level=1)

add_p("Müəllim soruşa bilər: 'Bu simulyasiya və MPPT sistemi sənayedə harada tətbiq olunur?' Aşağıdakı 5 real ssenarini cavab olaraq əminliklə misal çəkin:")

use_cases = [
    ("1. Şəbəkəyə Qoşulan Mərkəzi Günəş Elektrik Stansiyaları (Utility-Scale Solar Farms)",
     "Azərbaycanın Qarabağ və Şərqi Zəngəzur bölgələrində, eləcə də Qobustanda inşa edilən 230 MVt-lıq Qaraçala və Naxçıvan günəş parklarında mərkəzi və simli (string) invertorlar fəaliyyət göstərir. Bu nəhəng stansiyalarda MPPT alqoritminin səmərəliliyinin cəmi 0.5% artması il ərzində yüz minlərlə kilovatt-saat əlavə təmiz enerji və milyonlarla manat iqtisadi qazanc deməkdir."),
    
    ("2. Binaların Damüstü Paylanmış Günəş Sistemləri (Rooftop & C&I Solar)",
     "Yaşayış binalarının və fabriklərin damındakı panellər yaxınlıqdakı bacaların, antenaların və ağacların kölgəsinə məruz qalır. Bizim simulyasiya etdiyimiz Qismən Kölgələnmə (Partial Shading) və Çoxzirvəli GMPP alqoritmləri məhz bu cür damüstü mikro-invertorlarda və optimizatorlarda (məsələn, SolarEdge, Enphase) tətbiq edilir."),
    
    ("3. Günəş Enerjili Elektromobil Doldurma Stansiyaları (Solar EV Charging Hubs)",
     "Elektromobillərin batareyaları birbaşa sabit cərəyan (DC) qəbul edir. Günəş panellərindən gələn enerjini Boost konverter vasitəsilə 400V və ya 800V DC avtomobil batareyasına ötürmək üçün MPPT idarəedicisi şüalanmanın hər anında maksimal gücü avtomobilə ötürür və şəbəkədən asılılığı minimuma endirir."),
    
    ("4. Kənd Təsərrüfatında Günəş Su Nasosları və Aqro-Fotovoltaika (Agri-PV)",
     "Şəbəkədən uzaq aqrar rayonlarda və fermalarda su nasosları sabit tezlikli elektrik xəttinə malik deyil. MPPT çeviriciləri günəş çıxandan batana qədər nasosun mühərrikini ən yüksək hidravlik güc rejimində işlədərək quyulardan suyun fasiləsiz vurulmasını təmin edir."),
    
    ("5. Peyk Enerji Sistemləri və Avtonom Rabitə Qüllələri (Aerospace & Telecom)",
     "Kosmik peyklər Yerin kölgəsinə girib-çıxdıqda panel temperaturu -100°C ilə +100°C arasında kəskin dəyişir. Bizim simulyatorda modelləşdirilən temperatur asılılığı və sürətli INC alqoritmi kosmik aparatların batareyalarının minimal çəki və maksimal faydalı iş əmsalı ilə doldurulması üçün həyati əhəmiyyət kəsb edir.")
]

for title, desc in use_cases:
    add_styled_heading(title, level=2)
    add_p(desc, space_after=6)

# =========================================================================
# SECTION 4: MÜƏLLİMİN VERƏ BİLƏCƏYİ 7 ÇƏTİN SUAL VƏ CAVABLAR
# =========================================================================
add_styled_heading("4. Müəllimin Verə Biləcəyi 7 Çətin Sual və Professional Cavablar (Q&A)", level=1)

add_p("Müdafiə və ya təqdimat zamanı müəllimlər adətən dərindən yoxlamaq üçün bu sualları verirlər. Bu cavabları əzbər deyil, məntiqini dərk edərək söyləyin:")

qa_list = [
    ("Sual 1: Niyə Boost çeviricisində doluluq əmsalını (D) artırdıqda PV gərginliyi azalır?",
     "Cavab:",
     "“Çünki Boost çeviricisinin giriş müqaviməti R_in = R_load * (1 - D)^2 / eta düsturu ilə təyin olunur. D əmsalı artdıqda (1 - D) kəmiyyəti kiçilir, yəni çeviricinin paneldən gördüyü ekvivalent giriş müqaviməti kəskin azalır. Müqavimətin azalması paneldən daha böyük cərəyanın çəkilməsinə və nəticədə panelin I-V əyrisi üzrə sağdan sola sürüşərək terminal gərginliyinin düşməsinə səbəb olur. Məhz buna görə alqoritm gərginliyi qaldırmaq istədikdə D-ni azaltmalı, gərginliyi salmaq istədikdə isə D-ni artırmalıdır.”"),

    ("Sual 2: P&O alqoritmi niyə MPP nöqtəsində dayana bilmir və dalğalanır?",
     "Cavab:",
     "“P&O kor-təbii 'təpəyə dırmanma' (Hill Climbing) prinsipinə əsaslanır. O, MPP-də olub-olmadığını qabaqcadan bilmir. Yeganə yolu gərginliyi bir addım dəyişmək və gücün artıb-azaldığını yoxlamaqdır. MPP nöqtəsində dP/dV = 0 olsa belə, alqoritm növbəti addımı atdıqda dP mənfi olur və o, geri qayıtmaq əmri verir. Nəticədə MPP ətrafında 3 nöqtəli daimi dalğalanma (limit cycle oscillation) yaranır. Bunu aradan qaldırmaq üçün biz tədqiqatımızda 'Deadband' (ölü zona) və ya İnkremental Keçiricilik metodundan istifadə edirik.”"),

    ("Sual 3: İnkremental Keçiriciliyin (INC) P&O-dan əsas riyazi fərqi nədir?",
     "Cavab:",
     "“P&O yalnız son iki ölçmənin fərqinə (delta P) baxır. INC isə gücün gərginliyə görə törəməsini açır: dP/dV = d(V*I)/dV = I + V*(dI/dV). MPP zirvəsində bu törəmə sıfıra bərabər olduğundan dI/dV = -I/V şərti yaranır. Yəni differensial keçiricilik ani keçiriciliyin əksinə bərabər olduqda alqoritm tam MPP nöqtəsində olduğunu anlayır və addım atmağı dayandırır. Buna görə INC sabit rejimdə P&O-dan daha stabildir.”"),

    ("Sual 4: Tənliyi həll edərkən niyə Nyuton-Rafson deyil, Lambert W funksiyasını seçdiniz?",
     "Cavab:",
     "“Tək diodlu fotovoltaik tənlik transsendent tənlikdir — həm xətti, həm də eksponensial hədd eyni vaxtda daxildir. Ənənəvi Nyuton-Rafson iterasiyası kəskin hava dəyişikliklərində və açıq dövrə yaxınlığında dağıla (divergence) və ya 'overflow' xətası verə bilir. Lambert W riyazi funksiyası isə w*exp(w) = x tənliyinin qapalı analitik həllini verir. Bu metod həm 100 dəfə daha sürətlidir, həm də sıfır xəta ilə analitik həll təmin edir.”"),

    ("Sual 5: Qismən kölgələnmədə niyə çoxzirvəli əyri yaranır?",
     "Cavab:",
     "“Ardıcıl qoşulmuş modulların birinin üzərinə kölgə düşdükdə onun generasiya etdiyi cərəyan düşür. Əgər sistemdən tam cərəyan çəkilərsə, kölgəli modul istehlakçıya çevrilib qıza bilər (qaynar nöqtə effekti). Bunun qarşısını almaq üçün modullara paralel anti-paralel baypas diodları qoyulur. Cərəyan kölgəli modulun həddini keçdikdə baypas diodu açılır və cərəyan modulu ötüb keçir. Nəticədə P-V xarakteristikasında hər bir modul qrupunun açılma gərginliyinə uyğun bir neçə lokal pik (LMPP) və yalnız bir Qlobal Pik (GMPP) yaranır.”"),

    ("Sual 6: Simulyasiyanızın doğruluğunu necə sübut edirsiniz?",
     "Cavab:",
     "“Biz simulyasiyamızı beynəlxalq fotovoltaik sənaye standartı olan EN 50530 üzrə test etmişik. Kommersiya tipli Canadian Solar CS3U-400MS modulunun zavod pasport məlumatları ilə simulyasiyanın çıxardığı Voc, Isc, Vmp, Imp və Pmax göstəriciləri 99.8% üst-üstə düşür. Həmçinin 20 fərqli riyazi 'sanity check' ilə enerjinin saxlanması qanununun heç bir zaman addımında pozulmadığı riyazi sübut olunub.”"),

    ("Sual 7: Bulud keçidi zamanı P&O-da yaranan 'çaşqınlıq' (confusion) nədir?",
     "Cavab:",
     "“Əgər alqoritm gərginliyi artırdığı anda təsadüfən günəş şüalanması da kəskin artarsa, delta P müsbət olacaq. Alqoritm elə zənn edəcək ki, gücün artmasına səbəb onun gərginliyi artırmasıdır və gərginliyi daha da artırmağa davam edəcək — yəni MPP-dən uzaqlaşacaq. Bizim tətbiqdə MPPT periodunun (50 ms) düzgün seçilməsi və differensial yoxlama sayəsində bu çaşqınlıq minimuma endirilmişdir.”")
]

for q, a_label, a_text in qa_list:
    add_styled_heading(q, level=3)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    rq = p.add_run(f"{a_label} ")
    rq.font.name = 'Calibri'
    rq.font.size = Pt(10)
    rq.font.bold = True
    rq.font.color.rgb = TEAL
    
    ra = p.add_run(a_text)
    ra.font.name = 'Calibri'
    ra.font.size = Pt(10)
    ra.font.color.rgb = DARK

# =========================================================================
# SECTION 5: TƏQDİMAT ÜÇÜN QIZIL TÖVSİYƏLƏR
# =========================================================================
add_styled_heading("5. Uğurlu Təqdimat Üçün 5 Qızıl Qayda (Məsləhətlər)", level=1)

tips = [
    ("1. Brauzer Pəncərəsini Əvvəlcədən Hazır Saxlayın:",
     "Təqdimata başlamazdan əvvəl brauzerdə https://mppt-simulator.streamlit.app/ linkini açın, internet bağlantısını yoxlayın və pəncərəni tam ekran (F11) rejiminə qoyun."),
    
    ("2. Əvvəlcə Nəticəni Yox, Səbəbi İzah Edin:",
     "Sadəcə 'burada güc 400 Vt oldu' deməyin. 'Biz şüalanmanı 1000 W/m² qoyduğumuz üçün fotocərəyan 10.3 Amperə çatdı və çeviricinin idarəetməsi nəticəsində güc 400.3 Vt-a kilidləndi' formasında səbəb-nəticə əlaqəsi qurun."),
    
    ("3. 'Reset' Düyməsindən Düzgün İstifadə Edin:",
     "Bir ssenaridən digərinə keçərkən sol paneldəki '🔄 Reset' düyməsini sıxaraq əvvəlki nəticələri təmizləyin ki, yeni qrafiklər təmiz görünsün."),
    
    ("4. Rəqəmləri Əminliklə Sitat Gətirin:",
     "400.28 Vt maksimum güc, 99.92% səmərəlilik, 0.302 saniyə qərarlaşma vaxtı, qismən kölgələnmədə 548 Vt itki kimi dəqiq rəqəmlər müəllimdə sizin simulyasiyanı dərindən analiz etdiyiniz təəssüratını yaradır."),
    
    ("5. Özünüzü Proqramçı Kimi Deyil, Enerji Mühəndisi Kimi Təqdim Edin:",
     "Müəllimə proqramlaşdırma dili (Python, Streamlit) barədə yox, sistemin elektrotexniki davranışı (gərginlik, cərəyan, güc, doluluq əmsalı, səmərəlilik və itkilər) haqqında danışın. Kod sadəcə sizin mühəndislik alətinizdir.")
]

for t_title, t_desc in tips:
    add_p(f"• {t_title} {t_desc}", space_after=5)

# Save
out_path = r"C:\Users\ASUS\Desktop\MPPT_Streamlit_Canli_Numayis_ve_Teqdimat_Rehberi.docx"
doc.save(out_path)
print(f"Successfully generated Word document at: {out_path}")
