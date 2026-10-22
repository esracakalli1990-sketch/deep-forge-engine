# PROJE "DEEP-FORGE" — MASTER MİMARİ, DURUM VE DEVİR TESLİM DOKÜMANI (HANDOVER SPEC)

> **DİKKAT (YENİ AJAN / GELİŞTİRİCİ EKİP İÇİN TALİMAT):**  
> Bu doküman, **ForgeDepthStudio** (Etsy B2B Dijital Üretim & Otonom Trafik Fabrikası) projesinin tek gerçeği (Single Source of Truth) olarak hazırlanmıştır. Kullanıcıyla iletişim kurarken veya yeni kod üretirken bu dokümandaki kurallara, klasör yapısına ve mevcut ilerleme durumuna **%100 sadık kalınacaktır.** Tamamlanmış aşamaları tekrar önermeyin; doğrudan **"Sıradaki Aktif Görev"** bölümünden devam edin.

---

## 1. PROJE KİMLİĞİ VE STRATEJİK VİZYON

* **Proje Kod Adı:** DEEP-FORGE
* **Etsy Mağaza Adı:** `ForgeDepthStudio` (`https://forgedepthstudio.etsy.com`)
* **Sistem Tipi:** Otonom Etsy B2B/Üretici Tedarik & Dış Trafik Fabrikası
* **Hedef Pazar:** ABD, Kanada, İngiltere, Avustralya (Evinde/atölyesinde $3.000 - $10.000 değerinde Lazer Kesim, Fiber Galvo, CNC Router, UV/DTF Baskı makinesi olan ancak 3D modelleme/tasarım yeteneği olmayan küçük işletmeler ve zanaatkarlar).
* **Temel Felsefe:** 
  1. Herkesin battığı düşük kârlı son tüketici çöplüğünden (Wall Art, POD Tişört, $1 Clipart) uzak durmak.
  2. %100 kâr marjlı ve sıfır fiziksel üretim maliyetli **"B2B Üretici Hammaddesi"** (Ticari Dijital Varlıklar) üretmek.
  3. Etsy'de kuru kuruya ürün yükleyip organik arama beklemek yerine; Python tabanlı görsel/video üretim fabrikası ve otonom sosyal medya (Pinterest + YouTube Shorts/TikTok) botlarıyla dışarıdan sıcak trafik akıtmak.

---

## 2. HEDEF ÜRÜN GRUPLARI (3 ANA SÜTUN)

1. **Sütun 1 (AKTİF — Şu An Üretilen):** **3D İllüzyon Lazer Kazıma Derinlik Haritaları (3D Relief Depth Maps / Grayscale PNG)**
   * LightBurn, EZCAD, Glowforge, xTool ve CNC Router'lar için ahşap, pirinç (brass coin) ve arduvaz taşına (slate coaster) derin 3 boyutlu rölyef kazıma yapmayı sağlayan `4000x4000 px`, `300 DPI`, `8-bit Grayscale` kalibre edilmiş PNG dosyaları.
   * **Teknik Farkımız:** Her ürün hem **Standard** (Siyah = En derin) hem de **Inverted** (Beyaz = En derin) versiyonla teslim edilir. Arka planlar tam saf siyahtır (`#000000`).
2. **Sütun 2 (PLANLANAN):** **20oz Skinny Tumbler Tam Sarım (Seamless Sublimation Wraps) + DTF Paketleri**
   * Kenar pikselleri Python ile matematiksel olarak eşitlenmiş (`9.3" x 8.2"`, 300 DPI) %100 kusursuz birleşimli 50'li mega ticari paketler.
3. **Sütun 3 (PLANLANAN):** **Küçük İşletme Üretim & Maliyet Otomasyon Tabloları (Google Sheets + Apps Script)**
   * Lazer/CNC esnafının malzeme firelerini, makine saatlik maliyetini ve Etsy komisyonlarını hesaplayan hazır ticari tablolar.

---

## 3. KESİN OPERASYONEL KURALLAR (KIRMIZI ÇİZGİLER)

1. **Suspend (Kapanma) Kalkanı & Isındırma Protokolü:**
   * Kesinlikle VPN veya Proxy kullanılmaz; her zaman temiz yerel IP ve sabit Chrome profili kullanılır.
   * **İlk 72 Saat Isındırma Kuralı:** Mağaza açılışında tek seferde 50 ürün yüklenmez! İlk koleksiyon (6 ürün) yüklendikten sonra Etsy'nin anti-spam/bot filtresini tetiklememek için mağaza 48-72 saat dinlendirilir. Bu sürede yeni ürün eklenmez; arka planda dış trafik ve istihbarat modülleri çalıştırılır.
