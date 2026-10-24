# Pinterest kurulum ve haftalık rutin (Faz C — kurucu için)

Karar (2026-10-24): trafik **yalnız Pinterest** üzerinden; YouTube/TikTok tüm işler bittikten sonra konuşulacak.
Bot / tarayıcı otomasyonu YOK (Pinterest kuralları otomatik erişimi yasaklar). Pinler Pinterest'in **kendi zamanlayıcısıyla** elle kurulur.

## 1. Hesap açılışı (tek sefer, ~15 dk)
1. **pinterest.com/business/create** → ücretsiz **Business** hesabı. E-posta: Etsy mağazasının e-postası. Ad: **ForgeDepthStudio**.
   Ülke/dil: hedef kitle ABD → dil **English**.
2. Profil: logo (`render_logo` çıktısı / Etsy mağaza logosu), kullanıcı adı `forgedepthstudio` (alınmışsa `forgedepthstudio3d`).
   Hakkında: `3D depth maps for laser engraving: Norse mythology relief designs for LightBurn, Glowforge & xTool. Instant download on Etsy.`
3. Web sitesi alanı: `https://forgedepthstudio.etsy.com`.
4. Ayarlar → **Claimed accounts / Talep edilen hesaplar**: Etsy seçeneği varsa mağazayı bağla (doğrula; menü adı değişebilir).
5. 2 adımlı doğrulamayı aç. VPN yok, kendi bilgisayarın/telefonun.

## 2. Panolar (ilk gün oluştur; adlar `traffic_cannon.py` ile birebir aynı olmalı)
| Pano | Açıklama (kopyala) |
|------|--------------------|
| 3D Depth Maps for Laser Engraving | Grayscale 3D depth maps and relief designs for laser engraving on wood, slate and brass. |
| LightBurn 3D Slice & Laser Engraving Tips | How depth maps become laser reliefs: 3D Slice tips, test grids and material ideas. |
| Norse Mythology Laser Engraving Designs | Viking and Norse mythology laser engraving designs: Fenrir, Valkyrie, Yggdrasil, Thor, Odin. |

## 3. İlan linkleri (bana bir kez gönder)
Etsy → ilanı aç → paylaş → linki kopyala. 6 linki (5 ürün + bundle) sohbete yapıştır; ben `links.json`'a yazıp takvimi linkli üretirim.
Etsy **Share & Save** programına kayıtlıysan oradaki paylaşım linklerini kullan (kendi linkinden gelen satışta ücret indirimi; şartları Etsy'de doğrula).
Link gelene kadar takvimdeki tüm pinler mağaza ana sayfasına gider (çalışır ama dönüşüm daha düşük).

## 4. Haftalık rutin (~15–20 dk, haftada 1)
1. `PINTEREST_SCHEDULE.md`'yi aç; o haftanın günlerini sırayla kur:
   **Oluştur → Pin** → görseli yükle → Başlık / Açıklama / Alt metin / Link kopyala → Pano seç → **Publish at a later date** → tarih + saat (TR saati parantezde yazılı).
2. İlk hafta günde **2 pin** (takvim varsayılanı). Hesap 2. haftadan sonra sorunsuzsa 3'e çıkarız.
3. Haftada birkaç kez 5 dk elle gezin: lazer/ahşap/Norse konulu başkalarının pinlerini kendi panolarına kaydet (doğal hesap davranışı).

## 5. Yapma listesi
- Takipçi/etkileşim satın alma, takip-bırak döngüsü, toplu grup panolarına spam YOK.
- Aynı görseli aynı gün birden çok panoya basma YOK (takvim zaten ayırıyor).
- Görsel/metinde "calibrated", CNC vaadi, kanıtlanamayan iddia YOK (kod zorlar).
- Mockup'lar render: görsellerde "mockup render" notu var, silme.

## 6. Ölçüm (haftada 1, C6)
Pinterest Analytics: gösterim, kaydetme, **outbound click**. Etsy Stats → Traffic sources → **Pinterest**: ziyaret, favori, satış.
Rakamları sohbete yaz (ya da ekran görüntüsü yerine 5 sayı); hangi pin tipinin (Hero / Process / Materials) çalıştığına göre sonraki seriyi ayarlarım.

## Teknik not (CSV toplu yükleme)
`pin_scheduler.py --media-base-url https://...` Pinterest toplu CSV'si üretir; ancak görsellerin herkese açık bir URL'de durması gerekir
(şu an böyle bir barındırma yok). Kolon formatı Pinterest yardım sayfasından doğrulanmalı. Bu yüzden birincil yol elle zamanlama.
