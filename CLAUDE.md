# CLAUDE.md — DEEP-FORGE / ForgeDepthStudio (kalici hafiza; kisa tutulur, detay docs/ altinda)

> **YEREL OTURUM ISE:** Kullanici seni Etsy guncellemesi icin actiysa yalnizca `docs/ONE_TIME_TASK_ETSY_UPDATE.md` gorevini yap (tek seferlik), bitince oradaki bitis mesajini yaz ve dur.
> **DURUM (2026-10-24):** Etsy guncellemesi yerel oturumda yapildi (kullaniciya gore 6 ilan duzenlendi; bulut Etsy'ye erisemedigi icin dogrulama icin Listings ekran goruntusu istendi). **Kullanici acikca soyleyene kadar Faz B'ye GECME; haber bekle.**

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
- Kod: `first_launch_builder.py` (cekirdek), `batch_factory.py`, `bundle_packager.py`, `seo_generator.py`, `make_listing_video.py`; testler `tests/` (`python -m pytest -q`), CI `.github/workflows/ci.yml`. `inputs/ outputs/ *.mp4 *.zip bot_profile/ .env` git disi.
- Kullanicinin `forge/` klasoru repo ile birebir ayni (2026-10-23). `traffic_cannon.py` HIC YAZILMAMIS (handover'daki "MEVCUT" bilgisi yanlis) -> Faz C'de kurallara uygun yazilacak.
- **Gercek set (Etsy ekran goruntusuyle dogrulandi 2026-10-24):** 01_Fenrir_Wolf, 02_Valkyrie_Warrior, 03_Yggdrasil_Tree, 04_Thor_Mjolnir, 05_Odin_Allfather + bundle. Handover'daki "04 Vegvisir" YANLIS (4. urun Thor cekici). Canli basliklar eski seo_generator ciktisi (Thor basliginda "CNC Router", aciklamalarda "pre-calibrated" var). Fenrir ilaninin kapak fotografi 04 Comparison (kural: 01 Wood).
- Kullanici git/GitHub Desktop kullanmakta zorlaniyor: dosya alisverisi sohbete surukle-birak + SendUserFile ile.

## 5. Calisma kurallari
Batch uyumlu, try/except, az bagimlilik (opencv, numpy, Pillow; reportlab PDF; ffmpeg video). Pathlib + `Path(__file__).parent`; unicode yol icin `np.fromfile`+`imdecode`. Yazdigini calistir ve dogrula; sonucu durustce raporla. Moduller ayni cikti sozlesmesini kullanir.

## 6. Yol haritasi (yonetici durumu)
Plan: `docs/AUDIT_AND_WORKPLAN.md`. Faz A (2026-10-23): A1 iddia temizligi, A2 Vegvisir/Yggdrasil SEO, A3 bundle Etsy teslimi + link korumasi, A5 testler/CI TAMAM (kodda). Canli 6 ilan guncellendi (kullanici beyani, 2026-10-24). Kullanicinin forge/ klasorundeki .py dosyalari eski olabilir (yeni surumler gonderildi; kopyalandigi teyit edilmedi).
Siradaki: Faz B (K1 isik -> derinlik duzeltmesi, gercek makine testi), Faz C (Pinterest toplu CSV/zamanlama, YouTube resmi yol, `traffic_cannon` sifirdan), Faz D.
Bekleyen kurucu kararlari: Shorts otomasyonunun yontemi (API mi tarayici mi), scout_engine resmi kaynak onayi.