2. **Etsy Dosya Yükleme Kuralları (Çok Kritik — Daha Önce Karışıklık Yaşandı, Tekrarlanmayacak!):**
   * **Tekli Ürünlerde (`$4.99`):**
     * **Photo & Video Alanı (Vitrin):** Yalnızca **4 adet `.jpg` Mockup** (`01_Wood_Mockup.jpg` [Kapak/Featured], `04_Comparison_Split_Guide.jpg`, `02_Brass_Mockup.jpg`, `03_Slate_Coaster_Mockup.jpg`) ve **1 adet `.mp4` vitrin videosu** (`05_Listing_Video.mp4`) yüklenir.
     * **Digital Files Alanı (Müşterinin İndireceği Alan - Maks 5 Dosya Sınırı):** Buraya Mockup fotoğrafları, video, ZIP veya PDF **YÜKLENMEZ!** Sadece **2 adet asıl üretim dosyası** (`*_3D_DepthMap_300DPI.png` ve `*_3D_DepthMap_INVERTED_300DPI.png`) yüklenir.
   * **Çoklu Paketlerde / Mega Bundle (`$12.99`):**
     * Etsy'nin 20 MB dosya boyutu sınırı nedeniyle yüksek çözünürlüklü ZIP arşivleri **Google Drive**'a yüklenir (Erişim izni: *"Bağlantıya sahip olan herkes görüntüleyebilir"*).
     * **Digital Files Alanı:** Buraya ZIP dosyaları değil, sadece müşteriyi Google Drive indirme linkine yönlendiren şık tasarımlı **Teslimat PDF Kılavuzu** yüklenir.
3. **Etsy AI & Yaratıcılık Politikası Uyumu:**
   * "How it's made" sekmesinde: `I did` -> `A finished product` -> `2020-2026` ve içerik üretim biçimi olarak `"Created by me with the help of an AI generator"` seçilir.
4. **Token ve İletişim Verimliliği Kuralı:**
   * Kullanıcıdan gereksiz yere her adım için ekran görüntüsü istenerek token/limit harcanmaz. Tek seferde net, kopyala-yapıştır şablonlar ve tam çalışan Python scriptleri verilir.

---

## 4. ŞU ANA KADAR TAMAMLANANLAR (FAZ 1 & FAZ 2 — %100 BİTTİ)

### 4.1. Mağaza Kurulumu ve Kurumsal Kimlik (TAMAMLANDI)
* **Mağaza:** `ForgeDepthStudio` açıldı, kimlik ve banka/vergi doğrulamaları sıfır hatayla geçildi.
* **Görsel Kimlik:** `500x500 px` Mağaza Logosu ve `1600x400 px` Büyük Mağaza Banner'ı oluşturuldu ve yüklendi.
* **Kurumsal Metinler:**
  * *Shop Title:* `3D Laser Engraving Depth Maps & CNC Relief PNG Files`
  * *Shop Announcement (Duyuru):* Canlı mağaza düzenleme ekranından eklendi.
  * *Shop Story (Hikaye & Başlık):* Kalibrasyon, algoritmik derinlik haritası ve B2B atölye vurgulu kurumsal hikaye eklendi.
  * *Etsy Search Visibility:* Tüm eksik bildirimler giderildi, mağaza tam puanla yayında.

