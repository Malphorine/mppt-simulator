# MPPT Fotovoltaik Sisteminin Modelləşdirilməsi və Simulyasiyası
## Sərbəst İş / Kurs Layihəsi — Tam Təqdimat və Çıxış Bələdçisi (Slide-by-Slide Defense Guide)
**Müəllif:** Həmidov Xalid  
**Təhsil Müəssisəsi:** Azərbaycan Texniki Universiteti (AzTU)  
**Təqdimat Faylı:** `C:\Users\ASUS\Desktop\mppt teqdimat.pptx`  
**Slayd Sayı:** 20 slayd  

---

## Təqdimatın İdarəolunması Üzrə Ümumi Mühəndislik Strategiyası
1. **Vaxt bölgüsü:** Hər slayda orta hesabla 30–50 saniyə vaxt ayırın. Ümumi çıxış müddəti 10–12 dəqiqə olacaqdır.
2. **Çıxışın strukturu:**
   - **Giriş (Slayd 1–3):** Problem nədən ibarətdir, sistem necə işləyir.
   - **Fiziki və Riyazi Modelləşdirmə (Slayd 4–8):** Panelin tənliyi, parametr təyini, ekoloji təsirlər və çeviricinin real itki mexanizmləri.
   - **Alqoritmlərin İdarəetmə Məntiqi (Slayd 9–11):** P&O və Incremental Conductance alqoritmlərinin iş prinsipləri, addım seçimi.
   - **Eksperimentlər və Nəticələr (Slayd 12–18):** Standart rejim, radiasiya sıçrayışları, temperatur artımı, qismən kölgələnmə tələsi və müqayisə.
   - **Etibarlılıq və Yekun (Slayd 19–20):** 20 avtomatik mühəndislik yoxlaması və nəticələr.
3. **Müdafiə qaydası:** Slayddakı mətni sözbəsöz oxumayın. Slayd vizual sübutdur, sizin sözləriniz isə arxadakı mühəndislik məntiqini izah edən mühərrikdir.

---

```
========================================================================================
SLAYD 1: TİTUL SƏHİFƏSİ
========================================================================================
```
### Slaydın Vizual Məzmunu:
- Təhsil müəssisəsi: *Azərbaycan Texniki Universiteti*
- Əsas mövzu: *Fotovoltaik (PV) Sistemlərdə Maksimum Güc Nöqtəsinin İzlənməsi (MPPT) və DC-DC Çeviricinin Modelləşdirilməsi*
- Alt başlıq: *Canadian Solar CS3U-400MS (400W) Paneli, DC-DC Boost Çevirici, P&O və Incremental Conductance Alqoritmlərinin Dinamik və Qismən Kölgələnmə Rejimlərində Müqayisəli Tədqiqi*
- Müəllif: *Həmidov Xalid*

### Çıxış Mətni (Tam nitq):
> "Hörmətli münsiflər heyəti və dəyərli müəllimlər! Hər birinizi salamlayıram.
> 
> Mən Azərbaycan Texniki Universitetinin tələbəsi Həmidov Xalid. Bugünkü tədqiqat və sərbəst işimin mövzusu **'Fotovoltaik Sistemlərdə Maksimum Güc Nöqtəsinin İzlənməsi — yəni MPPT texnologiyası və DC-DC Çeviricinin Modelləşdirilməsi'**dir.
> 
> Layihəmizdə sadələşdirilmiş və ya süni simulyasiya deyil, 400 Vattlıq kommersiya günəş panelinin dəqiq fiziki tək-diodlu modeli qurulmuş, real elektron itkilərə malik DC-DC Boost çeviricisi ilə birləşdirilmiş və iki ən geniş yayılmış MPPT alqoritmi — Perturb & Observe ilə Incremental Conductance alqoritmlərinin dinamik hava və qismən kölgələnmə şəraitindəki performansı müqayisəli tədqiq edilmişdir. İcazənizlə, işin məqsədi və arxitekturası ilə davam edim."

### Müəllimin Olası Sualı və Qısa Cavab:
- **Sual:** *"Niyə məhz MPPT mövzusunu seçmisiniz?"*
- **Cavab:** *"Müəllim, günəş panelləri həm maya dəyəri yüksək olan, həm də faydalı iş əmsalı təbiətən məhdud olan (18–22%) sistemlərdir. Əgər biz MPPT tətbiq etməsək, panelin hasil edə biləcəyi enerjinin 30-40%-i yük uyğunsuzluğuna görə birbaşa itirilir. MPPT stansiyanın iqtisadi və texniki səmərəliliyini təmin edən ən kritik komponentdir."*

---

```
========================================================================================
SLAYD 2: PROBLEM TƏRİFİ VƏ MPPT TEXNOLOGİYASININ ƏHƏMİYYƏTİ
========================================================================================
```
### Slaydın Vizual Məzmunu:
- **Fotovoltaik Panellərin Qeyri-Xətti Təbiəti:**
  - Qeyri-xətti cərəyan-gərginlik xarakteristikası;
  - Tək maksimum nöqtə (MPP);
  - Birbaşa qoşulma itkisi (30–40% azalma);
  - MPPT zərurəti (doluluq əmsalı $D$ vasitəsilə tənzimləmə).
- **Tədqiqatın Məqsəd və Hədəfləri (4 mərhələ):**
  1. Dəqiq fiziki model (SDM və Lambert W);
  2. Güc elektronikası inteqrasiyası (fiziki itkilər);
  3. Alqoritmlərin real izlənməsi (P&O və INC);
  4. Qismən kölgələnmə analizi (GMPP vs LMPP).

### Çıxış Mətni (Tam nitq):
> "Fotovoltaik panellərin ən böyük texniki xüsusiyyəti onların qeyri-xətti daxili təbiətidir. Günəş paneli nə sabit gərginlik mənbəyidir, nə də sabit cərəyan mənbəyi. Hər bir günəş şüalanması və temperatur şəraiti üçün panelin Güc-Gərginlik əyrisində yalnız və yalnız bir dənə optimal işçi nöqtə — Maksimum Güc Nöqtəsi (MPP) mövcuddur.
> 
> Əgər biz günəş panelini birbaşa akkumulyatora və ya rezistiv yükə qoşsaq, işçi nöqtə yükün xətti xarakteristikası ilə məhdudlaşır. Bu zaman hasilat teoretik maksimumdan 30-40% aşağı düşür.
> 
> Bu problemin həlli üçün qarşımıza 4 əsas hədəf qoyduq:
> Birincisi, paneli Lambert W analitik həlli ilə 100% rəqəmsal dayanıqlı modelləşdirmək;
> İkincisi, güc çeviricisinin drossel, tranzistor və diod itkilərini hesaba qatmaq;
> Üçüncüsü, klassik P&O və Incremental Conductance alqoritmlərini diskret zaman addımı ilə sıfırdan proqramlaşdırmaq;
> Və dördüncüsü, qismən kölgələnmə zamanı yaranan çoxzirvəli əyridə ənənəvi alqoritmlərin lokal tələyə düşmə riskini eksperimental olaraq sübut etmək."

### Müəllimin Olası Sualı və Qısa Cavab:
- **Sual:** *"Birbaşa qoşulma itkisi haradan yaranır?"*
- **Cavab:** *"Ohm qanununa görə yükün tələb etdiyi $V/I$ nisbəti panelin MPP nöqtəsindəki $V_{mp}/I_{mp}$ optimal daxili empedansına bərabər gəlmir. Nəticədə panel ya aşağı gərginlik rejimində ilişir, ya da cərəyanı kəskin məhdudlaşır."*

---

