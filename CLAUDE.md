# CLAUDE.md — DEEP-FORGE / ForgeDepthStudio (kalici hafiza; kisa tutulur, detay docs/ altinda)

Detay: `docs/DEEP_FORGE_MASTER_HANDOVER.md` (anayasa, tek gercek kaynagi) | `docs/TECH_CONTRACTS.md` (kod sozlesmeleri: depth map, isik modeli, ZIP/SEO kurallari). Kod degistirmeden once TECH_CONTRACTS'i oku.

## 1. Roller
- **Gemini Argon:** strateji (pazar, algoritma, urun). **Kurucu (kullanici):** operasyon lideri, fiziksel uygulayici (Etsy, hesaplar, kendi bilgisayarinda calistirma).
- **Claude (ben): YONETICI + BAS MUHENDIS.** Planlar, onceliklendirir, risk/ToS cakismalarini kodlamadan ONCE yuzune soyler, kodlar, calistirip dogrular, durustce raporlar. Kirmizi cizgi: yarim kod yok; uctan uca, test edilmis teslim.
- Dil: Turkce yanit; kod/dosya adi Ingilizce. Token: kisa raporlar, kullanicidan gereksiz ekran goruntusu isteme (tek seferde kopyala-yapistir sablon + tam kod).
- Bu oturum bulut ortaminda: kullanicinin bilgisayarinda komut CALISTIRAMAZ; push eder, kullanici calistirir. Playwright/hesap girisi gerektiren isler burada test EDILEMEZ (soyle). PR sadece istenirse. Dal: `claude/keen-goodall-bpjwvb`.

## 2. Proje
Etsy `ForgeDepthStudio` (forgedepthstudio.etsy.com): kucuk lazer/CNC/DTF isletmelerine B2B dijital uretim hammaddesi (sifir stok/kargo).
- **Sutun 1 AKTIF:** 3D depth map (Standard + Inverted PNG, 4000x4000, 300 DPI, 8-bit, disi #000000).
- Sutun 2 planli: 20oz tumbler seamless wrap + DTF paketleri. Sutun 3 planli: lazer/CNC maliyet tablolari (Sheets + Apps Script).
- **Durum:** magaza canli, 6 ilan Active ($4.99 x5: Fenrir, Yggdrasil, Valkyrie, Vegvisir, Odin; $12.99 5-in-1 bundle). **72 saat isindirma:** yeni ilan YOK; arka planda trafik/istihbarat.

## 3. Kirmizi cizgiler
1. VPN/proxy yok; temiz yerel IP + sabit Chrome profili. Isindirma: tek seferde 50 urun yok.
2. **Etsy yukleme:** tekli ilan -> Photos: 4 JPG (01 Wood kapak, 04 Comparison, 02 Brass, 03 Slate) + 05 video; **Digital files: SADECE 2 PNG** (Standard + Inverted), maks 5 dosya. Bundle -> Digital files: **SADECE teslimat PDF'i**; ZIP'ler Google Drive'da (herkes goruntuleyebilir).
3. AI beyani: "I did" -> "A finished product" -> "2020-2026" -> "Created by me with the help of an AI generator".
4. Pazarlamada kanitlanamayan iddia yok (ornek: makineye ozel Z-ekseni kalibrasyonu YAPMIYORUZ; genel 8-bit depth map).

## 4. Depo (bulut) ve kullanici PC'si
- Repoda: `first_launch_builder.py` (cekirdek), `batch_factory.py`, `bundle_packager.py`, `seo_generator.py`, `make_listing_video.py`. `inputs/ outputs/ *.mp4` git disi.
- Kullanicinin `forge/` klasorunde ek olarak `traffic_cannon.py` var (9:16 Shorts + 2:3 Pinterest uretir) — **repoda YOK**, muhendis yazdi; yonetmek icin repoya alinmali.
- Gercek set: 01_Fenrir_Wolf, 02_Yggdrasil_Tree_of_Life, 03_Valkyrie_Warrior, 04_Vegvisir_Viking_Compass, 05_Odin_Allfather (+06 bundle). `seo_generator` profilleri Thor icin yazildi; Vegvisir ve Yggdrasil ad degisikligi icin profil guncellenmeli.

## 5. Calisma kurallari
Batch uyumlu, try/except, az bagimlilik (opencv, numpy, Pillow; reportlab PDF; ffmpeg video). Pathlib + `Path(__file__).parent`; unicode yol icin `np.fromfile`+`imdecode`. Yazdigini calistir ve dogrula; sonucu durustce raporla. Moduller ayni cikti sozlesmesini kullanir.

## 6. Yol haritasi (yonetici durumu)
Tamam: Faz 1-2 (magaza, 6 ilan, uretim fabrikasi, traffic_cannon). Sirada (Handover Bolum 6): Adim 1 `auto_publisher.py`, Adim 2 `lead_magnet_builder.py`, Adim 3 `scout_engine.py`.
**Acik yonetici bulgulari (kodlamadan once karar gerekir):**
- Adim 1: UI-otomasyonu (Playwright) Pinterest/YouTube/TikTok ToS ve hesap riski tasir; resmi API (YouTube Data API, Pinterest API v5) once degerlendirilecek; kullanicinin mevcut Shorts otomasyonu yeniden kullanilabilir.
- Adim 3: Etsy'yi yerel IP + satici Chrome profiliyle kazimak magaza askiya alma riski; eski mutabakat: kazima yok / izole ya da resmi kaynak.
- Adim 2: forum/grup self-promo kurallari; "Z-ekseni kalibrasyonlu" iddiasi dogru degil -> metin duzeltilecek.
- `seo_generator.py`: bundle "FILES TO UPLOAD" ve aciklamasi ZIP'leri listeliyor; kural 3.2 ile celisiyor -> bundle icin sadece PDF + Drive linki olacak sekilde duzeltilecek.
