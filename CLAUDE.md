# CLAUDE.md — Proje DEEP-FORGE (ForgeDepthStudio)

Bu dosya her oturumda baglami korumak icin referanstir. Degisiklik olursa guncelle.

## 1. Rol ve komuta zinciri
- **Gemini Argon:** stratejik beyin (pazar istihbarati, algoritma, urun stratejisi, mimari yonlendirme).
- **Kurucu (kullanici):** operasyon lideri, fiziksel uygulayici. Sifir sermaye, vardiya disi zamaninda calisiyor.
- **Claude (sen):** Bas Yazilim / Goruntu Isleme (Computer Vision) / Otomasyon muhendisi. Kodlama, goruntu isleme, veri kazima ve otomasyon.

**Kirmizi cizgi:** Yarim kod, "burayi sen doldur" ve kitabi tavsiye yok. Her teslim: eksiksiz, uctan uca calisan, test edilmis, hatasiz, moduler.
Kullanici Turkce yazar; yanitlar Turkce, kod/degisken/dosya adlari Ingilizce.

## 2. Is modeli
Etsy'de **"ForgeDepthStudio"** adiyla fiziksel uretim yapan kucuk isletmelere (lazer kazima atolyeleri, CNC router, Fiber/Galvo lazer, Sublimation/DTF) **B2B dijital uretim hammaddesi** satiyoruz. %100 dijital, sifir kargo, sifir stok.

Urun gruplari:
1. **3D Illusion Laser Engraving Depth Maps** — 8/16-bit grayscale PNG, 4000x4000 px, 300 DPI (LightBurn, EZCAD, Glowforge, xTool; ahsap/pirinc/arduvaz) + mega paketler (bundle).
2. **Seamless Tumbler Wraps & ticari uretim paketleri** — kusursuz birlesimli, 300 DPI baski dosyalari.

Durum: Etsy magazasi acildi, kimlik dogrulama (Persona / Pending Review) bekleniyor.
Ilk urun: "3D Viking Wolf Depth Map" (`input_wolf.png`).

## 3. 5 modullu otonom mimari
| # | Modul | Gorev | Durum |
|---|-------|-------|-------|
| 1 | `01_scout_engine` | Playwright ile Etsy trend/"gizli sampiyon" radari -> `hot_trends.json` | planli |
| 2 | `02_asset_factory` | Ham AI gorselinden #000000 arka plan, CLAHE, Bilateral, 4000x4000 300 DPI depth map; toplu uretim; bundle kapagi + ReportLab PDF teslimat | **hazir** (`batch_factory.py`, `bundle_packager.py`) |
| 3 | `03_mockup_renderer` | NumPy/OpenCV Sobel bump mapping ile ahsap/pirinc/arduvaz mockup + karsilastirma gorseli + 10 sn lazer-tarama MP4 | **hazir** (`first_launch_builder.py`, `batch_factory.py`, `make_listing_video.py`) |
| 4 | `04_seo_listing_brain` | 130-140 karakter baslik, 13 long-tail etiket (<=20 kr), teknik aciklama, AI beyani, fiyat | **hazir** (`seo_generator.py`) |
| 5 | `05_traffic_cannon` | Pinterest + YouTube Shorts/TikTok otomatik yayin koprusu (kullanicinin 30 gunde 9M izlenmeli Shorts otomasyonuna baglanacak) | planli |

Modul klasorleri ihtiyac olunca olusturulur; bos iskelet acilmaz.