```
========================================================================================
SLAYD 3: SİSTEM ARXİTEKTURASI VƏ ENERJİ ÇEVRİLMƏ ZƏNCİRİ
========================================================================================
```
### Slaydın Vizual Məzmunu:
- **Tam Qapalı Əks-Əlaqəli Sistem Dövrəsi Diaqramı:**
  - PV Modul (Canadian Solar 400W) $\rightarrow$ DC-DC Boost Çevirici $\rightarrow$ Elektrik Yükü ($20\ \Omega$);
  - MPPT Kontrolleri ($V_{pv}, I_{pv}$ ölçməsi $\rightarrow$ PWM Doluluq Əmsalı $D$).
- **Siqnal Axını və Mərhələlər:** 50 ms ölçmə dövrü, güc analizi, $D$ siqnalının ötürülməsi.
- **Empedans Uyğunlaşdırma Qanunu:** $R_{\mathrm{gir},\mathrm{eff}} = R_{\mathrm{y\ddot{u}k}} \cdot \frac{(1 - D)^2}{\eta}$.

### Çıxış Mətni (Tam nitq):
> "Bu slaydda qurduğumuz simulyasiya sisteminin tam qapalı idarəetmə arxitekturasını görürsünüz. Zəncir 4 əsas blokdan təşkil olunub.
> 
> Birinci blok enerjini generasiya edən günəş panelidir. İkinci blok gərginliyi artıran DC-DC Boost çeviricisidir. Üçüncü blok enerji istehlakçısı olan elektrik yüküdür. Dördüncü blok isə bütün bu zənciri idarə edən MPPT kontrolleridir.
> 
> Sistem belə işləyir: Kontroller paneldən gərginlik və cərəyanı hər 50 millisaniyədən bir oxuyur. Güc dəyişimini analiz edir və çeviriciyə yeni $D$ doluluq əmsalı göndərir.
> 
> Bəs doluluq əmsalı panelin gücünü necə idarə edir? Aşağıda gördüyünüz empedans uyğunlaşdırma qanununa əsasən: Boost çeviricisi panelin çıxışına $R_{\mathrm{gir},\mathrm{eff}}$ effektiv müqaviməti göstərir. Biz $D$ əmsalını artırdıqda effektiv müqavimət azalır və panel gərginliyi düşür; $D$-ni azaltdıqda isə effektiv müqavimət artır və panel gərginliyi qalxır. Yəni kontroller $D$ parametrini tənzimləməklə panelin işçi nöqtəsini Güc-Gərginlik əyrisi boyunca istədiyi yerə hərəkət etdirə bilir."

---

```
========================================================================================
SLAYD 4: FOTOVOLTAİK MODULUN TƏK DİODLU 5-PARAMETRLİ MODELİ (SDM)
========================================================================================
```
### Slaydın Vizual Məzmunu:
- **Dövrə Tənliyi:**
  $$I = I_{ph} - I_0 \cdot \left[ \exp\left(\frac{V + I \cdot R_{\mathrm{ard}}}{n \cdot N_s \cdot V_t}\right) - 1 \right] - \frac{V + I \cdot R_{\mathrm{ard}}}{R_{\mathrm{par}}}$$
- **Fiziki Parametrlər:**
  - $I_{ph}$ (fotocərəyan), $I_0$ (tərs doyma cərəyanı), $R_{\mathrm{ard}}$ (ardıcıl müqavimət), $R_{\mathrm{par}}$ (paralel sızma müqaviməti), $n$ (ideallıq əmsalı = 1.10), $N_s$ (ardıcıl elementlər = 72).
  - Termal gərginlik: $V_t = \frac{k_B \cdot T}{q} \approx 25.69\ \text{mV}$ ($25^\circ\text{C}$).
- **Lambert W Analitik Həlli:**
  - Nyuton-Rafsonun divergensiya çatışmazlığı;
  - Lambert W $W_0$ əsas budağı ilə analitik həll;
  - Log-domain asimptotik genişlənməsi ilə sıfır hesablama daşması (zero overflow).

### Çıxış Mətni (Tam nitq):
> "Panelin simulyasiyasında beynəlxalq elmi ədəbiyyatda qızıl standart sayılan **Tək Diodlu 5-Parametrli Model (SDM)** tətbiq edilmişdir.
> 
> Slayddakı dövrə tənliyinə diqqət yetirsək, cərəyan həm tənliyin sol tərəfində, həm də sağ tərəfdə eksponentin daxilində və müqavimət hədlərində yer alır. Bu tənlik transsendentdir, yəni adi cəbri üsulla $I$-ni bir tərəfə keçirmək mümkün deyil.
> 
> Əksər tələbə və mühəndislik işlərində bunu sadəcə Nyuton-Rafson iterasiyası ilə həll edirlər. Lakin Nyuton-Rafson metodu açıq dövrə yaxınlığındakı kəskin döngələrdə və ya ani sıçrayışlarda rəqəmsal divergensiyaya uğrayır, yəni həll tapa bilmir və proqram çökür.
> 
> Biz bu problemi kökündən həll etmək üçün tənliyi xüsusi riyazi aparat olan **Lambert W funksiyası** vasitəsilə qapalı analitik formaya gətirdik. Böyük eksponentlər üçün log-domain asimptotik yaxınlaşması yazdıq. Nəticədə simulyasiyamızda heç bir iterativ ilişmə, NaN və ya sonsuzluq (overflow) xətası yoxdur; model 100% riyazi dəqiqliklə analitik həll olunur."

---

```
========================================================================================
SLAYD 5: REFERANS KOMMERSİYA MODULU: CANADIAN SOLAR CS3U-400MS (400W)
========================================================================================
```
### Slaydın Vizual Məzmunu:
- **Standart Test Şəraiti (STC: $G = 1000\ \text{W/m}^2$, $T = 25^\circ\text{C}$):**
  - Nominal Güc ($P_{\mathrm{max}}$): $400.33\ \text{W}$
  - Optimal Gərginlik ($V_{\mathrm{mp}}$): $40.99\ \text{V}$
  - Optimal Cərəyan ($I_{\mathrm{mp}}$): $9.77\ \text{A}$
  - Açıq Dövrə Gərginliyi ($V_{\mathrm{oc}}$): $48.61\ \text{V}$
  - Qısa Qapanma Cərəyanı ($I_{\mathrm{sc}}$): $10.33\ \text{A}$
  - Daxili Ardıcıl Müqavimət ($R_{\mathrm{ard}}$): $0.15\ \Omega$
  - Daxili Paralel Müqavimət ($R_{\mathrm{par}}$): $650.0\ \Omega$
  - Diod İdeallıq Əmsalı ($n$): $1.10$
  - Temperatur Əmsalları: $\alpha = +0.05\ \%/^\circ\text{C}$, $\beta = -0.29\ \%/^\circ\text{C}$
- **Qrafik:** Modulun STC şəraitində I-V və P-V xarakteristika əyrisi.
- **Model Dəqiqliyi:** Teoretik xəta 0.1%-dən kiçikdir.

### Çıxış Mətni (Tam nitq):
> "Modelin doğruluğunu yoxlamaq üçün sənayedə real tətbiq olunan monokristallik **Canadian Solar CS3U-400MS** panelini baza götürdük.
> 
> Standart laboratoriya test şəraitində — yəni 1000 Vatt/kvadrat radiasiya və 25 dərəcə temperaturda bu panelin maksimum gücü 400.33 Vatt-dır. Optimal nöqtədə gərginlik 41 Volt, cərəyan 9.8 Amper təşkil edir. Açıq dövrə gərginliyi 48.6 Volt, qısa qapanma cərəyanı isə 10.33 Amperdir.
> 
> Sağdakı qrafikdə panelin cərəyan-gərginlik əyrisi əks olunub. Qırmızı nöqtə ilə qısa qapanma cərəyanı, yaşıl nöqtə ilə açıq dövrə gərginliyi işarələnib.
> 
> Modelimizin hesabladığı nəticələrlə istehsalçının rəsmi texniki pasportu (datasheet) arasında fərq 0.1%-dən də az olmuşdur. Bu fakt qurduğumuz SDM modelinin real fiziki prosesləri tam dəqiqliklə əks etdirdiyini nümayiş etdirir."

