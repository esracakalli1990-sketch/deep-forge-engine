# CLAUDE.md — DEEP-FORGE / ForgeDepthStudio (kalici hafiza; kisa tutulur, detay docs/ altinda)

> **YEREL OTURUM ISE:** Bekleyen tek seferlik gorev YOK (Etsy x2, Pinterest pin, SCOUT, Noel ilani TAMAMLANDI; tekrar yapma).
> **DURUM (2026-10-24):** Kurucu karari B sonra A. **50'lik Noel depth map paketi URETILDI** (Higgsfield z_image, 54 gorsel uretildi, 4 test dahil; 8 elendi/yenilendi; scratchpad xmas/out/_BUNDLE: kapak, katalog, 4 mockup, video, ilan metni $9.99, STANDARD+INVERTED ZIP ~120 MB'lik iki dosya). Teslim = Drive (Etsy 5x20 MB'a sigmaz). Drive klasoru: https://drive.google.com/drive/folders/1bt2_0RMp8opYWk62vfudHzvAhRie2r_I (herkese acik okuma dogrulandi; ZIP'ler 2026-10-24 itibariyla klasorde GORUNMUYORDU). **Noel ilani CANLI:** https://forgedepthstudio.etsy.com/listing/4602548321 ($9.99, 2026-10-24). Drive ZIP'leri MCP aramasiyla dogrulanamadi -> kurucu gizli pencerede test etmeli. 6 Noel pini (yeni pano 'Christmas Laser Engraving Designs', 25-30.10, 13:00 ET) kurucuya gonderildi. Higgsfield ucretsiz plan TICARI KULLANIM sarti dogrulanmadi (yayindan once kurucu kontrol etmeli). Higgsfield kredisi ~1.3 kaldi; kalan uretim kurucunun Gemini Pro/Nano Banana Pro ile.

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
- **Durum:** magaza canli, 6 ilan Active ($4.99 x5: Fenrir, Valkyrie, Yggdrasil, Thor Mjolnir, Odin; $12.99 5-in-1 bundle). **72 saat isindirma:** yeni ilan YOK; arka planda trafik/istihbarat.

## 3. Kirmizi cizgiler
1. VPN/proxy yok; temiz yerel IP + sabit Chrome profili. Isindirma: tek seferde 50 urun yok.
2. **Etsy yukleme:** tekli ilan -> Photos: 4 JPG (01 Wood kapak, 04 Comparison, 02 Brass, 03 Slate) + 05 video; **Digital files:** 2 PNG 8-bit (Standard + Inverted) + (2026-10-24 kurucu onayi) 2 PNG 16-bit + 1 STL = 5 dosya (Etsy maks 5, her biri <20 MB). Canli 6 ilanda henuz yalniz 2 PNG var. **Bundle (2026-10-23 kurucu karari, Kural 3.2 revize):** Digital files = ZIP parcalari + teslimat PDF'i dogrudan Etsy'de (her biri <=20 MB, toplam <=5; `bundle_packager` varsayilan `--delivery etsy`). Drive yalniz 5 dosyaya sigmayan buyuk paketler icin (`--delivery drive --download-url`).
3. AI beyani: "I did" -> "A finished product" -> "2020-2026" -> "Created by me with the help of an AI generator".
4. Pazarlamada kanitlanamayan iddia yok ("calibrated" yok; makineye ozel Z-ekseni kalibrasyonu YAPMIYORUZ). **Lazer odakli konumlandirma (kurucu karari):** baslik/etiket/rozette CNC vaadi yok; CNC yalniz aciklamada durust uyari olarak. Testler (`tests/`) bunu zorlar.

## 4. Depo (bulut) ve kullanici PC'si
- Kod: `first_launch_builder.py` (cekirdek), `batch_factory.py`, `bundle_packager.py`, `seo_generator.py`, `make_listing_video.py`, `make_test_kit.py`, `traffic_cannon.py`, `pin_scheduler.py`, `scout_engine.py` (Etsy API istihbarat); testler `tests/` (`python -m pytest -q`), CI `.github/workflows/ci.yml`. `inputs/ outputs/ *.mp4 *.zip bot_profile/ .env` git disi.
- Kullanicinin `forge/` klasoru repo ile birebir ayni (2026-10-23). `traffic_cannon.py` 2026-10-24 sifirdan yazildi (yalniz Pinterest pinleri; dikey video yok).
- **Gercek set (Etsy ekran goruntusuyle dogrulandi 2026-10-24):** 01_Fenrir_Wolf, 02_Valkyrie_Warrior, 03_Yggdrasil_Tree, 04_Thor_Mjolnir, 05_Odin_Allfather + bundle. Handover'daki "04 Vegvisir" YANLIS (4. urun Thor cekici). Canli ilanlar 2026-10-24'te yeni seo_generator ciktisi + yeni gorsellerle guncellendi.
- Kullanici git/GitHub Desktop kullanmakta zorlaniyor: dosya alisverisi sohbete surukle-birak + SendUserFile ile.

## 5. Calisma kurallari
Batch uyumlu, try/except, az bagimlilik (opencv, numpy, Pillow; reportlab PDF; ffmpeg video). Pathlib + `Path(__file__).parent`; unicode yol icin `np.fromfile`+`imdecode`. Yazdigini calistir ve dogrula; sonucu durustce raporla. Moduller ayni cikti sozlesmesini kullanir.

## 6. Yol haritasi (yonetici durumu)
Plan: `docs/AUDIT_AND_WORKPLAN.md`. Faz A (2026-10-23): A1 iddia temizligi, A2 Vegvisir/Yggdrasil SEO, A3 bundle Etsy teslimi + link korumasi, A5 testler/CI TAMAM (kodda). Canli 6 ilan guncellendi (kullanici beyani, 2026-10-24). Kullanicinin forge/ klasorundeki .py dosyalari eski olabilir (yeni surumler gonderildi; kopyalandigi teyit edilmedi).
Faz B TAMAM (B3 kitinin geri bildirimi bekleniyor). Faz C devam (Pinterest elle zamanlama; C1/C2 kodda). Sonra Faz D.
Ertelenenler (sona): Pinterest API otomasyonu + RSS, YouTube/Shorts. Bekleyen karar: scout_engine resmi kaynak onayi.