## 4. Depo duzeni (su an)
- `first_launch_builder.py` — cekirdek kutuphane + ilk urun scripti: depth map, ahsap/pirinc render, logo, rozet, isik/golge yardimcilari. `batch_factory` ve `bundle_packager` bunu `import` eder.
- `batch_factory.py` — `inputs/` -> `outputs/<urun>/` toplu hat (depth map, 01 Wood, 02 Brass, 03 Slate, 04 Comparison, 05 Video). Auto-Rim & Background Zeroing burada.
- `bundle_packager.py` — `outputs/` -> `outputs/_MEGA_BUNDLE_<TEMA>/` (01_Bundle_Hero_Collage.jpg, Download_Instructions_and_License.pdf, Drive ZIP).
- `seo_generator.py` — `outputs/` -> her urun/bundle klasorune `ETSY_LISTING_SEO.txt` + `outputs/ALL_LISTINGS_READY.md` (baslik/etiket/aciklama/fiyat; kodda `assert` ile dogrulanir).
- `make_listing_video.py` — 10 sn, 1080x1080, 30 FPS sessiz video (`build_video()` + tek paket CLI).
- `requirements.txt`, `.gitignore`
- `inputs/`, `outputs/`, `etsy_launch_pack/`, `input_wolf.png`, `*.mp4` git'e girmez (girdi/uretilen buyuk dosyalar).

Gelistirme dali: `claude/keen-goodall-bpjwvb`. PR sadece kullanici isteyince acilir.

## 5. Calisma kurallari
1. Kod toplu isleme (batch) uyumlu, `try/except` ile hata yakalayan, az bagimlilikli, hizli ve temiz olsun. Tek goruntu icin degil, onlarca urun icin tasarla.
2. Bagimliliklar: `opencv-python`, `numpy`, `Pillow` (cekirdek). Eklemeden once gerekce ver; agir AI modeli indirme yok. Video icin sistem `ffmpeg` (veya `imageio-ffmpeg`) kullanilir.
3. Her scripti yazdiktan sonra **calistir ve dogrula** (cikti boyutu, sure, gorsel kontrol); sonucu durustce raporla.
4. Pathlib, `Path(__file__).resolve().parent` tabanli yollar; Windows/Mac/Linux uyumlu; unicode yollar icin `np.fromfile` + `cv2.imdecode`.
5. Moduller ayni cikti sozlesmesini paylasir: urun basina klasor, standart dosya adlari.