---

```
========================================================================================
SLAYD 6: ƏTRAF MÜHİTİN TƏSİRİ: GÜNƏŞ RADİASİYASININ (G) DƏYİŞMƏSİ
========================================================================================
```
### Slaydın Vizual Məzmunu:
- **Fotocərəyan Düsturu:** $I_{ph}(G, T) = \frac{G}{G_0} \cdot [I_{ph,0} + \alpha_{sc} \cdot (T - T_0)]$
- **Fiziki Qanunauyğunluqlar:**
  - Fotocərəyan şüalanma ilə düz mütənasibdir ($G$ 1000-dən $200\ \text{W/m}^2$-ə düşdükdə $I \approx 10.3\ \text{A} \rightarrow 2.0\ \text{A}$);
  - Açıq dövrə gərginliyi loqarifmik asılılıqla çox az dəyişir ($\propto \ln(G/G_0)$);
  - MPP gücü şüalanmaya mütənasib olaraq $400\ \text{W} \rightarrow 80\ \text{W}$-a enir.
- **Qrafiklər:** Müxtəlif şüalanma səviyyələrində I-V və P-V əyriləri ailəsi ($200, 400, 600, 800, 1000\ \text{W/m}^2$).

### Çıxış Mətni (Tam nitq):
> "Təbiətdə günəş radiasiyası daim sabit qalmır. Bu slaydda şüalanmanın dəyişməsinin panellərə necə təsir etdiyini görürük.
> 
> Tənlikdən aydın olur ki, fotocərəyan ($I_{ph}$) günəş şüalanması ilə birbaşa düz mütənasibdir. Əgər radiasiya 1000-dən 200 Vatt/kvadrata düşərsə, cərəyan da təxminən 5 dəfə azalaraq 10.3 Amperdən 2 Amperə enir.
> 
> Lakin gərginlik cərəyandan fərqli olaraq şüalanmadan loqarifmik asılıdır. Yəni günəş zəifləyəndə gərginlik cəmi 2–3 Volt azalır, əsas itki cərəyanda baş verir.
> 
> Nəticədə, P-V qrafiklərində gördüyünüz kimi, pik güc 400 Vatt-dan birbaşa 80 Vatt-a qədər yuvarlanır. Bu təhlil sübut edir ki, günəş azalan zaman MPPT kontrolleri gərginliyi kəskin dəyişməməli, əsas diqqəti azalan cərəyana uyğun empedansı dəyişməyə yönəltməlidir."

---

```
========================================================================================
SLAYD 7: ƏTRAF MÜHİTİN TƏSİRİ: TEMPERATURUN (T) PANELİN GÜCÜNƏ TƏSİRİ
========================================================================================
```
### Slaydın Vizual Məzmunu:
- **Tərs Doyma Cərəyanı Tənliyi:**
  $$I_0(T) = I_{0,0} \cdot \left(\frac{T}{T_0}\right)^3 \cdot \exp\left[\frac{q}{k_B} \left(\frac{E_{g,0}}{T_0} - \frac{E_g(T)}{T}\right)\right]$$
- **Termal Deqradasiya Mexanizmləri:**
  - Qadağan zonasının ($E_g$) daralması;
  - Tərs doyma cərəyanının ($I_0$) kubik və eksponensial artımı;
  - $V_{\mathrm{oc}}$ gərginliyinin hər dərəcədə $-0.29\%$ azalması;
  - $55^\circ\text{C}$-də gücün $400\ \text{W}$-dan $335\ \text{W}$-a düşməsi.
- **Qrafik:** Temperatur artımı ($15^\circ\text{C} \rightarrow 55^\circ\text{C}$) zamanı P-V əyrilərinin sola sürüşməsi.

### Çıxış Mətni (Tam nitq):
> "İkinci ən mühüm iqlim parametri modulun temperaturudur. İnsanlarda belə bir yanlış təsəvvür var ki, hava nə qədər isti olsa, günəş paneli o qədər çox enerji verər. Fiziki qanunlar isə tam əksini sübut edir.
> 
> Panel qızdıqca silisium yarımkeçiricisinin qadağan olunmuş zonası daralır və ekranda gördüyünüz tənliyə əsasən diodun sızma cərəyanı ($I_0$) həm kubik, həm də eksponensial olaraq kəskin yüksəlir.
> 
> Bu sızma cərəyanının artması panelin açıq dövrə gərginliyini hər dərəcə istilik artımında 0.29% azaldır. Qrafikə baxsanız, temperatur 15 dərəcədən 55 dərəcəyə qalxdıqda güc əyrisinin təpəsi 400 Vatt-dan 335 Vatt-a enir və sola doğru sürüşür.
> 
> Yəni yay aylarında panellərin qızması hasilatı təbii olaraq 15–20% aşağı salır. MPPT kontrolleri bu termal sürüşməni vaxtında hiss edib doluluq əmsalını tənzimləməsə, əlavə güc itkiləri qaçılmaz olar."

---

```
========================================================================================
SLAYD 8: DC-DC BOOST ÇEVİRİCİSİ: FİZİKİ İTKİ VƏ DİNAMİK MODEL
========================================================================================
```
### Slaydın Vizual Məzmunu:
- **Gərginlik Ötürməsi:** $V_{\mathrm{c\imath x}} = \frac{V_{\mathrm{gir}}}{1 - D} \cdot \eta$
- **Fiziki İtki Mexanizmləri (Tam Equation Bloku):**
  1. Drossel sarğı itkisi: $P_L = I_{\mathrm{gir}}^2 \cdot R_L \quad (R_L = 0.05\ \Omega)$
  2. MOSFET keçid itkisi: $P_{\mathrm{FET}} = I_{\mathrm{gir}}^2 \cdot D \cdot R_{\mathrm{ds}} \quad (R_{\mathrm{ds}} = 0.02\ \Omega)$
  3. Çıxış diodunun güc itkisi: $P_{\mathrm{diod}} = I_{\mathrm{c\imath x}} \cdot V_{\mathrm{diod}} \quad (V_{\mathrm{diod}} = 0.7\ \text{V})$
  4. Kommutasiya itkisi: $P_{\mathrm{kom}} \approx \frac{1}{2} \cdot V_{\mathrm{c\imath x}} \cdot I_{\mathrm{gir}} \cdot (t_r + t_f) \cdot f_{\mathrm{sw}} \quad (f_{\mathrm{sw}} = 50\ \text{kHz})$
  5. Tam itki və Səmərəlilik: $\Sigma P_{\mathrm{itki}} = P_L + P_{\mathrm{FET}} + P_{\mathrm{diod}} + P_{\mathrm{kom}}, \quad \eta_{\mathrm{conv}} = 1 - \frac{\Sigma P_{\mathrm{itki}}}{P_{\mathrm{gir}}} \approx 97.5\% - 98.2\%$
- **Dinamik Filtrasiya və Təhlükəsizlik:**
  - LC Süzgəc dinamikası ($\tau = 2\ \text{ms}$, $L = 100\ \mu\text{H}$, $C = 470\ \mu\text{F}$);
  - Doluluq əmsalı limitləri: $D \in [0.05, 0.90]$;
  - Enerjinin saxlanması qanunu: $P_{\mathrm{c\imath x}} \leq P_{\mathrm{gir}} - P_{\mathrm{itki}}$ (100% təmin edilir).

