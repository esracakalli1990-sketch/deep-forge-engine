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
- Kullanicinin `forge/` klasorundeki 5 .py dosyasi repodakiyle BIREBIR AYNI (2026-10-23 dogrulandi). `traffic_cannon.py` handover'da var ama kullanici gondermedi — varligi teyit edilecek.
- Gercek set: 01_Fenrir_Wolf, 02_Yggdrasil_Tree_of_Life, 03_Valkyrie_Warrior, 04_Vegvisir_Viking_Compass, 05_Odin_Allfather (+06 bundle). `seo_generator` profilleri Thor icin yazildi; Vegvisir ve Yggdrasil ad degisikligi icin profil guncellenmeli.

## 5. Calisma kurallari
Batch uyumlu, try/except, az bagimlilik (opencv, numpy, Pillow; reportlab PDF; ffmpeg video). Pathlib + `Path(__file__).parent`; unicode yol icin `np.fromfile`+`imdecode`. Yazdigini calistir ve dogrula; sonucu durustce raporla. Moduller ayni cikti sozlesmesini kullanir.

## 6. Yol haritasi (yonetici durumu)
Tamam: Faz 1-2 (magaza, 6 ilan, uretim fabrikasi, traffic_cannon). **Guncel plan ve bulgular: `docs/AUDIT_AND_WORKPLAN.md`** (Faz A dogruluk/hijyen -> B urun kalitesi -> C uyumlu trafik -> D buyume -> E yeni sutunlar).
Kritik bulgular: K1 isik depth'e gomulu (dis halka %41 sapma; CNC vaadi riskli), K2 "calibrated" iddialari, K3 UI-bot ToS riski, K4 Etsy kazima riski, Y1 Vegvisir SEO hatasi, Y2 kismen cozuldu (5 dosya ayni; traffic_cannon belirsiz).
Kurucu kararlari bekleniyor (rapor Bolum 8): Kural 3.2 revizyonu, Adim 1/3 yontemi, konumlandirma, Faz A onayi.
