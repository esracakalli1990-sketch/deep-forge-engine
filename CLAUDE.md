# CLAUDE.md — DEEP-FORGE / ForgeDepthStudio (kalici hafiza; kisa tutulur, detay docs/ altinda)

> **YEREL OTURUM ISE:** Bekleyen tek seferlik gorev YOK (Etsy x2 ve `ONE_TIME_TASK_PINTEREST_PINS.md` TAMAMLANDI; tekrar yapma).
> **DURUM (2026-10-24):** Faz B TAMAM. Faz C: trafik YALNIZ Pinterest; ilk etapta pinler ELLE (Pinterest zamanlayicisi). Kurucu karari: Pinterest API otomasyonu (`pin_publisher.py`, RSS) TUM ISLER BITTIKTEN SONRA; YouTube/TikTok da sona. C1/C2 + `docs/PINTEREST_SETUP.md`, C5 `docs/COMMUNITY_PLAYBOOK.md`, C6 `docs/WEEKLY_METRICS.md` hazir. 6 ilan linki `links.json`'da (ID'ler: Fenrir 4601158125, Valkyrie 4601187128, Yggdrasil 4601190170, Thor 4601165553, Odin 4601194528, Bundle 4601175685); linkli takvim (2026-10-26 basliyor) gonderildi. Pinterest Business hesabi ACIK (pinterest.com/forgedepthstudio), 3 pano + 16 pin PLANLANDI (26.10-03.11.2026, kullanici beyani). Kurucu bir sure bilgisayar basinda degil; Faz D BEKLEMEDE (kurucu donunce once Faz D planini acikla, onayla basla). Sirada: ilk olcum 2026-11-02 (WEEKLY_METRICS), topluluk paylasimi (kurucu).

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
2. **Etsy yukleme:** tekli ilan -> Photos: 4 JPG (01 Wood kapak, 04 Comparison, 02 Brass, 03 Slate) + 05 video; **Digital files: SADECE 2 PNG** (Standard + Inverted), maks 5 dosya. **Bundle (2026-10-23 kurucu karari, Kural 3.2 revize):** Digital files = ZIP parcalari + teslimat PDF'i dogrudan Etsy'de (her biri <=20 MB, toplam <=5; `bundle_packager` varsayilan `--delivery etsy`). Drive yalniz 5 dosyaya sigmayan buyuk paketler icin (`--delivery drive --download-url`).
3. AI beyani: "I did" -> "A finished product" -> "2020-2026" -> "Created by me with the help of an AI generator".
4. Pazarlamada kanitlanamayan iddia yok ("calibrated" yok; makineye ozel Z-ekseni kalibrasyonu YAPMIYORUZ). **Lazer odakli konumlandirma (kurucu karari):** baslik/etiket/rozette CNC vaadi yok; CNC yalniz aciklamada durust uyari olarak. Testler (`tests/`) bunu zorlar.

## 4. Depo (bulut) ve kullanici PC'si
- Kod: `first_launch_builder.py` (cekirdek), `batch_factory.py`, `bundle_packager.py`, `seo_generator.py`, `make_listing_video.py`, `make_test_kit.py`, `traffic_cannon.py`, `pin_scheduler.py`; testler `tests/` (`python -m pytest -q`), CI `.github/workflows/ci.yml`. `inputs/ outputs/ *.mp4 *.zip bot_profile/ .env` git disi.
- Kullanicinin `forge/` klasoru repo ile birebir ayni (2026-10-23). `traffic_cannon.py` 2026-10-24 sifirdan yazildi (yalniz Pinterest pinleri; dikey video yok).
- **Gercek set (Etsy ekran goruntusuyle dogrulandi 2026-10-24):** 01_Fenrir_Wolf, 02_Valkyrie_Warrior, 03_Yggdrasil_Tree, 04_Thor_Mjolnir, 05_Odin_Allfather + bundle. Handover'daki "04 Vegvisir" YANLIS (4. urun Thor cekici). Canli ilanlar 2026-10-24'te yeni seo_generator ciktisi + yeni gorsellerle guncellendi.
- Kullanici git/GitHub Desktop kullanmakta zorlaniyor: dosya alisverisi sohbete surukle-birak + SendUserFile ile.

## 5. Calisma kurallari
Batch uyumlu, try/except, az bagimlilik (opencv, numpy, Pillow; reportlab PDF; ffmpeg video). Pathlib + `Path(__file__).parent`; unicode yol icin `np.fromfile`+`imdecode`. Yazdigini calistir ve dogrula; sonucu durustce raporla. Moduller ayni cikti sozlesmesini kullanir.

## 6. Yol haritasi (yonetici durumu)
Plan: `docs/AUDIT_AND_WORKPLAN.md`. Faz A (2026-10-23): A1 iddia temizligi, A2 Vegvisir/Yggdrasil SEO, A3 bundle Etsy teslimi + link korumasi, A5 testler/CI TAMAM (kodda). Canli 6 ilan guncellendi (kullanici beyani, 2026-10-24). Kullanicinin forge/ klasorundeki .py dosyalari eski olabilir (yeni surumler gonderildi; kopyalandigi teyit edilmedi).
Faz B TAMAM (B3 kitinin geri bildirimi bekleniyor). Faz C devam (Pinterest elle zamanlama; C1/C2 kodda). Sonra Faz D.
Ertelenenler (sona): Pinterest API otomasyonu + RSS, YouTube/Shorts. Bekleyen karar: scout_engine resmi kaynak onayi.