### Çıxış Mətni (Tam nitq):
> "Layihəmizin ən güclü mühəndislik aspektlərindən biri DC-DC Boost çeviricisinin modelləşdirilməsidir. Əksər simulyasiyalarda çeviriciyə sadəcə ideal $V_{\mathrm{c\imath x}} = V_{\mathrm{gir}} / (1 - D)$ düsturu kimi baxırlar. Biz isə real güc elektronikası dövrəsinin bütün daxili itkilərini fiziki tənliklərlə hesaba qatdıq.
> 
> Slayddakı tənliklərə diqqət yetirsək, 4 fərqli itki nəzərə alınıb:
> 1. Drosselin mis sarğısında yaranan omik itki ($P_L$);
> 2. MOSFET tranzistorunun daxili kanal müqavimətindəki keçiricilik itkisi ($P_{\mathrm{FET}}$);
> 3. Çıxış diodunun 0.7 Voltluq p-n keçid gərginlik düşgüsü itkisi ($P_{\mathrm{diod}}$);
> 4. Və 50 kilohets kommutasiya tezliyində açılıb-bağlanma zamanı yaranan dinamik keçid itkisi ($P_{\mathrm{kom}}$).
> 
> Bu hesablamalar nəticəsində çeviricimizin real faydalı iş əmsalı 97.5% ilə 98.2% arasında təyin edilmişdir.
> 
> Sağ tərəfdə isə LC süzgəcinin birinci tərtib aperiodik dinamikası modelləşdirilib. Yəni idarəetmə dəyişən kimi gərginlik sıçramır, 2 millisaniyəlik zaman sabiti ilə hamar keçid edir. Doluluq əmsalı isə induktorun doymasını və qısa qapanmanı önləmək üçün 0.05 ilə 0.90 arasında sərt məhdudlaşdırılmışdır."

---

```
========================================================================================
SLAYD 9: MPPT ALQORİTMİ 1: PERTURB & OBSERVE (P&O)
========================================================================================
```
### Slaydın Vizual Məzmunu:
- **P&O Qərar Alqoritmi (Equation Bloku):**
  - Güc hesabatı: $P(k) = V(k) \cdot I(k)$, $\Delta P = P(k) - P(k-1)$, $\Delta V = V(k) - V(k-1)$
  - Qərar qaydaları:
    - $\Delta P > 0 \land \Delta V > 0 \Longrightarrow D(k) = D(k-1) - \Delta D$ (Gərginliyi artır)
    - $\Delta P > 0 \land \Delta V < 0 \Longrightarrow D(k) = D(k-1) + \Delta D$ (Gərginliyi azalt)
    - $\Delta P < 0 \land \Delta V > 0 \Longrightarrow D(k) = D(k-1) + \Delta D$ (İstiqaməti dəyiş)
    - $\Delta P < 0 \land \Delta V < 0 \Longrightarrow D(k) = D(k-1) - \Delta D$ (İstiqaməti dəyiş)
- **Boost Çeviricidə Qütblük və Addım Kompromisi:**
  - $D$ artdıqda $V_{pv}$ azalır (tərs qütblük məntiqi);
  - Böyük $\Delta D$ vs Kiçik $\Delta D$ kompromisi;
  - Seçilmiş parametr: $\Delta D = 0.005$ ($0.3\ \text{s}$ sürətli yaxınlaşma və cəmi $0.36\ \text{W}$ dalğalanma).

### Çıxış Mətni (Tam nitq):
> "İndi isə tətbiq etdiyimiz birinci MPPT alqoritminə — **Perturb & Observe**, yəni 'Həyəcanlandır və Müşahidə et' metoduna baxaq. Bu alqoritm sənayedə ən populyar 'təpəyə dırmanma' metodudur.
> 
> Məntiqi çox aydındır: Kontroller hər dövrdə gücü hesablayır və əvvəlki dövrlə müqayisə edir ($\Delta P$). Əgər güc artıbsa, deməli atdığımız addım düzgün istiqamətdədir və eyni tərəfə addımlayırıq. Əgər güc azalıbsa, deməli pik nöqtəsini keçmişik və ya səhv tərəfə getmişik; dərhal istiqaməti tərsinə çeviririk.
> 
> Burada çox vacib bir güc elektronikası incəliyi var: Boost çeviricidə $D$ artanda panel gərginliyi azalır! Yəni ötürmə xarakteristikası tərsinədir. Alqoritmdə bu qütblük nəzərə alınmasa, sistem pikə deyil, birbaşa sıfıra yuvarlanar.
> 
> İkinci kritik mühəndislik məsələsi addım ölçüsüdür ($\Delta D$). Əgər addımı böyük götürsək, sistem pikə tez çatar, lakin pik nöqtəsində çox böyük ossilyasiya itkisi verər. Əgər addımı çox kiçik götürsək, dalğalanma olmaz, amma bulud gələndə reaksiya verə bilməz.
> 
> Biz riyazi optimallaşdırma apararaq addım ölçüsünü $\Delta D = 0.005$ seçdik. Nəticədə həm 0.3 saniyə kimi çox yüksək sürət, həm də cəmi 0.36 Vattlıq inanılmaz dərəcədə kiçik dalğalanma əldə etdik."

---

```
========================================================================================
SLAYD 10: MPPT ALQORİTMİ 2: INCREMENTAL CONDUCTANCE (INC)
========================================================================================
```
### Slaydın Vizual Məzmunu:
- **Riyazi Törəmə Şərti:**
  $$\frac{dP}{dV} = \frac{d(V \cdot I)}{dV} = I + V \cdot \frac{dI}{dV} = 0 \quad \Longrightarrow \quad \frac{dI}{dV} = -\frac{I}{V}$$
- **Qərar Qaydaları:**
  - $\frac{dI}{dV} = -\frac{I}{V} \implies \frac{dP}{dV} = 0 \implies \Delta D = 0$ (Dəqiq MPP! Addım atılmır, sıfır dalğalanma)
  - $\frac{dI}{dV} > -\frac{I}{V} \implies \frac{dP}{dV} > 0 \implies \Delta D < 0$ (MPP-dən soldayıq, $V$ artırılır)
  - $\frac{dI}{dV} < -\frac{I}{V} \implies \frac{dP}{dV} < 0 \implies \Delta D > 0$ (MPP-dən sağdayıq, $V$ azaldılır)
- **P&O ilə Müqayisədə Üstünlükləri:**
  1. Qərarlaşmış rejimdə sıfır yellənmə;
  2. Dinamik hava şəraitində səhvsiz istiqamət təyini;
  3. Bölmə və törəmə tələb etdiyi üçün bir qədər yüksək hesablama tələbi.

### Çıxış Mətni (Tam nitq):
> "İkinci alqoritmimiz daha mürəkkəb riyazi bünövrəyə malik olan **Incremental Conductance — Diferensial Keçiricilik** metodudur.
> 
> Bu alqoritm kor-təbii dırmanmır, birbaşa riyazi törəməyə əsaslanır. Gücün gərginliyə görə törəməsini açsaq: $\frac{dP}{dV} = I + V \cdot \frac{dI}{dV}$. P-V əyrisinin təpə zirvəsində törəmə sıfır olmalıdır! Bu bərabərlikdən alırıq ki, diferensial keçiricilik ani keçiriciliyin mənfisinə bərabər olduqda ($\frac{dI}{dV} = -\frac{I}{V}$), sistem DƏQİQ pik nöqtəsindədir.
> 
> Bu metodun P&O-dan iki böyük üstünlüyü var:
> Birincisi, P&O pikə çatanda belə dayana bilmir, 3 nöqtə ətrafında sağa-sola yellənir. INC isə törəmənin sıfır olduğunu görən kimi addım atmağı dayandırır və sıfır dalğalanma ilə sabit qalır.
> İkincisi, qəfil bulud gələndə P&O güc artımını gərginlik dəyişməsi ilə səhv salıb tərs istiqamətə qaça bilər. INC isə cərəyanın törəməsini izlədiyi üçün heç vaxt aldanmır.
> 
> Yeganə kompromis odur ki, INC alqoritmi hər dövrdə bölmə və diferensial hesabladığı üçün mikrokontrollerdən daha güclü hesablayıcı arxitektura tələb edir."