### 4.2. Yerel Python Üretim Fabrikası (`forge/` Klasörü — TAMAMLANDI)
Kullanıcının bilgisayarında (`forge` dizininde) çalışan çekirdek üretim scriptleri kuruldu ve ilk koleksiyonu başarıyla üretti:
* `batch_factory.py`: Ham görselleri alır; `4000x4000 px` 300 DPI 8-bit grayscale **Standard** ve **Inverted** Depth Map PNG'lerine çevirir. Ardından OpenCV/Pillow ışıklandırma ve kabartma matematiğiyle **Ahşap (`01_Wood_Mockup.jpg`)**, **Pirinç (`02_Brass_Mockup.jpg`)**, **Arduvaz Taşı (`03_Slate_Coaster_Mockup.jpg`)**, **Teknik Karşılaştırma (`04_Comparison_Split_Guide.jpg`)** görsellerini ve **FFmpeg Lazer Tarama Videosunu (`05_Listing_Video.mp4`)** üretir.
* `bundle_packager.py`: 5 ürünü tek bir Mega Bundle çatısında toplar, vitrin kolaj görsellerini, ZIP arşivlerini ve içinde Google Drive linki + kullanım rehberi + ticari lisans bulunan **PDF Teslimat Kılavuzunu** üretir.
* `seo_generator.py`: Etsy 2026 algoritmasına uygun, 140 karakteri aşmayan başlıkları, 20 karakter sınırına tam uyumlu 13 uzun kuyruk (long-tail) etiketi ve teknik LightBurn/EZCAD başlangıç tablosu içeren açıklamaları (`ETSY_LISTING_SEO.txt` ve `ALL_LISTINGS_READY.md`) üretir.
* `traffic_cannon.py`: Her ürün için `outputs/07_Traffic_Cannon/` klasörüne `1080x1920` (9:16) dikey YouTube Shorts/TikTok lazer dönüşüm videolarını (`.mp4`), `1000x1500` (2:3) Pinterest Pin görsellerini (`.jpg`) ve `SOCIAL_CAPTIONS_READY.txt` metin dosyasını üretir.

### 4.3. Yayındaki Aktif Ürünler (6 İlan — `Active`, Stok: `999`)
1. **`01_Fenrir_Wolf`** — `$4.99` (Tekli İlan - 2 PNG + 4 Mockup + 1 Video)
2. **`02_Yggdrasil_Tree_of_Life`** — `$4.99` (Tekli İlan - 2 PNG + 4 Mockup + 1 Video)
3. **`03_Valkyrie_Warrior`** — `$4.99` (Tekli İlan - 2 PNG + 4 Mockup + 1 Video)
4. **`04_Vegvisir_Viking_Compass`** — `$4.99` (Tekli İlan - 2 PNG + 4 Mockup + 1 Video)
5. **`05_Odin_Allfather`** — `$4.99` (Tekli İlan - 2 PNG + 4 Mockup + 1 Video)
6. **`06_Norse_Mythology_5in1_Mega_Bundle`** — `$12.99` (Mega Paket - Google Drive Linkli PDF + Kolaj Mockuplar + Video)
   * *Not:* Tüm ilanların kapak (Featured) fotoğrafları bitmiş fiziksel sonuç (`Wood` / `Brass` Mockup) olarak ayarlandı ve videoları eklendi.

---

## 5. TEKNİK KLASÖR MİMARİSİ (MEVCUT + İNŞA EDİLECEK)

```text
forge/
├── batch_factory.py               # [MEVCUT] Depth Map + 4 Mockup + Kare Video Üretici
├── bundle_packager.py             # [MEVCUT] 5-in-1 Mega Bundle + Google Drive PDF Üretici
├── seo_generator.py               # [MEVCUT] Başlık, 13 Etiket ve Açıklama Üretici
├── traffic_cannon.py              # [MEVCUT] 9:16 Dikey Shorts Video + 2:3 Pinterest Pin Üretici
├── auto_publisher.py              # [SIRADAKİ GÖREV] Playwright Otonom Pinterest & Shorts Yükleyici Bot
├── scout_engine.py                # [SIRADAKİ GÖREV] Playwright Etsy Bestseller & Trend Kazıyıcı Bot
├── bot_profile/                   # [OLUŞTURULACAK] Playwright kalıcı tarayıcı çerez/oturum klasörü
└── outputs/
    ├── 01_Fenrir_Wolf/            # [MEVCUT] Üretilen tüm ürün dosyaları ve ETSY_LISTING_SEO.txt
    ├── 02_Yggdrasil_Tree_of_Life/ # [MEVCUT]
    ├── 03_Valkyrie_Warrior/       # [MEVCUT]
    ├── 04_Vegvisir_Viking_Compass/# [MEVCUT]
    ├── 05_Odin_Allfather/         # [MEVCUT]
    ├── 06_Norse_Mythology_Bundle/ # [MEVCUT] Mega Bundle dosyaları + Müşteri PDF'i
    ├── 07_Traffic_Cannon/         # [MEVCUT] 9:16 MP4 Shorts videoları + Pinterest Pinleri
    └── hot_trends.json            # [OLUŞTURULACAK] scout_engine.py tarafından kazınan sıcak nişler
```

---

## 6. SIRADAKİ AKTİF GÖREVLER VE YOL HARİTASI (FAZ 3 & FAZ 4)

Şu an **Isındırma Protokolü (72 Saat)** içindeyiz. Mağazaya yeni ürün yüklemeden, sırasıyla şu **3 otonom modülü** kodlayıp devreye alacağız:

