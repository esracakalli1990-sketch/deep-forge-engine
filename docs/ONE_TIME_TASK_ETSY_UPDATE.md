# TEK SEFERLİK GÖREV — Etsy ilan güncellemesi (ForgeDepthStudio)

> **Bu dosyayı okuyan yerel Claude oturumu için:** Bu, yalnızca BİR KEZ yapılacak, sınırlı bir görevdir. Görev bitince başka hiçbir şeye geçme;
> kullanıcıya aşağıdaki "Bitiş mesajı"nı yaz ve dur. Projenin geri kalanı (kod, planlama) başka bir oturumda yürütülüyor; bu oturumda kod değiştirme.

## Amaç
Etsy mağazası **ForgeDepthStudio**'daki 6 aktif ilanın metinlerini, fotoğraflarını ve videolarını hazır dosyalarla güncellemek.
Neden: eski metinlerde kanıtlanamayan "pre-calibrated" iddiası ve CNC vaadi var; Thor ilanının başlığı yanlış konumlandırılmış; bundle teslim yöntemi değişti.

## Gerekli dosyalar (kullanıcının bilgisayarında, büyük ihtimalle İndirilenler / Downloads klasöründe)
1. `ETSY_GUNCELLEME.zip` → aç. İçinde `ETSY_GUNCELLEME/` klasörü:
   - `0_NASIL_YAPILIR.txt`
   - `1_Fenrir_Wolf/`, `2_Valkyrie_Warrior/`, `3_Yggdrasil_Tree/`, `4_Thor_Mjolnir/`, `5_Odin_Allfather/`: her birinde `01_Wood_Mockup.jpg`, `04_Comparison_Split_Guide.jpg`, `05_Listing_Video.mp4`, `YAPISTIR.txt`
   - `6_Norse_Mythology_Bundle/YAPISTIR.txt`
2. Bundle dijital dosyaları (ayrı indirildi): `5_IN_1_NORDIC_MYTHOLOGY_MEGA_BUNDLE_STANDARD_Files.zip`, `5_IN_1_NORDIC_MYTHOLOGY_MEGA_BUNDLE_INVERTED_Files.zip`, `Download_Instructions_and_License.pdf`

Dosyaları bulamazsan kullanıcıya nerede olduklarını sor; tahmin etme.

## İlan eşleştirmesi (Etsy > Shop Manager > Listings; şu anki başlığın başı)
| Klasör | Etsy'deki mevcut başlık başlar | Fiyat |
|--------|-------------------------------|-------|
| 1_Fenrir_Wolf | "LightBurn 3D Depth Map…" | $4.99 |
| 2_Valkyrie_Warrior | "Fiber Laser Coin Relief Fil…" | $4.99 |
| 3_Yggdrasil_Tree | "Slate Coaster Laser Engr…" | $4.99 |
| 4_Thor_Mjolnir | "CNC Router Relief Depth…" | $4.99 |
| 5_Odin_Allfather | "xTool D1 P2 Laser Engravi…" | $4.99 |
| 6_Norse_Mythology_Bundle | "5-in-1 Mega Bundle Laser…" | $12.99 |

Fotoğraftaki madalyonun klasörle eşleştiğini kontrol et (kurt / kanatlı kadın savaşçı / ağaç / yılanla çevrili çekiç / sakallı Odin ve kuzgunlar). Eşleşmiyorsa DUR ve kullanıcıya sor.

## Her tekli ilan için (1–5) — Edit sayfasında
1. **Photos:** eski kapak (1. fotoğraf) ve eski karşılaştırma görselini (ham depth map + ahşap + pirinç paneli olan) sil.
   `01_Wood_Mockup.jpg` → **1. sıra (kapak)**, `04_Comparison_Split_Guide.jpg` → **2. sıra**. Diğer fotoğraflar (pirinç, arduvaz) kalır.
2. **Video:** eski videoyu sil, `05_Listing_Video.mp4` yükle.
3. **Title:** `YAPISTIR.txt` bölüm 1'deki metnin aynısı.
4. **Tags:** önce mevcut 13 etiketi sil, sonra bölüm 2'deki satırı yapıştır (13 etiket olmalı).
5. **Description:** mevcut metnin tamamını sil, bölüm 3'teki metni yapıştır.
6. **Kaydet** (Update / Publish changes).

## Bundle ilanı için (6)
- Title / Tags / Description: `6_Norse_Mythology_Bundle/YAPISTIR.txt` (aynı yöntem).
- **Digital files:** mevcut PDF'i (Google Drive linkli eski kılavuz) sil; 3 dosyayı yükle: 2 ZIP + `Download_Instructions_and_License.pdf`.
- Fotoğraflar ve video aynı kalır.
- Kaydet.

## Kesin kurallar
- **DOKUNMA:** fiyat, stok (999), kategori, "How it's made"/AI beyanı ayarları, tekli ilanlardaki 2 PNG dijital dosya, kargo/iade politikaları, diğer mağaza ayarları.
- Yeni ilan oluşturma, ilan silme, indirim/reklam açma YOK.
- İlk ilanı kaydetmeden önce kullanıcıya göster ve onay al; onaydan sonra kalan ilanları aynı şekilde yap.
- Etsy beklenmedik bir uyarı, doğrulama (captcha, giriş, politika uyarısı) veya hata gösterirse DUR, kullanıcıya bildir.
- İnsan hızında, ilan ilan çalış; toplu düzenleme (Bulk edit) kullanma.
- Her ilandan sonra kısa kontrol: başlık ve 13 etiket kaydedilmiş mi, kapak fotoğrafı ahşap mockup mı.

## Bitiş mesajı (görev bitince kullanıcıya AYNEN yaz ve dur)
> ✅ Etsy güncelleme görevi tamamlandı: [güncellenen ilanların listesi; yapılamayan bir şey varsa nedeni].
> Bu tek seferlik bir görevdi. Lütfen **bulut oturumuna geri dönün** ve orada **"geri geldim"** yazın; proje oradan kaldığı yerden devam edecek.