---

```
========================================================================================
SLAYD 11: SİMULYASİYA MÜHƏRRİKİ VƏ MÜSTƏQİL DOĞRULAMA
========================================================================================
```
### Slaydın Vizual Məzmunu:
- **Zaman Sahəsində Diskret Modelləşdirmə:**
  - $dt = 0.001\ \text{s}$ (1 ms çevirici və yük inteqrasiya addımı);
  - $T_{\mathrm{mppt}} = 0.050\ \text{s}$ (50 ms / 20 Hz MPPT kontroller seçmə dövrü);
  - Bütün parametrlərin pandas DataFrame-də real vaxt qeydiyyatı.
- **Müstəqil Ground-Truth Metodologiyası:**
  - *"No Lookahead"* Qaydası (kontroller teoretik piki bilmir, yalnız $V$ və $I$ ölçməsi ilə idarə edir);
  - Mühərrikin paralel ideal MPP hesabatı;
  - İzləmə səmərəliliyi düsturu: $\eta_{\mathrm{MPPT}} = \frac{P_{\mathrm{izlenen}}}{P_{\mathrm{teoretik}}} \times 100\%$.

### Çıxış Mətni (Tam nitq):
> "Bütün bu modelləri reallaşdırmaq üçün Python mühitində sıfırdan diskret zaman simulyasiya mühərriki proqramlaşdırdıq.
> 
> Mühərrik iki-pilləli zaman mexanizmi ilə işləyir: DC-DC çevirici, drossel və kondensator dinamikası hər 1 millisaniyədən bir differensial inteqrasiya edilir; MPPT kontrolleri isə sənaye mikrokontrollerlərinin tezliyinə uyğun olaraq hər 50 millisaniyədən bir, yəni 20 Hers tezliklə işə düşür.
> 
> Tədqiqatımızın elmi dürüstlüyü üçün ən əsas prinsipimiz **'No Lookahead' — Gələcəyi Görməmək** qaydası oldu. Yəni kontroller heç vaxt sistemin o andakı teoretik maksimum gücünü qabaqcadan bilmir. O, xəritəsiz hərəkət edir, yalnız sensorlardan gələn $V$ və $I$ qiymətlərinə baxır.
> 
> Simulyasiya mühərriki isə arxa planda müstəqil olaraq hər millisaniyə üçün fiziki ideal piki hesablayır və kontrollerin faktiki hasil etdiyi gücü teoretik gücə bölərək izləmə səmərəliliyini qərəzsiz şəkildə qeydə alır."

---

```
========================================================================================
SLAYD 12: EKSPERİMENT 1: STANDART ŞƏRAİTDƏ (STC) SİMULYASİYA NƏTİCƏLƏRİ
========================================================================================
```
### Slaydın Vizual Məzmunu:
- **Rəqəmsal Nəticələr (STC: $1000\ \text{W/m}^2$, $25^\circ\text{C}$):**
  - İzlənən Faktiki Güc: $400.01\ \text{W}$ (Teoretik: $400.33\ \text{W}$);
  - İzləmə Səmərəliliyi: **$99.92\%$**;
  - Qərarlaşma Müddəti: **$0.302\ \text{s}$**;
  - Çevirici Səmərəliliyi: **$98.16\%$**;
  - Qərarlaşmış Doluluq Əmsalı: $D = 0.5500$.
- **Qərarlaşmış Vəziyyət Dəqiqliyi:**
  - Gərginlik xətası: $0.37\%$ ($40.83\ \text{V}$ vs $40.99\ \text{V}$);
  - Cərəyan xətası: $0.30\%$ ($9.80\ \text{A}$ vs $9.77\ \text{A}$);
  - Güc xətası: Cəmi $0.08\%$ ($0.31\ \text{W}$).
- **Qrafik:** 6 panelli tam simulyasiya idarəetmə paneli (Dashboard).

### Çıxış Mətni (Tam nitq):
> "İndi isə əldə etdiyimiz eksperimental nəticələrə keçək. Birinci eksperimentdə sistem standart sınaq şəraitində — yəni 1000 Vatt/kvadrat və 25 dərəcədə sınaqdan keçirildi.
> 
> Nəticələr rəqəmsal olaraq heyranedicidir: Teoretik maksimum güc 400.33 Vatt olduğu halda, kontrollerimiz 400.01 Vatt gücü tam şəkildə izləyərək hasil etdi. İzləmə səmərəliliyi **99.92%** təşkil etmişdir.
> 
> Sistem başlanğıc vəziyyətindən cəmi **0.302 saniyə** ərzində qərarlaşmış rejimə keçir. Qərarlaşmış rejimdə güc xətası cəmi 0.31 Vatt, yəni 0.08%-dir. Gərginlik və cərəyan xətaları isə 0.3%-in altındadır.
> 
> Çeviricimiz real itkilərə baxmayaraq 98.16% səmərəliliklə işləmiş və doluluq əmsalı $D = 0.5500$ nöqtəsində sabitləşmişdir. Sağdakı 6 panelli idarəetmə panelində gərginlik, cərəyan, güc və doluluq əmsalının zamana görə hamar davranışı aydın görünür."

---

```
========================================================================================
SLAYD 13: EKSPERİMENT 1: P&O ALQORİTMİNİN ADDIM-ADDIM YAXINLAŞMASI
========================================================================================
```
### Slaydın Vizual Məzmunu:
- **Yaxınlaşma Xronologiyası:**
  - Başlanğıc: $D_{\mathrm{init}} = 0.50$ nöqtəsi;
  - Sürətli Qalxma: Cəmi 6 addımda ($\sim 0.3\ \text{s}$) $350\ \text{W} \rightarrow 400\ \text{W}$;
  - Qərarlaşma: $0.302\ \text{s}$ sonra $\pm 0.36\ \text{W}$ kənarlaşma ilə sabit kilidlənmə;
  - Bütün simulyasiya boyu orta effektivlik: **$99.85\%$**.
- **Qrafiklər:** Gücün zamana görə trayektoriyası və P-V əyrisi üzərində işçi nöqtənin addım-addım təpəyə dırmanması.

### Çıxış Mətni (Tam nitq):
> "Bu slaydda P&O alqoritminin başlanğıcdan pik nöqtəyə necə addımladığının mikroskopik təhlili verilib.
> 
> Sistem işə düşərkən təhlükəsiz başlanğıc nöqtəsi kimi $D = 0.50$ seçilmişdir. Həmin anda güc 350 Vatt civarında idi. Kontroller işə düşən kimi hər 50 millisaniyədən bir addım ataraq cəmi 6 addım ərzində — yəni təxminən 0.3 saniyədə gücü 350-dən 400 Vatt-a qaldırır.
> 
> Sağdakı qrafikə baxsanız, mavi xətt işçi nöqtənin P-V əyrisi boyunca yuxarıya necə səliqəli dırmandığını göstərir. Zirvəyə çatdıqdan sonra alqoritm təpə ətrafında cəmi $\pm 0.36$ Vattlıq mikroskopik dalğalanma ilə kilidlənir.
> 
> Beləliklə, ilk saniyədəki keçid prosesini də daxil etsək belə, bütün simulyasiya boyunca orta izləmə səmərəliliyi 99.85% olmuşdur."

---