### ADIM 1 (ŞU ANKİ AKTİF GÖREV): Otonom Dış Trafik Yükleyici Bot (`auto_publisher.py`)
* **Amaç:** Kullanıcının her gün elle Pinterest'e ve YouTube Shorts / TikTok'a video/görsel yükleme zahmetini ortadan kaldırmak.
* **Teknik Çözüm:**
  * Python **Playwright (`launch_persistent_context`)** kullanılarak `forge/bot_profile` dizininde kalıcı bir Chrome oturumu açılacak.
  * Kullanıcı ilk çalıştırmada Pinterest (`ForgeDepthStudio`) ve YouTube Studio hesaplarına 1 kez giriş yapacak.
  * Script (`auto_publisher.py`), `outputs/07_Traffic_Cannon/` klasöründeki henüz yayınlanmamış dikey videoları (`*_Vertical_Short_9x16.mp4`) ve pin görsellerini (`*_Pinterest_Pin_2x3.jpg`) sırayla alacak.
  * Otomatik olarak `pinterest.com/pin-builder/` ve `studio.youtube.com` üzerinden başlığı, açıklamayı ve **doğrudan Etsy mağaza/ürün linkini** girerek paylaşımı yapacak.
  * Paylaşılan ürünleri `published_log.json` dosyasına kaydedecek; böylece Windows Görev Zamanlayıcı (veya Hostinger VPS / n8n) ile her gün belirli saatlerde sıfır insan müdahalesiyle çalışacak.

### ADIM 2: Lazer Toplulukları "Truva Atı" (Lead Magnet) Paketi (`lead_magnet_builder.py`)
* **Amaç:** Reddit (`r/laserengraving`, `r/LightBurn`, `r/xToolOfficial`) ve Facebook Lazer gruplarındaki hazır makine sahiplerini doğrudan mağazaya çekmek.
* **Teknik Çözüm:**
  * Kullanıcının bu gruplarda *"Lazer makineleri için özel Z-ekseni kalibrasyonlu 3D depth map algoritması geliştirdik, kendi makinenizde test etmeniz için 1 adet 4000x4000px 300 DPI dosyayı ücretsiz bıraktık"* diyerek paylaşabileceği **Ücretsiz Test Paketi + İçinde Mağaza İndirim Kancası Olan PDF** üretilecek.

### ADIM 3: Pazar İstihbarat ve Klonlama Botu (`scout_engine.py`)
* **Amaç:** 72 saatlik mağaza ısınma süresi biter bitmez hangi yeni koleksiyonları (Gothic, Celtic, Samurai, Wildlife, Tumbler Wrap vb.) üreteceğimizi veriye dayalı seçmek.
* **Teknik Çözüm:**
  * Playwright botu Etsy'de hedef kelimeleri tarayacak; `"X people bought this in the last 24 hours"`, `"In 20+ carts"` ve `"Bestseller"` rozetli ürünleri tespit edecek.
  * Yorumları `"Newest"` olarak sıralayıp son 7-14 günde yoğun yorum alan ürünlerin başlıklarını, 13 etiketini (sayfa kaynağındaki meta veriden) ve konseptini çekip `outputs/hot_trends.json` dosyasına kaydedecek.
  * Ardından bu JSON dosyası doğrudan `batch_factory.py` motoruna beslenerek günde 5-10 yeni paketin seri üretimine geçilecek.

---

## 7. YENİ OTURUM BAŞLATMA KOMUTU (PROMPT)

Başka bir yapay zeka ajanına veya yeni bir sohbete geçildiğinde sadece bu dosyayı (`DEEP_FORGE_MASTER_HANDOVER.md`) yükleyip şu komutu vermeniz yeterlidir:

> *"Ekteki `DEEP_FORGE_MASTER_HANDOVER.md` dosyasını oku. Bu bizim aktif projemizin anayasasıdır. FAZ 1 ve FAZ 2'yi (6 ürünün üretimi, Etsy mağaza kurulumu ve `traffic_cannon.py` ile dikey videoların/pinlerin üretimini) tamamladık. Şu an Bölüm 6 - ADIM 1'deyiz (`auto_publisher.py` — Playwright kalıcı oturum ile Pinterest ve YouTube Shorts'a sıfır el değmeden otomatik içerik yükleyen botun kodlanması). Bana hiçbir eski aşamayı tekrar anlatma, doğrudan ADIM 1'in (`auto_publisher.py`) kurulumu ve tam koduyla devam et."*