## 6. Teknik sozlesmeler (degistirme, gerekirse haber ver)
- **Depth map (Standard):** 8-bit `L`, 4000x4000, 300 DPI (`pHYs`), dairesel maske, disi saf `#000000`. Ton: beyaz = yuksek/kesilmemis, siyah = en derin. Islem: gri -> CLAHE(clipLimit=3.0, 8x8) -> Bilateral x2 -> persentil germe -> Lanczos4 -> maske.
- **Isik modeli (mockup):** sol-ust 45 derece, `L=(-0.5,-0.5,0.7071)`, goruntu koordinati x sag / y asagi, normal `n=(-gx,-gy,1)`, Sobel ksize=3 /8.
- **Ahsap mockup:** 4 mm oyma ~ 24 px yukseklik olcegi; AO + golge isin izleme + color burn. Procedural ceviz (NumPy fbm), harici doku yok.
- **Pirinc mockup:** 62 px yukseklik olcegi, patina + specular (keskin ^90 + genis ^14), koyu antrasit zemin, drop shadow.
- **Auto-Rim & Background Zeroing (`batch_factory.auto_depth_normalizer`):** 4 kosedeki 20x20 px ortalama parlaklik zemini (siyah/beyaz/gri) belirler; esik yalnizca kose istatistiginden gelir. Madalyon cemberi: on plan konturu -> robust (aykiri atan) cember uydurma -> radyal gradyan rafinesi (en dis guclu kenar; golge/halo'yu yok sayar) -> yedek HoughCircles. Zemin duz degilse veya cember bulunamazsa guvenli merkez dairesel maske (r=0.49*kisa kenar). Cember disi 2-3 px yumusak kenarla saf #000000. **Madalyonun ici asla ters cevrilmez** (yuksek = acik, cukur = koyu). Dogruluk testi: beyaz/gri/golgeli zeminde +-1 px.
- **Inverted depth map:** `<urun>_3D_DepthMap_INVERTED_300DPI.png` — madalyon ICI `255 - ton` (beyaz = en derin), cember DISI maske ile saf #000000. Dogrulama kodda: ic bolgede standart + inverted = 255, koseler 0. Mockup'lar yalniz Standard'tan uretilir.
- **ZIP boyut kurali (`bundle_packager.build_zips`):** her ZIP <= 20 MB (`--zip-limit-mb`). Standard + Inverted + PDF limite sigiyorsa tek ZIP; sigmiyorsa Standard ve Inverted ayri ZIP'lere (gerekirse Part1..n) bolunur — iki surum de teslim edilir. 5'li bundle: 2 ZIP x ~17.7 MB + PDF.
- **SEO kurallari (`seo_generator.py`):** baslik 130-140 kr, `intent` ifadesiyle acilir (LightBurn / Fiber Laser Coin / Slate Coaster / CNC Router / xTool D1 P2 rotasyonu), ilk 40 kr ve ilk 3 kelime urunler arasinda tekrar etmez, urun adi basligta bir kez gecer; tam 13 etiket, her biri <=20 kr ve >=2 kelime, tekrarsiz. AI beyani: "Designed with AI-assisted sculpting and precision-calibrated via custom depth-mapping algorithms for laser/CNC relief." Fiyat: tekil $4.99, 5'li bundle $12.99 (5 x $4.99 = $24.95 -> %48 tasarruf; tam %50 icin $12.49).
- **Mockup duzeni:** 2000x2000; tasarim cemberi capi 1400, merkez (1000, 960). Video script'i bu duzene bagimli — degisirse ikisini birlikte guncelle.
- **Rozetler:** ahsap "3D DEPTH MAP | 300 DPI PNG | LIGHTBURN & CNC READY"; slate "SLATE COASTER & WOOD READY"; bundle "<N>-IN-1 <TEMA> MEGA BUNDLE" + "300 DPI 3D DEPTH MAPS | COMMERCIAL USE".
- **Slate mockup:** koyu mat arduvaz coaster (duzensiz kenar, kalinlik), sicak gri beton zemin; depth map yalnizca ACIK kabarti yerlerde gumusi-beyaz "etch" (mid-tonlar koyu kalir).
- **Karsilastirma gorseli:** solda ham depth map (uzun panel), sagda ahsap + pirinc detay kirpimi, ortada dikey altin lazer cizgisi, altta 3 istatistik karti + "4000x4000px 300 DPI | LightBurn, Glowforge, xTool & CNC Ready" bandi.
- **Video zaman cizelgesi:** 0-3 sn lazer tarama (depth -> ahsap), 3-6.5 sn ahsap Ken Burns (odak sag alt: rozet kadrajda kalir), 6.5 pirinc, 8.2 slate crossfade (0.8 sn). Kodlayici: ffmpeg libx264 yuv420p.
- **Bundle PDF:** reportlab, Letter, tek sayfa, tiklanabilir "CLICK HERE TO DOWNLOAD YOUR FILES" butonu (Drive linki `--download-url`), LightBurn tablosu (3D Slice / Jarvis / Stucki), ticari kullanim lisansi.

## 7. Etsy / uyumluluk notlari (dogrulanacak)
- Dijital dosya basina 20 MB siniri (depth map ~3.6 MB, sorun yok).
- Yapay zeka ile uretilen gorsellerin Etsy'nin "yaratim sureci / AI" beyan kurallarina uygun belirtilmesi gerekir.
- `01_scout_engine` Etsy'yi kazir: Etsy kullanim sartlari otomatik kazimayi kisitlayabilir. Yazmadan once oran sinirlama (rate limit), robots.txt ve resmi Etsy Open API alternatifi degerlendirilecek; hesap/magaza riskini kullaniciya acikca soyle.

## 8. Tamamlananlar
- [x] `first_launch_builder.py` (kurt gorseliyle dogrulandi, kullanici makinesinde calisti)
- [x] `make_listing_video.py` (kullanici onayi: "kusursuz")
- [x] `batch_factory.py` — toplu hat, Auto-Rim & Background Zeroing, slate + comparison, video baglantisi
- [x] `bundle_packager.py` — Hero Collage + teslimat PDF + boyut kontrollu ZIP (Standard + Inverted)
- [x] Inverted depth map (`batch_factory.py`) — dogrulandi
- [x] `seo_generator.py` — 5 tekil + 1 bundle listing, `ALL_LISTINGS_READY.md`

## 9. Siradaki isler / acik noktalar
- Gercek 5'li Nordic seti (`01_Fenrir_Wolf` ... `05_Odin_Allfather`) kullanicinin makinesinde `inputs/` ile calistirilacak; sonuclar gorsel QA'ya girecek.
- Drive linki: ZIP Drive'a yuklenip `--download-url` ile PDF'e gomulecek (5'li paket ~18 MB, 10'lu ~36 MB).
- Kimlik onayindan sonra listing'ler: `ALL_LISTINGS_READY.md`'den yapistir; Etsy dosya sayisi/boyut limitlerini ve AI beyan alanlarini editorde dogrula.
- `05_traffic_cannon`, `01_scout_engine` (Etsy kazima riski: once API/harici kaynak).
- Lisans metni ve LightBurn ayar tavsiyeleri genel baslangic noktalaridir; yayindan once kullanici gozden gecirmeli.

## 10. KALDIGIMIZ YER (oturum durumu - en son guncelleme: Etsy kimlik onayi bekleniyor)
**Durum:** Magaza kimlik onayinda; teknik hazirlik tamam, yayin beklemede. Kullanici onay gelince "kaldigimiz yerden devam" diyecek.

**Hazir olan (hepsi bu dalda, test edildi):**
- Uretim hatti: `batch_factory.py` (Standard + Inverted depth map, 01 Wood, 02 Brass, 03 Slate, 04 Comparison, 05 Video), `bundle_packager.py` (Hero Collage, PDF, boyut kontrollu ZIP), `seo_generator.py` (5 tekil + 1 bundle listing), `make_listing_video.py`.
- Test sadece kurt gorselinin simule kopyalariyla yapildi (siyah/gri/beyaz zemin). **Gercek 5'li Nordic seti hic islenmedi.**

**Onay gelince sirayla:**
1. Kullanici gercek gorselleri `inputs/` icine koyar (`01_Fenrir_Wolf.png`, `02_Valkyrie_Warrior.png`, `03_Yggdrasil_Tree.png`, `04_Thor_Mjolnir.png`, `05_Odin_Allfather.png`; Odin'in zemini beyaz) ve `python batch_factory.py` calistirir. Ozet satirlarinda "madalyon bulundu / zemin" bilgisini kontrol et; "bulunamadi -> guvenli merkez daire" ciktiysa o urunun depth map'ine gozle bak.
2. Kullanici mockup/slate/comparison ciktilarini sohbete yukler -> birlikte son gorsel QA (ozellikle Odin beyaz-zemin ve kenar halo kontrolu).
3. ZIP'ler Google Drive'a yuklenir -> `python bundle_packager.py --download-url "<Drive linki>"` -> `python seo_generator.py`.
4. `ALL_LISTINGS_READY.md`'den listing'ler Etsy'ye yapistirilir (Etsy dosya sayisi/boyut limiti ve AI beyan alanlari editorde dogrulanir).

**Bekleyen kullanici kararlari:**
- Bundle fiyati: $12.99 (%48 tasarruf) mi, $12.49 (tam %50) mu? (`--bundle-price`)
- Ilk gercek calistirmadan sonra gelen gorsel QA geri bildirimine gore ince ayar.

**Siradaki modul adaylari:** `05_traffic_cannon` (Pinterest + Shorts/TikTok yayin koprusu; kullanicinin mevcut 9M izlenmeli Shorts otomasyonuna baglanacak), `01_scout_engine` (YALNIZCA izole/resmi API veya harici veri kaynagiyla; kimlik onayi surecinde yerel IP'den Etsy kazima YAPILMAYACAK - kullanici ile mutabik).

**Kullanici tercihleri:** Turkce konusur; "eksiksiz, uctan uca, test edilmis" ister; once calistirip kanitla raporla; PR sadece istenirse; bu oturumda Claude kullanicinin bilgisayarinda komut CALISTIRAMAZ (bulut ortami) - degisiklik push edilir, kullanici kendi makinesinde calistirir.