```
========================================================================================
SLAYD 14: EKSPERİMENT 2 & 3: RADİASİYA SIÇRAYIŞLARI (BULUDUN GƏLMƏSİ VƏ ÇƏKİLMƏSİ)
========================================================================================
```
### Slaydın Vizual Məzmunu:
- **Dinamik Adaptasiya Ssenariləri:**
  1. Radiasiyanın Qəfil Düşməsi ($1000 \rightarrow 700\ \text{W/m}^2$ @ $t = 10\ \text{s}$):
     - Güc sıçrayışla $400\ \text{W} \rightarrow 280\ \text{W}$-a enir;
     - Kontroller çaşmır, dərhal yeni MPP-yə adaptasiya olur;
     - İzləmə səmərəliliyi: **$99.94\%$**.
  2. Radiasiyanın Qəfil Qalxması ($700 \rightarrow 1000\ \text{W/m}^2$ @ $t = 10\ \text{s}$):
     - Günəş qəfil parladıqda bərpa müddəti cəmi **$0.152\ \text{s}$** təşkil edir.
- **Qrafiklər:** Hər iki eksperiment üçün güc izlənməsi və qırmızı qırıq xətlə göstərilən teoretik MPP-yə tam üst-üstə düşmə.

### Çıxış Mətni (Tam nitq):
> "Stasionar şəraitdən sonra alqoritmləri ən çətin sınaqlardan biri — kəskin hava dəyişikliyi qarşısında yoxladıq.
> 
> İkinci eksperimentdə günəşli havada hərəkət edən qatı bulud simulyasiya edildi: 10-cu saniyədə radiasiya anidən 1000-dən 700 Vatt/kvadrata düşür. Qrafikdə gördüyünüz kimi, güc dərhal 400 Vatt-dan 280 Vatt-a enir. Ən vacib məqam odur ki, kontroller istiqamətini itirmədi, heç bir yalançı addım atmadan yeni 280 Vattlıq pik nöqtəsini dərhal yaxaladı və səmərəliliyi 99.94%-də saxladı.
> 
> Üçüncü eksperimentdə isə əks proses sınaqdan keçirildi: bulud çəkilir və günəş parlayır (700-dən 1000-ə sıçrayış). Sistem cəmi 0.152 saniyə ərzində — yəni cəmi 3 addımda tam olaraq 400 Vattlıq yeni zirvəyə kökləndi.
> 
> Bu eksperimentlər seçdiyimiz $\Delta D = 0.005$ addımının dinamik hava sıçrayışlarında tam dayanıqlı olduğunu təsdiqləyir."

---

```
========================================================================================
SLAYD 15: EKSPERİMENT 4 & 5: TERMAL İSTİLİK ARTIMI VƏ MÜRƏKKƏB HAVA SSENARİSİ
========================================================================================
```
### Slaydın Vizual Məzmunu:
- **Eksperiment 5: Kombinə Dəyişən Şərait:**
  - $t = 10\ \text{s}$: Radiasiya $1000 \rightarrow 700\ \text{W/m}^2$ düşür;
  - $t = 15\ \text{s}$: Temperatur $25^\circ\text{C} \rightarrow 40^\circ\text{C}$-yə yüksəlir.
- **Nəticələr:**
  - Orta İzləmə Səmərəliliyi: **$99.94\%$**;
  - Qərarlaşmış Xəta: Cəmi **$0.23\ \text{W}$**;
  - Termal gərginlik düşgüsünə ($41\ \text{V} \rightarrow 37\ \text{V}$) baxmayaraq kontroller paneli optimal nöqtədə saxlayır.
- **Qrafik:** Kombinə ssenarinin 6 panelli dashboard qrafiki.

### Çıxış Mətni (Tam nitq):
> "Real təbiətdə təkcə günəş deyil, temperatur da eyni vaxtda dəyişir. Buna görə 5-ci eksperimentdə mürəkkəb kombinə ssenari qurduq:
> 
> 10-cu saniyədə bulud gəlir (radiasiya 1000-dən 700-ə düşür), 15-ci saniyədə isə külək kəsilir və panelin temperaturu 25-dən 40 dərəcəyə yüksəlir.
> 
> Qrafiklərə diqqət yetirsəniz, 15-ci saniyədə temperatur artdıqca panelin gərginliyi 41 Volt-dan 37 Volt-a doğru enməyə başlayır. Lakin MPPT nəzarətçisi dərhal çeviricinin doluluq əmsalını azaldaraq daxili empedansı tənzimləyir və panelin gərginliyini dəqiq yeni $V_{\mathrm{mp}}$ səviyyəsinə oturdur.
> 
> Bu mürəkkəb ikiqat təsir altında belə orta izləmə səmərəliliyi 99.94% olmuş, qərarlaşmış güc xətası isə cəmi 0.23 Vatt təşkil etmişdir."

---

```
========================================================================================
SLAYD 16: EKSPERİMENT 6: QİSMƏN KÖLGƏLƏNMƏ VƏ ÇOXZİRVƏLİ ƏYRİ
========================================================================================
```
### Slaydın Vizual Məzmunu:
- **3 Zirvəli P-V Əyrisinin Yaranması:**
  - 3 seriyalı modul ardıcıl birləşdirilib və hər birində bypass diodu var;
  - Modul 1: $1000\ \text{W/m}^2$ (tam günəş);
  - Modul 2: $400\ \text{W/m}^2$ (orta kölgə);
  - Modul 3: $200\ \text{W/m}^2$ (ağır kölgə).
- **Fiziki Pik Nöqtələri:**
  - Qlobal Maksimum (GMPP): **$1338.2\ \text{W}$ @ $132.3\ \text{V}$**
  - Lokal Pik 1 (LMPP-1): **$790.1\ \text{W}$ @ $130.2\ \text{V}$**
  - Lokal Pik 2 (LMPP-2): **$395.6\ \text{W}$ @ $130.4\ \text{V}$**
- **Qrafik:** 3 zirvəli xarakterik P-V əyrisi və üzərində işarələnmiş GMPP və LMPP nöqtələri.

### Çıxış Mətni (Tam nitq):
> "İndi isə işimizin ən maraqlı, elmi və praktiki baxımdan ən aktual probleminə gəlirik: **Qismən Kölgələnmə (Partial Shading)**.
> 
> Günəş stansiyalarında ağac budağı, dirək kölgəsi və ya quş çirklənməsi səbəbindən ardıcıl panellərin bəziləri kölgələnə bilir. Əgər qoruyucu bypass diodları olmasa, kölgəli panel 'qaynar nöqtə' (hotspot) effekti ilə yanıb sıradan çıxar.
> 
> Lakin bypass diodları işə düşdükdə dövrənin fiziki təbiəti kökündən dəyişir! Slayddakı qrafikə diqqətlə baxın: 3 modulun biri 1000, ikincisi 400, üçüncüsü 200 Vatt/kvadrat işıqlanma aldıqda, P-V əyrisində artıq tək bir təpə deyil, **3 fərqli güc zirvəsi** yaranır!
> 
> Bunlardan yalnız biri əsl Qlobal Maksimumdur (GMPP) — 1338 Vatt gücündə. Digər iki təpə isə aldadıcı Lokal Pikləridir (biri 790 Vatt, digəri 395 Vatt). Və bu vəziyyət klassik alqoritmlər üçün böyük bir mühəndislik tələsi yaradır!"

---

```
========================================================================================
SLAYD 17: MÜHƏNDİSLİK XƏBƏRDARLIĞI: KLASSİK P&O-NUN LOKAL TƏLƏDƏ İLİŞİB QALMASI
========================================================================================
```
### Slaydın Vizual Məzmunu:
- **Klassik P&O Alqoritminin Məhdudiyyəti (Real Fakt):**
  - P&O işə düşərkən ən yaxın təpəyə dırmanır və $790.1\ \text{W}$-lıq lokal pikdə (LMPP-1) ilişib qalır!
  - İzləmə Səmərəliliyi: Cəmi **$72.36\%$**!
  - İtirilən Enerji: Mövcud 1338.2 Vatt gücün **$548\ \text{W}$-ı ($27.6\%$-i)** istifadəsiz qalır!
  - Səbəb: P&O kor 'dırmanıcıdır', yalnız qonşu nöqtənin meylinə baxır, bütün əyrini görmür.
