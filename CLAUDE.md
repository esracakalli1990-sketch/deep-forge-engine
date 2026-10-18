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
| 2 | `02_asset_factory` | Ham AI gorselinden #000000 arka plan, CLAHE, Bilateral, Unsharp, 4000x4000 300 DPI depth map; bundle icin ReportLab PDF teslimat | planli (cekirdegi `first_launch_builder.py`'de) |
| 3 | `03_mockup_renderer` | NumPy/OpenCV Sobel/Scharr bump mapping ile ahsap/pirinc/arduvaz mockup + 10 sn lazer-tarama MP4 | kismen (`first_launch_builder.py`, `make_listing_video.py`) |
| 4 | `04_seo_listing_brain` | 140 karakter baslik, 13 long-tail etiket, teknik aciklama | planli |
| 5 | `05_traffic_cannon` | Pinterest + YouTube Shorts/TikTok otomatik yayin koprusu (kullanicinin 30 gunde 9M izlenmeli Shorts otomasyonuna baglanacak) | planli |

Modul klasorleri ihtiyac olunca olusturulur; bos iskelet acilmaz.

## 4. Depo duzeni (su an)
- `first_launch_builder.py` — tek dosya: depth map + ahsap mockup + pirinc mockup + logo -> `etsy_launch_pack/`
- `make_listing_video.py` — 10 sn, 1080x1080, 30 FPS sessiz urun videosu -> `etsy_launch_pack/03_Etsy_Listing_Video.mp4`
- `requirements.txt`, `.gitignore`
- `etsy_launch_pack/`, `input_wolf.png`, `*.mp4` git'e girmez (uretilen/buyuk dosyalar).

Gelistirme dali: `claude/keen-goodall-bpjwvb`. PR sadece kullanici isteyince acilir.

## 5. Calisma kurallari
1. Kod toplu isleme (batch) uyumlu, `try/except` ile hata yakalayan, az bagimlilikli, hizli ve temiz olsun. Tek goruntu icin degil, onlarca urun icin tasarla.
2. Bagimliliklar: `opencv-python`, `numpy`, `Pillow` (cekirdek). Eklemeden once gerekce ver; agir AI modeli indirme yok. Video icin sistem `ffmpeg` (veya `imageio-ffmpeg`) kullanilir.
3. Her scripti yazdiktan sonra **calistir ve dogrula** (cikti boyutu, sure, gorsel kontrol); sonucu durustce raporla.
4. Pathlib, `Path(__file__).resolve().parent` tabanli yollar; Windows/Mac/Linux uyumlu; unicode yollar icin `np.fromfile` + `cv2.imdecode`.
5. Moduller ayni cikti sozlesmesini paylasir: urun basina klasor, standart dosya adlari.

## 6. Teknik sozlesmeler (degistirme, gerekirse haber ver)
- **Depth map:** 8-bit `L`, 4000x4000, 300 DPI (`pHYs`), dairesel maske, disi saf `#000000`. Ton: beyaz = yuksek/kesilmemis, siyah = en derin. Islem: gri -> CLAHE(clipLimit=3.0, 8x8) -> Bilateral x2 -> persentil germe -> Lanczos4 -> maske.
- **Isik modeli (mockup):** sol-ust 45 derece, `L=(-0.5,-0.5,0.7071)`, goruntu koordinati x sag / y asagi, normal `n=(-gx,-gy,1)`, Sobel ksize=3 /8.
- **Ahsap mockup:** 4 mm oyma ~ 24 px yukseklik olcegi; AO + golge isin izleme + color burn. Procedural ceviz (NumPy fbm), harici doku yok.
- **Pirinc mockup:** 62 px yukseklik olcegi, patina + specular (keskin ^90 + genis ^14), koyu antrasit zemin, drop shadow.
- **Mockup duzeni:** 2000x2000; tasarim cemberi capi 1400, merkez (1000, 960). Video script'i bu duzene bagimli — degisirse ikisini birlikte guncelle.
- **Etsy rozeti:** "3D DEPTH MAP | 300 DPI PNG | LIGHTBURN & CNC READY".

## 7. Etsy / uyumluluk notlari (dogrulanacak)
- Dijital dosya basina 20 MB siniri (depth map ~3.6 MB, sorun yok).
- Yapay zeka ile uretilen gorsellerin Etsy'nin "yaratim sureci / AI" beyan kurallarina uygun belirtilmesi gerekir.
- `01_scout_engine` Etsy'yi kazir: Etsy kullanim sartlari otomatik kazimayi kisitlayabilir. Yazmadan once oran sinirlama (rate limit), robots.txt ve resmi Etsy Open API alternatifi degerlendirilecek; hesap/magaza riskini kullaniciya acikca soyle.

## 8. Tamamlananlar
- [x] `first_launch_builder.py` (4 dosya, kurt gorseliyle dogrulandi, kullanici makinesinde calisti)
- [x] `make_listing_video.py` (10 sn lazer-tarama listing videosu)

## 9. Siradaki isler
- Batch modu (`inputs/` klasoru, urun basina cikti klasoru) — kullanici onayiyla.
- `02_asset_factory`, `04_seo_listing_brain`, `05_traffic_cannon`, `01_scout_engine`.
