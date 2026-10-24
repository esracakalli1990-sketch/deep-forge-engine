# MARKET_RESEARCH — Pazar araştırması (2026-10-24, kurucu talebi; Faz D2'nin öne alınmış hali)

## Kurucu tespiti
Kategoride 100–120 parçalık setler ~$10 ve altında. Bizim 5'li bundle $12.99 (~$2.60/tasarım) → parça sayısıyla rekabet edemeyiz.
Hedef: Etsy'de kategorimizde **ne satıyor** tespit edip o nişlere girmek.

## Ön bulgular (web araması; satış verisi DEĞİL, sinyal)
- Depth map pazarı: tema setleri baskın. Coin (fiber lazer) setleri $13–25; dev arşivler (1000+ tasarım $99, 1500+ 16-bit $121); fiyatlar sürekli "%50 indirimde".
- Çok görülen satan temalar: coin setleri (askeri, burç, EDC, ABD 250. yıl), slate coaster setleri (dini, western/rodeo), 3D illusion / multilayer, kesme tahtası (charcuterie) tasarımları, **Noel/tatil** kapı-süs-tabela dosyaları, anahtarlık.
- Dev "500.000 tasarım" paketleri büyük olasılıkla derleme/telifsiz değil → kopyalanmaz, rakip sayılmaz.
- YouTube (son 12 ay, ilk 15 videonun medyan izlenmesi; üretici ilgisi sinyali): fiber laser coin 165K, cutting board 122K, depth map 45K, 3D illusion 34K, slate coaster 30K, Christmas ornament 24K, keychain 10K, multilayer 4K.
- Mevsim: Ekim sonu → lazer atölyeleri Kasım–Aralık hediye üretimi için dosyayı **Kasım başında** alır. Noel temalı dosyalar için pencere şimdi.

## Gerçek veri yöntemi (kurallara uygun, kazıma yok)
- Kurucu kendi tarayıcısında Etsy araması yapar; **EverBee** (Chrome eklentisi, ücretsiz katman; tahmini aylık satış/gelir, ~%80 doğruluk iddiası) açıkken sonuç sayfasının ekran görüntüsü → Claude okur, tabloya döker, puanlar.
- Alternatif/ek: **eRank** (ücretsiz katman; anahtar kelime arama hacmi/rekabet).
- Her niş için: ilk 20 ilan → fiyat, tasarım sayısı, yorum sayısı, Bestseller rozeti, (EverBee) aylık satış tahmini, ilan yaşı.
- Puan = talep (satış/yorum) ÷ rekabet (ilan sayısı) × bizim hattın uygunluğu (depth map/PNG ile üretilebilir mi).

## Kontrol edilecek niş listesi (ilk tur)
1. christmas ornament laser file / christmas depth map
2. slate coaster laser engraving bundle (christmas / western / religious)
3. fiber laser coin depth map (military / zodiac / EDC)
4. 3d illusion laser engraving file
5. cutting board laser engraving file
6. depth map bundle (genel; fiyat/parça sayısı referansı)
7. norse / viking laser file (mevcut nişimiz — kıyas)

## Derin tur (2026-10-24, kurucu: "sınırsız düşün, her yolu dene")
Denenen kaynaklar: web arama (Etsy market sayfaları, EtsyHunt, sektör blogları), YouTube Data API (üretici ilgisi), Etsy listing snippet'leri.
Erişilemeyen: Etsy/EtsyHunt sayfalarının doğrudan okunması (bulut ağ politikası: etsy.com, openapi.etsy.com, etsyhunt.com engelli).

### YouTube — son 12 ay, ilk 20 video medyan izlenme (üretici talebi sinyali)
| Konu | Medyan |
|------|--------|
| fiber laser 3d engraving coin | 75.7K |
| laser engraving photo 3d | 75.4K |
| fiber laser deep engraving relief | 65.0K |
| laser engraved knife fiber | 30.7K |
| laser engraving tumbler 3d | 28.1K |
| challenge coin fiber laser | 17.1K |
| christmas ornament laser engraving ideas | 12.2K |
| norse viking laser engraving | **1.2K** (mevcut nişimiz zayıf) |
| 16 bit depth map fiber laser | 0.7K (az içerik = az rakip/eğitim boşluğu) |

### Etsy sinyalleri (snippet; doğrulanmadı)
- Coin depth map satıcıları (ör. BestOfEngraving): listing sayfalarında 1.9K ve 4.9K "sales" görülüyor; ürün = **STL + PNG height map** birlikte; tek coin $3–15, temalı coin setleri $10–25.
- Rakiplerde 16-bit PNG seçeneği var (fiber/EZCAD 3D için daha yumuşak katman); biz 8-bit veriyoruz.
- EtsyHunt kategori sıralamaları (haftalık/toplam satış tahmini) mevcut; laser-cut Noel köyü / Noel mega bundle örnekleri haftalık ~37–55 satış. Laser-cut SVG nişi çok kalabalık.

### Ön sonuç
1. Norse/Viking tek başına zayıf niş → koru ama genişleme yapma.
2. En güçlü uyum: **fiber lazer coin / derin rölyef depth map** (askeri/challenge coin, hayvan, kafatası, kartal/ABD, burç, din) — bizim ürün tipimizle birebir.
3. Ürün farkı: **16-bit PNG + STL** ekle (rakip standardı), temalı setler (20–50 tasarım) makul fiyat.
4. Mevsim: Noel temalı depth map coin/ornament seti — pencere Kasım başı.

### Gerçek satış verisi için yol haritası (kurallara uygun)
- **Etsy Open API v3** (resmi): anahtar kelime → ilk 100 ilan → mağaza `transaction_sold_count`, ilan favori/yaş → satış hızı tahmini. `scout_engine.py` (D2 öne alındı). Gerekli: kurucunun ücretsiz Etsy geliştirici uygulaması (API anahtarı); çalıştırma kurucu PC'de veya bulut ağ izni (openapi.etsy.com).
- **EverBee** (ücretsiz eklenti) ekran görüntüleri: hemen başlanabilir.
- Mağaza "X sales" sayfaları + yorum hızı (yorum × ~10–20 ≈ satış, kaba).