- **Mühəndislik Həlli: Qlobal MPPT (GMPPT):**
  1. *Scanning-based Global MPPT:* Doluluq əmsalı $D = 0.05 \rightarrow 0.90$ aralığında skan edilir, bütün piklər tapılır və 1338 Vattlıq qlobal pik seçilir.
  2. *Ağıllı Alqoritmlər (PSO, GA):* Hissəciklər Sürüsü Optimizasiyası (PSO) GMPP-ni 99% dəqiqliklə tapır.
  3. *Elmi Nəticə:* Çoxmodullu günəş stansiyalarında adi P&O bəs etmir, mütləq Qlobal MPPT tətbiq olunmalıdır.

### Çıxış Mətni (Tam nitq):
> "Bu slaydda simulyasiyamızın ən böyük elmi tapıntısını görürsünüz.
> 
> Klassik P&O alqoritmini həmin 3 zirvəli şəraitdə işə saldıqda nə baş verdi? Alqoritm işə düşən kimi qarşısına çıxan ilk təpəyə dırmandı və 790 Vattlıq lokal maksimumda ilişib qaldı! Alqoritm elə bilir ki, artıq pikdədir, çünki sağa da getsə güc azalır, sola da getsə güc azalır. O, 1338 Vattlıq əsl qlobal pikdən tamamilə bixəbərdir!
> 
> Nəticədə izləmə səmərəliliyi 99%-dən birbaşa **72.36%-ə** düşdü! Mövcud olan 1338 Vatt enerjinin 548 Vattı — yəni 27.6%-i havaya sovruldu!
> 
> Bəs mühəndislik həlli nədir?
> Biz tədqiqatımızda sübut etdik ki, kölgələnmə ehtimalı olan stansiyalarda adi P&O bəs etmir. Burada **Qlobal MPPT (GMPPT)** tətbiq olunmalıdır:
> Ya sistem periodik olaraq doluluq əmsalını 0.05-dən 0.90-dək sürətlə skan etməli və 1338 Vattlıq mütləq piki tapmalıdır; ya da **PSO (Hissəciklər Sürüsü Optimizasiyası)** kimi intellektual alqoritmlər işə salınmalıdır."

### Müəllimin Olası Sualı və Qısa Cavab:
- **Sual:** *"Bəs nə üçün hər zaman skan etmirlər?"*
- **Cavab:** *"Müəllim, skan zamanı doluluq əmsalı kəskin dəyişdiyi üçün bir neçə millisaniyə ərzində şəbəkəyə verilən gücdə kəsinti və dalğalanma yaranır. Ona görə də skan yalnız hava dəyişəndə və ya hər 5–10 dəqiqədən bir qısa müddətə işə salınır."*

---

```
========================================================================================
SLAYD 18: EKSPERİMENT 7: P&O VƏ INCREMENTAL CONDUCTANCE MÜQAYİSƏLİ ANALİZİ
========================================================================================
```
### Slaydın Vizual Məzmunu:
- **Müqayisə Cədvəli:**
  | Metrika | P&O | Incremental Conductance (INC) |
  | :--- | :---: | :---: |
  | **İzlənən Enerji** | 6321.3 J | 6321.3 J |
  | **Orta İzləmə Effektivliyi** | 98.86 % | 98.86 % |
  | **Qərarlaşmış Effektivlik** | 99.95 % | 99.95 % |
  | **Pik Dalğalanma ($\sigma$)** | 0.13 W | 0.13 W |
  | **Çevirici İtkisi** | ~377 J | ~377 J |
  | **Ümumi Sistem Faydalı İş Əmsalı** | 97.19 % | 97.19 % |
  | **İcraya Nəzarət** | Asan, intuitiv | Mürəkkəb diferensial |
  | **Hesablama Tələbi** | Çox az | Bölmə və törəmə tələb edir |
- **Əsas Tapıntı:** Standart (tək zirvəli) şəraitdə düzgün köklənmiş P&O və INC eyni yüksək nəticəni verir; seçim mikrokontrollerin resursuna görə aparılmalıdır.
- **Qrafik:** Hər iki alqoritmin zamana görə çıxış güclərinin müqayisəli qrafiki.

### Çıxış Mətni (Tam nitq):
> "7-ci eksperimentdə sənayedə ən çox mübahisə doğuran suala cavab axtardıq: **P&O, yoxsa Incremental Conductance? Hansı daha yaxşıdır?**
> 
> Hər iki alqoritmi eyni şəraitdə, eyni Canadian Solar paneli və Boost çeviricisi ilə sınaqdan keçirdik. Cədvəldəki rəqəmlər çox maraqlı həqiqəti ortaya qoyur:
> Tək zirvəli standart hava şəraitində, addım ölçüsü optimal seçildikdə hər iki alqoritm praktiki olaraq eyni nəticəni verir: Hasil olunan enerji 6321 Coul, orta səmərəlilik 98.86%, qərarlaşmış səmərəlilik 99.95%, ümumi sistem faydalı iş əmsalı isə 97.19%-dir.
> 
> Bəs fərq nədədir?
> Fərq proqram təminatının mürəkkəbliyindədir. P&O alqoritmini sadə bir 8-bitlik ucuz mikrokontrollerdə bir neçə sətir kodla reallaşdırmaq mümkündür. INC isə bölmə və törəmə tələb etdiyi üçün daha bahalı 32-bitlik prosessor tələb edir.
> 
> Nəticə: Sadə günəş qurğularında P&O tamamilə yetərlidir; yüksək dinamik tələbləri olan sənaye stansiyalarında isə INC və Qlobal MPPT seçilməlidir."

---

```
========================================================================================
SLAYD 19: MÜHƏNDİSLİK DÜRÜSTLÜYÜ: 20 AVTOMATİK FİZİKİ YOXLAMA (SANITY CHECKS)
========================================================================================
```
### Slaydın Vizual Məzmunu:
- **100% Uğurla Keçilmiş Avtomatik Yoxlamalar Siyahısı:**
  - `[PASS]` 1. $P = V \cdot I$ bərabərliyi hər addımda $0.1\%$ dəqiqliklə təmin edilir;
  - `[PASS]` 2. Hasil olunan güc həmişə müsbətdir ($P \geq 0$);
  - `[PASS]` 3. Rəqəmsal sabitlik tam qorunur (Sıfır NaN, Sıfır Inf);
  - `[PASS]` 4. $V_{\mathrm{oc}} > V_{\mathrm{mp}}$ və $I_{\mathrm{sc}} > I_{\mathrm{mp}}$ fiziki şərtləri təmin olunur;
  - `[PASS]` 5. $P_{\mathrm{max}} \approx V_{\mathrm{mp}} \cdot I_{\mathrm{mp}}$ bərabərliyi $2\%$ xəta hüdudundadır;
  - `[PASS]` 6. Çeviricinin doluluq əmsalı qəti şəkildə hədlərdədir: $D \in [0.05, 0.90]$;
  - `[PASS]` 7. Panelin gərginlik və cərəyanı mənfiyə düşmür ($V \geq 0, I \geq 0$);
  - `[PASS]` 8. Enerjinin Saxlanması Qanunu: $P_{\mathrm{c\imath x}} \leq P_{\mathrm{gir}}$ (Heç vaxt çıxış girişdən çox ola bilməz);
  - `[PASS]` 9. Heç bir rejimdə ekvivalent mənfi müqavimət yaranmır ($V/I > 0$);
  - `[PASS]` 10. Qərarlaşmış rejimdə dalğalanma $P_{\mathrm{max}}$-ın $0.1\%$-dən aşağıdır;
  - `[PASS]` 11–20. Termal monotonluq, determinizm, SI vahidləri və no-lookahead prinsipləri.
- **Yekun Status:** 20 / 20 Yoxlama Uğurla Keçildi — Model Fiziki Cəhətdən Düzgündür.

### Çıxış Mətni (Tam nitq):
> "Mühəndislik simulyasiyalarında ən böyük təhlükə 'gözəl görünən, lakin fiziki cəhətdən səhv olan' nəticələrdir. Biz simulyasiyamızın dürüstlüyünü sübut etmək üçün proqram daxilində **20 avtomatik fiziki yoxlama (Sanity Checks)** mexanizmi qurduq.
> 
> Bu yoxlamalar hər bir simulyasiya addımında avtomatik işə düşür:
> - Termodinamikanın birinci qanunu — enerjinin saxlanması: Çeviricinin çıxış gücü heç vaxt giriş gücündən çox ola bilməz ($P_{\mathrm{c\imath x}} \leq P_{\mathrm{gir}}$);
> - Doluluq əmsalı fiziki hədlərdən çıxmır ($D \in [0.05, 0.90]$);
> - Panelin gərginlik və cərəyanı heç vaxt mənfiyə düşmür;
> - Heç bir nöqtədə NaN və ya sonsuzluq xətası yaranmır;
> - Bütün ölçü vahidləri beynəlxalq SI standartına uyğundur.
> 
> Bütün 20 fiziki yoxlama 100% uğurla 'PASS' statusu almışdır. Bu fakt modelin sadəcə qrafik deyil, real fiziki və riyazi qanunlara əsaslanan mühəndislik aləti olduğunu qəti şəkildə sübut edir."

---

```
========================================================================================
SLAYD 20: YEKUN NƏTİCƏLƏR VƏ PRAKTİKİ TƏTBİQ
========================================================================================
```
### Slaydın Vizual Məzmunu:
- **Əsas Elmi və Mühəndislik Nəticələri (4 bənd):**
  1. *Dəqiq Modelləşdirmə:* Canadian Solar 400W paneli və Boost çeviricisi real fiziki itkilərlə analitik həll edildi.
  2. *Yüksək İzləmə Dəqiqliyi:* P&O və INC alqoritmləri $99.9\%$-dən yüksək izləmə dəqiqliyi və $0.3\ \text{s}$-dən az qərarlaşma nümayiş etdirdi.
  3. *Kölgələnmə Probleminin Sübutu:* Qismən kölgələnmədə $27.6\%$ enerji itkisi ilə lokal tələyə düşmə riyazi olaraq sübut edildi.
  4. *Praktiki Tətbiq:* Təqdim olunan kod və arxitektura birbaşa STM32 və ya Texas Instruments C2000 mikrokontrollerlərinə inteqrasiya oluna bilər.
- **Təşəkkür və Suallar Bölməsi:**
  - *Diqqətinizə görə təşəkkür edirəm! Suallarınızı məmnuniyyətlə cavablandıra bilərəm.*
  - Müəllif: Həmidov Xalid, Bakı, 2026.

### Çıxış Mətni (Tam nitq):
> "Yekun olaraq işimizin əsas elmi və praktiki nəticələrini ümumiləşdirmək istərdim:
> 
> 1. Canadian Solar 400 Vattlıq paneli tək diodlu model və Lambert W analitik funksiyası ilə modelləşdirilmiş, xətası 0.1%-dən az olmuşdur.
> 2. DC-DC Boost çeviricisi drossel, tranzistor, diod və kommutasiya itkiləri ilə birlikdə real güc elektronikası səviyyəsində inteqrasiya edilmişdir.
> 3. Həm P&O, həm də Incremental Conductance alqoritmləri standart və dəyişən hava şəraitində 99.9%-dən yüksək izləmə səmərəliliyi və 0.3 saniyəlik sürətli qərarlaşma nümayiş etdirmişdir.
> 4. Qismən kölgələnmə rejimində klassik alqoritmlərin 27.6% enerji itkisi ilə lokal maksimumda ilişib qalması riyazi olaraq sübut edilmiş və Qlobal MPPT həlli əsaslandırılmışdır.
> 5. Ən əsası, layihəmiz çərçivəsində yazılmış alqoritmlər və diskret idarəetmə arxitekturası birbaşa sənaye mikrokontrollerlərinə — məsələn, STM32 və ya Texas Instruments C2000 çiplərinə yüklənməyə tam hazırdır.
> 
> Dinlədiyiniz üçün hər birinizə dərin təşəkkürümü bildirirəm! Mövzu ilə bağlı suallarınızı məmnuniyyətlə cavablandırmağa hazıram."

---

## 🎯 Müdafiə Zamanı Müəllimlərdən Gələ Biləcək "Top-5" Çətin Sual və Dəqiq Cavablar

1. **Sual:** *"Niyə Buck çeviricisi deyil, məhz Boost çeviricisi seçdiniz?"*
   - **Cavab:** *"Müəllim, günəş panelimizin nominal gərginliyi təxminən 41 Voltdur. Şəbəkəyə qoşulan invertorların və ya sənaye akkumulyator şinlərinin gərginliyi isə adətən 48 Volt, 100 Volt və ya daha yüksək olur. Panelin aşağı gərginliyini sistem şininə uyğunlaşdırmaq üçün gərginliyi artıran (step-up), yəni Boost topologiyası tələb olunur."*

2. **Sual:** *"Lambert W funksiyasının Nyuton-Rafsondan əsas üstünlüyü nədir?"*
   - **Cavab:** *"Nyuton-Rafson iterativ ədədi üsuldur. Əgər başlanğıc nöqtə yaxşı seçilməsə və ya kəskin hava sıçrayışı baş versə, törəmə sıfıra yaxınlaşır və metod ilişib qalır (divergensiya). Lambert W isə qapalı analitik həlldir — heç bir dövr və ya iterasiya tələb etmir, birbaşa dəqiq nəticəni verir və 100% rəqəmsal dayanıqlıdır."*

3. **Sual:** *"P&O alqoritmində addım ölçüsü ($\Delta D$) niyə 0.005 seçildi?"*
   - **Cavab:** *"Biz addım ölçüsü üzərində həssaslıq analizi apardıq. $\Delta D = 0.01$ olanda sistem pik nöqtəsində $\pm 1.5\ \text{W}$ yellənirdi. $\Delta D = 0.001$ olanda isə qərarlaşma müddəti 1.5 saniyəyə qədər gecikirdi. $\Delta D = 0.005$ qiyməti həm 0.3 saniyəlik sürətli keçid, həm də cəmi 0.36 Vattlıq minimal dalğalanma təmin edən optimal kompromis nöqtəsi oldu."*

4. **Sual:** *"Qismən kölgələnmədə bypass diodları olmasa nə baş verər?"*
   - **Cavab:** *"Bypass diodları olmasa, kölgədə qalan zəif fotoelement dövrədə yük kimi davranmağa başlayır. Digər panellərin hasil etdiyi cərəyan həmin hüceyrədən keçərkən güclü istilik ayrılır ('Hot-spot' effekti) və panel fiziki olaraq yanaraq sıradan çıxır. Bypass diodu kölgəli modulu dövrədən xaric edərək cərəyanı kənardan ötürür, lakin bu da P-V əyrisində çoxzirvəli dalğalanma yaradır."*

5. **Sual:** *"Simulyasiyada qəbul etdiyiniz $20\ \text{Hz}$ MPPT tezliyi real avadanlıqlar üçün uyğundurmu?"*
   - **Cavab:** *"Bəli, tamamilə uyğundur. Sənaye MPPT invertorlarında (məsələn, SMA, Huawei) MPPT alqoritmi adətən 10–50 Hers tezliklə işə düşür. Çünki drossel və kondensatorun keçid prosesi 2–5 millisaniyə çəkir. Çeviricinin öz PWM tezliyi 50 kilohets olsa da, MPPT alqoritminin hər 50 millisaniyədən bir qərar verməsi sistemin sabitliyi üçün beynəlxalq standartdır."*
