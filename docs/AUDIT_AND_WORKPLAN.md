# DEEP-FORGE — Yönetici Denetim Raporu ve İş Planı

Hazırlayan: Claude (Yönetici + Baş Mühendis) · Kapsam: repo kodu, `docs/DEEP_FORGE_MASTER_HANDOVER.md`, üretilen çıktılar, plan edilen modüller.
Yöntem: Her bulgu ya kodda/çıktıda ölçülerek ya da çalıştırılarak doğrulandı. "(doğrula)" etiketi, bu oturumdan teyit edemediğim platform kuralı/ücret bilgisidir.

> **Dürüst not — "kesin kazanç":** Hiçbir plan kazancı garanti edemez. Bu plan; ürün kalitesini kanıtlanabilir kılmayı, hesap/mağaza kaybı riskini sıfıra yaklaştırmayı ve her kararı ölçülen veriye bağlamayı hedefler. Kazanç olasılığını en yükseğe çıkaran yol budur.

---

## 1. Yönetici özeti

1. **Ürünün çekirdeğinde ölçülmüş bir kalite sorunu var.** Depth map'ler AI render'ının *parlaklığından* türetiliyor; render'daki ışık derinliğe gömülü. Kanıt: fiziksel olarak her açıda aynı yükseklikte olan dış halka, haritada açıya göre 127–231 arasında değişiyor (derinlik aralığının **%41'i**). Lazerde "3D illüzyon" görünümüne yardım eder; **CNC / 3D Slice'ta halka eğik oyulur.** İlanlar "CNC Router Relief" vaat ediyor → iade/kötü yorum riski.
2. **Kendi kırmızı çizgimizi çiğneyen metinler canlıda olabilir.** "pre-calibrated" ve "precision-calibrated" ifadeleri SEO açıklamalarında, karşılaştırma görselinde ve AI beyanında var. Kalibrasyon yapmıyoruz.
3. **Planlanan iki modül hesabı/mağazayı riske atıyor:** `auto_publisher.py` (Playwright ile Pinterest/YouTube/TikTok yükleme) ve `scout_engine.py` (satıcı IP + profiliyle Etsy kazıma). İkisinin de kurallara uygun, aynı işi yapan resmi yolu var.
4. **Repo tek gerçek kaynak değil.** Kullanıcının `forge/` klasöründeki kod (traffic_cannon, 06_/07_ klasör adları) repoda yok; repo kodu bu adlarla bundle SEO'sunu sessizce atlıyor.
5. **Somut SEO hatası:** Vegvisir ilanında "vegvisir" kelimesi 13 etiketin hiçbirinde yok; başlıkta ürün adı iki kez geçiyor.

**Öneri:** Yeni modül yazmadan önce 3 günlük "doğruluk ve hijyen" fazı (Faz A), ardından ürün kalitesinin gerçek makinede kanıtlanması (Faz B). Trafik ve büyüme (Faz C–D) bunların üstüne kurulur.

---

## 2. Bulgular

Seviye: **KRİTİK** = para/hesap kaybı riski · **YÜKSEK** = satış/itibar kaybı · **ORTA** = verim/sürdürülebilirlik · **DÜŞÜK** = iyileştirme.

| ID | Seviye | Alan | Bulgu | Kanıt | Çözüm |
|----|--------|------|-------|-------|-------|
| K1 | KRİTİK | Ürün kalitesi | Işık depth'e gömülü (luminance ≠ yükseklik) | Dış halka 8 yönde 127–231; fark %41 (`01_Fenrir_Wolf` depth map) | B1 de-lighting + B2 ışıksız üretim prompt'ları + B3 gerçek makine testi; o zamana kadar CNC vaadini yumuşat |
| K2 | KRİTİK | Uyum / doğruluk | "pre-calibrated", "precision-calibrated" iddiaları | `seo_generator.py:37,210,231`, `batch_factory.py:440` | A1: metinleri düzelt, canlı ilanlar için yapıştırılacak düzeltme şablonu |
| K3 | KRİTİK | Hesap güvenliği | `auto_publisher` UI otomasyonu: YouTube/Pinterest/TikTok kullanım şartları otomatik erişimi yasaklar | Handover Bölüm 6 Adım 1 | C1–C2: Pinterest toplu CSV + yerel zamanlayıcı / resmi API'ler |
| K4 | KRİTİK | Mağaza güvenliği | `scout_engine` satıcının IP ve Chrome profiliyle Etsy kazıyacak; Etsy botları yasaklar, mağaza askıya alınabilir | Handover Bölüm 6 Adım 3 + Kural 3.1 | D2: Etsy Open API v3 (şartları doğrula) + Pinterest/Google Trends + manuel kısa liste |
| Y1 | YÜKSEK | SEO | Vegvisir: 0 ürüne özel etiket, başlıkta ad tekrarı | `seo_generator` gerçek adlarla çalıştırıldı; 13 etiketin tamamı genel | A2: Vegvisir + Yggdrasil profili; yedek profilin ad tekrarı ve etiket üretimi düzeltmesi |
| Y2 | YÜKSEK | Kod yönetimi | Repo ≠ kullanıcı `forge/`: `traffic_cannon.py` yok; bundle `06_Norse_Mythology_Bundle` adıyla `seo_generator` bundle'ı atlıyor | `list_bundles()` yalnız `_MEGA_BUNDLE*` arar | A4: kullanıcı kodunu repoya al, klasör sözleşmesini birleştir |
| Y3 | YÜKSEK | Teslimat | Bundle Drive linkine bağımlı: link paylaşılabilir (korsan), silinirse müşteri dosya alamaz | 5'li bundle'ın 2 ZIP'i 17,7 MB → Etsy'ye doğrudan sığar (3 dosya ≤ 5, her biri ≤ 20 MB) | A3: Kural 3.2 revizyonu: ≤20 MB parçalar Etsy'de, PDF yalnızca rehber |
| Y4 | YÜKSEK | Teslimat | Drive linki verilmezse PDF yer tutucu linkle üretiliyor (yalnızca uyarı) | `bundle_packager.py:489` | A3: link yoksa çıkış kodu ≠ 0 ile dur |
| Y5 | YÜKSEK | Doğruluk | Bundle açıklaması "Download from Etsy" + ZIP listesi; Kural 3.2 ile çelişki | `seo_generator.py:182,237,320` | A3 ile birlikte |
| O1 | ORTA | Kalite güvencesi | Otomatik test ve CI yok; bağımlılık sürümleri sabit değil (opencv 5.0.0.93, numpy 2.5.3, Pillow 12.3.0, reportlab 5.0.1 ile test edildi) | `requirements.txt` sürümsüz | A5: pytest + GitHub Actions + sürüm sabitleme |
| O2 | ORTA | Pazarlama | Lead magnet metni "Z-ekseni kalibrasyonlu algoritma" diyor; forum/grup kendini tanıtma kuralları | Handover Adım 2 | C4: doğru metin, topluluk kurallarına göre değer-öncelikli paylaşım |
| O3 | ORTA | Fikri mülkiyet | Marka adları (LightBurn, Glowforge, xTool, EZCAD) başlık/etiketlerde; uyumluluk anlatımı genelde kabul görür ama şikayette ilan kaldırılabilir (doğrula) | Başlık/etiketler | "for LightBurn" / "compatible with" kalıbı; marka adını ilk 40 karakterde tek tutma |
| O4 | ORTA | Ölçüm | Hiçbir KPI kaydı yok; kararlar veriye dayanmıyor | — | D5: haftalık 6 rakamlık metrik kaydı + karar raporu scripti |
| O5 | ORTA | Süreklilik | Tüm üretim tek bir kişisel bilgisayarda; bilgisayar giderse fabrika durur | Handover Bölüm 5 | A4 + A5: repo tek kaynak, CI'da çalışabilen hat |
| D1 | DÜŞÜK | Ürün | 16-bit PNG seçeneği CNC'de bantlanmayı azaltabilir (premium sürüm) | Hat 8-bit | B-fazı sonrası değerlendir |
| D2 | DÜŞÜK | Bilgi | "72 saat ısındırma" resmi Etsy kuralı değil, temkinli sezgi — korumak zararsız | — | Koru; kademeli yükleme kadansına dönüştür (D1) |

**Handover ile çelişkiler (karar gerekli):** Kural 3.2 (bundle her zaman Drive) ↔ Y3; Adım 1 yöntemi ↔ K3; Adım 3 yöntemi ↔ K4 ve Kural 3.1'in amacı; Adım 2 metni ↔ Kırmızı çizgi 4.

---

## 3. Birim ekonomi (varsayımlı, doğrula)

Varsayım: işlem ücreti %6,5; ödeme işleme ≈ %3 + $0,25 (Türkiye oranı farklı olabilir); çok adetli ilanda her satış $0,20 yenileme ücreti; banka para birimi USD değilse %2,5 döviz dönüşümü; Offsite Ads ile gelen satışta +%15 (yıllık $10k altında devre dışı bırakılabilir).

| Ürün | Fiyat | Tahmini ücret | Net | Net oran |
|------|-------|---------------|-----|----------|
| Tekli | $4,99 | ≈ $1,05 | ≈ $3,94 | %79 |
| 5'li bundle | $12,99 | ≈ $2,01 | ≈ $10,98 | %85 |

**Hedef matematiği:** Aylık $1.000 net ≈ 250 tekli satış ≈ günde 8–9 satış. %1,5–3 dönüşüm varsayımıyla ayda ~8.500–17.000 ilan ziyareti gerekir. 6 ilanla bu gerçekçi değil → **katalog büyüklüğü (100+ ilan) + dış trafik + bundle ile sepet ortalaması** birlikte gerekli. Gerçek dönüşüm oranı 30. günde ölçülüp bu tablo güncellenecek.

---

## 4. Hedef mimari — kurallara uygun otonomi

Otonomi seviyeleri: **L0** elle · **L1** tek komut script · **L2** zamanlanmış çalışma · **L3** resmi API ile uçtan uca, insan yalnızca "onay" verir.

| Hat | Bugün | Hedef | Yöntem (kurallara uygun) |
|-----|-------|-------|--------------------------|
| Üretim (görsel → depth → mockup → video) | L1 | L2 | `batch_factory` + QA kapısı (ölçülebilir kalite eşikleri) + CI |
| SEO / ilan metni | L1 | L2 | `seo_generator` (profil + test) |
| Etsy'ye ilan yükleme | L0 | L3 | Etsy Open API v3: taslak ilan + görsel + video + dijital dosya yükleme (uygulama onayı gerekir, doğrula); kurucu yalnız "Publish" der |
| Pinterest | L0 | L2 | Pinterest toplu pin CSV yüklemesi + yerel zamanlama (doğrula); sonra Pinterest API v5 (erişim onayı gerekir) |
| YouTube Shorts | ? | L2–L3 | Kurucunun mevcut sistemi veya YouTube Data API (doğrulanmamış projelerde yüklemeler gizli kalır, denetim başvurusu gerekir — doğrula) |
| TikTok | L0 | L2 | Yerel zamanlayıcı; Content Posting API denetimli (doğrula) |
| Pazar istihbaratı | — | L2 | Etsy Open API v3 + Pinterest Trends + Google Trends + manuel kısa liste — **kazıma yok** |
| Ölçüm | — | L1 | Haftalık 6 rakam (ziyaret, favori, sipariş, gelir, en iyi kaynak, en iyi ilan) → `metrics.csv` → karar raporu |

**Kural:** Hiçbir modül, satıcı hesabının oturumunu veya IP'sini otomatik tarama/yükleme için kullanmaz. Yayın her zaman ya resmi API ya da platformun kendi zamanlayıcısıyla yapılır.

---

## 5. İş planı

Sahip: **C** = Claude (kod, test, rapor) · **K** = Kurucu (hesap, yapıştırma, makine) · **A** = Gemini Argon (strateji görüşü).

### Faz A — Doğruluk ve hijyen (Gün 0–3, ısındırma içinde, yeni ilan yok)
| # | Görev | Sahip | Kabul kriteri |
|---|-------|-------|---------------|
| A1 | "calibrated" iddialarını tüm kod/metinden çıkar; canlı 6 ilan için düzeltilmiş açıklama + AI notu şablonu | C → K yapıştırır | `grep -i calibrat` kodda 0 sonuç; 6 ilan güncel |
| A2 | Vegvisir + Yggdrasil_Tree_of_Life profili; yedek profilde ad tekrarı yok, ürüne özel ≥4 etiket | C | Gerçek adlarla test: her ilanda ürün adı başlıkta 1 kez, ≥4 özel etiket |
| A3 | Bundle teslimi: ≤20 MB parçalar Etsy'de (karar), PDF rehber; link yoksa paketleyici durur; bundle açıklaması düzeltilir | C (+K karar) | Placeholder ile çalıştırma → çıkış kodu 1; açıklama Kural 3.2'nin yeni hâliyle uyumlu |
| A4 | `forge/` klasöründeki tüm kodu (traffic_cannon dahil) repoya al; 06_/07_ klasör sözleşmesini birleştir | K yükler → C birleştirir | Repo = çalışan kod; `seo_generator` 06_ bundle'ı tanır |
| A5 | pytest (sentetik girdiyle uçtan uca) + GitHub Actions + `requirements.txt` sürüm sabitleme | C | CI yeşil; her push'ta testler çalışır |

### Faz B — Ürün kalitesini kanıtla (Hafta 1–2)
| # | Görev | Sahip | Kabul kriteri |
|---|-------|-------|---------------|
| B1 | De-lighting: düşük frekanslı ışık bileşenini çıkaran işlem (halka testi ölçüt) | C | Dış halka açısal farkı %41 → <%10; detay korunur (görsel QA) |
| B2 | Işıksız / depth-style AI üretim prompt kütüphanesi (kaynakta düzeltme) | C + A | 5 deneme görselinde halka farkı <%10 |
| B3 | Gerçek makine testi: 3–5 lazer/CNC sahibine ücretsiz dosya (B-faz testçileri = lead magnet); izinli fotoğraflar ilan görseline | K | ≥3 gerçek kazıma fotoğrafı + geri bildirim |
| B4 | Konumlandırma kararı: "3D illusion grayscale engraving" ana vaat; CNC vaadi B1–B3 sonucuna göre | A + K | Başlık/etiket politikası güncellenir |

### Faz C — Kurallara uygun trafik (Hafta 1–3)
| # | Görev | Sahip | Kabul kriteri |
|---|-------|-------|---------------|
| C1 | `traffic_cannon` çıktılarından Pinterest toplu CSV + 2 haftalık yayın takvimi üreten `pin_scheduler.py` | C | CSV yükleme hatasız; günde 3–5 pin takvimi |
| C2 | YouTube: kurucunun mevcut sisteminin yöntemi öğrenilir; API ise ona bağlanır, değilse Data API + denetim başvurusu | K bilgi → C | Shorts yayını resmi yolla |
| C3 | Satıcının kendi paylaşım linkleri (Share & Save — ücret indirimi, doğrula) tüm pin/video açıklamalarında | C | Tüm sosyal metinlerde doğru link |
| C4 | Lead magnet (`lead_magnet_builder.py`): doğru metin, ücretsiz dosya + kupon, topluluk kurallarına uygun gönderi şablonları | C → K paylaşır | Her topluluk için kural kontrol listesi |

### Faz D — Büyüme motoru (Hafta 2–8)
| # | Görev | Sahip | Kabul kriteri |
|---|-------|-------|---------------|
| D1 | Haftalık koleksiyon kadansı: 5 tasarım/hafta (+1 bundle/2 hafta) | K üretir (C hattı) | 8. haftada ~40–45 ilan |
| D2 | `scout_engine` = resmi kaynaklı istihbarat (Etsy API + Trends) → `hot_trends.json` | C | Kazıma yok; haftalık niş önerisi |
| D3 | `listing_uploader.py`: Etsy API ile taslak ilan (görsel, video, dosya, SEO) | C (+K uygulama başvurusu) | 1 komutla 5 taslak; K yalnız Publish |
| D4 | Etsy'nin kendi teklif araçları (favori/sepet teklifleri, sezon indirimleri — doğrula) + fiyat testi (tekli $4,99 ↔ $5,99) | K + C analiz | 30 günlük karşılaştırma |
| D5 | `metrics.csv` + `weekly_report.py` (karar önerisi üretir) | C | Her pazartesi 1 sayfalık rapor |

### Faz E — Yeni sütunlar (Ay 2–3, veriyle karar)
- **Önce Sütun 3** (lazer/CNC maliyet tabloları, Sheets + Apps Script): rekabet düşük, fiyat yüksek ($15–29 aralığı hedef, doğrula), aynı müşteri kitlesi → çapraz satış.
- **Sonra Sütun 2** (tumbler wrap): kalabalık pazar; ancak Faz D verisi talep gösterirse.

---

## 6. Karar kapıları ve KPI'lar (başlangıç hedefleri — 30. günde kalibre edilir)

| Gün | Ölçüt | Eşik | Altındaysa |
|-----|-------|------|-----------|
| 7 | Ziyaret / favori | ≥150 ziyaret, ≥10 favori | Trafik (C) öncelik |
| 30 | Dönüşüm | ≥%1 (≥500 ziyarette) | Görsel/fiyat/başlık revizyonu |
| 30 | Ret/iade/şikayet | 0 kalite şikayeti | Faz B'ye dön, vaadi daralt |
| 60 | Katalog + satış | ≥40 ilan, ≥30 satış | Niş değiştir (D2) |
| 90 | Net gelir | Kurucunun belirleyeceği hedef | Sütun 3'ü öne çek |

---

## 7. Risk matrisi (özet)

| Risk | Olasılık | Etki | Önlem |
|------|----------|------|-------|
| Etsy mağaza askıya alma (bot/kazıma) | Orta (K4 uygulanırsa yüksek) | Ölümcül | Kazıma yok; resmi API |
| Sosyal hesap kapanması (UI bot) | Orta-yüksek | Yüksek | Resmi API / yerel zamanlayıcı |
| Kalite şikayeti / iade (K1) | Orta | Yüksek | Faz B, vaadi daraltma |
| Yanıltıcı iddia (K2) | Yüksek (şu an canlıda olabilir) | Orta | A1 |
| Drive linki sızıntısı / kırık link | Orta | Orta | A3 |
| Marka adı şikayeti | Düşük | Orta | "compatible with" kalıbı |
| Tek bilgisayar bağımlılığı | Orta | Yüksek | A4 + A5 |

---

## 8. Kurucudan gereken kararlar

1. **Kural 3.2 revizyonu:** ≤20 MB parçaları Etsy'ye doğrudan yükleyelim mi (Drive yalnız 5 dosyaya sığmayan büyük paketler için)?
2. **Adım 1 yöntemi:** Mevcut Shorts otomasyonunuz hangi yolla yüklüyor (resmi API mi, tarayıcı mı)? Pinterest için toplu CSV + zamanlama ile başlayalım mı?
3. **Adım 3 yöntemi:** `scout_engine` yalnız resmi kaynaklarla (Etsy API + Trends) mı? (Öneri: evet.)
4. **Konumlandırma:** B fazı bitene kadar CNC vaadini yumuşatıp "3D illusion laser engraving" ana mesaj olsun mu?
5. **Faz A'ya başlama onayı** ve `forge/` klasöründeki kodun repoya yüklenmesi.

---

## 9. Karar kaydı ve ilerleme

**2026-10-23 — kurucu kararları**
- `traffic_cannon.py` yok (handover'daki "MEVCUT" bilgisi yanlış) → Faz C'de kurallara uygun sıfırdan yazılacak.
- Kural 3.2 revize: bundle **doğrudan Etsy'den** teslim (ZIP parçaları + PDF). Drive yalnız 5 dosyaya sığmayan paketler için.
- Konumlandırma: **lazer odaklı**; CNC vaadi başlık/etiket/rozetten kaldırıldı, açıklamada dürüst uyarı.
- Faz A onaylandı.

**Faz A durumu (kod tarafı tamam, testlerle doğrulandı — 9/9 geçti):**
- A1 ✅ "calibrated" iddiaları tüm kod/metinlerden çıktı; rozetler: "LIGHTBURN & LASER READY", "OPTIMIZED FOR LASER ENGRAVING", "...xTool & EZCAD Ready".
- A2 ✅ Vegvisir + Yggdrasil Tree of Life profilleri; yedek profilde ad tekrarı yok; ≥4 ürüne özel etiket kuralı kodda.
- A3 ✅ `--delivery etsy` (varsayılan) / `drive` (link zorunlu); Etsy 5 dosya / 20 MB kontrolü; `bundle_manifest.json`; SEO bundle metni teslim moduna göre.
- A4 ✅ Kullanıcı `forge/` = repo (birebir aynı).
- A5 ✅ `tests/test_pipeline.py` + GitHub Actions CI + bağımlılık alt sınırları.
- Ek hata düzeltmesi: karşılaştırma görselinde ürün adı numarasıyla basılıyordu ("01 FENRIR WOLF") → düzeltildi.
- **Kurucu tarafında bekleyen:** güncel `.py` dosyalarını `forge/`'a kopyalamak; `docs/LIVE_LISTING_FIXES.md` ile 6 ilanı güncellemek; bundle'a 3 dosyayı yüklemek; (önerilir) 01 ve 04 görsellerini yenilemek.

**2026-10-24 — Faz B onaylandı** (kurucu: "Onaylıyorum, başla"; kurucunun lazer makinesi yok → B3 test kiti, testçiler Faz C'de kurallara uygun bulunacak).
- B1 ✅ `remove_directional_light` (batch_factory): yönlü ışık izi, polar 1. harmonik ile yalnız dış bantlardan (r ≥ 0.50R) çıkarılır; merkez konuya dokunulmaz; eksen güveni < 0.5 ise uygulanmaz; `--no-delight` ile kapatılır. Ölçüt: dış bant eğimi medyanı (QA eşiği %10).
  Gerçek 5 üründe önce → sonra: Fenrir %10.5→5.4, Valkyrie %14.4→3.3, Yggdrasil %18.1→4.1, Thor %30.3→7.0, Odin %10.9→4.6 (detay korelasyonu 0.93–0.98). 11/11 test geçti.
  Sınır: küçük detayların kendi aydınlık/gölge yanları kalır → lazer odaklı konumlandırma doğru; kaynak görselde düz ışık şart (B2).
- B2 ✅ `docs/PROMPT_LIBRARY.md` (düz ışık kaynak görsel kalıpları + QA kapısı + manuel kontrol).
- B4 ✅ kurucu onayı: 5 ürün delight ile yeniden üretildi, bundle ZIP'leri yenilendi (PDF aynı); `PNG_GUNCELLEME.zip` + `docs/ONE_TIME_TASK_PNG_SWAP.md` (yerel oturum değiştirecek).
- B4 ✅ kurucu beyanı: 6 ilanın dijital dosyaları yerel oturumla değiştirildi (tekli 2 PNG, bundle 2 ZIP + PDF).
- B3 ✅ `make_test_kit.py`: 1 tasarım (Standard + Inverted) + 1 sayfalık `Test_Guide.pdf` + `FEEDBACK_FORM.txt` (5 soru). Etsy teşvikli yorum yasağı gereği kit yorum/satın alma karşılığı değil; alıntı yalnız yazılı izinle. Kurucunun lazeri yok → dağıtım Faz C'de (topluluk kurallarına uygun, spam yok). Geri bildirim gelince B1 eşikleri/ayar önerileri gözden geçirilecek.

**2026-10-24 — Faz C onaylandı.** Kurucu kararları: trafik **yalnız Pinterest**; YouTube/TikTok tüm işler bittikten sonra konuşulacak (C2 YouTube maddesi ertelendi). Pinterest hesabı yok → açılış rehberi.
- C1 ✅ `traffic_cannon.py`: ürün başına 3 pin (Hero / Process / Materials) + bundle pini, 1000x1500; `pins.json` + `SOCIAL_CAPTIONS_READY.txt`; "mockup render" notu; metinde CNC/"calibrated" yok (kod + test).
- C2 ✅ `pin_scheduler.py`: elle zamanlama takvimi (`PINTEREST_SCHEDULE.md`, ET + TR saati, günde 2, aynı ürün art arda yok), `links.json` (yalnız https etsy.com/etsy.me), opsiyonel toplu CSV (`--media-base-url`).
- `docs/PINTEREST_SETUP.md`: hesap, panolar, haftalık rutin, yapma listesi, ölçüm. 13/13 test geçti.
- Bekleyen: kurucudan 6 ilan linki; hesap açılışı. Sonra C5 (test kiti + topluluk şablonları), C6 (ölçüm tablosu).
- Kurucu kararı (2026-10-24): ilk etapta pinler **elle** (Pinterest zamanlayıcısı). Pinterest resmi API otomasyonu (`pin_publisher.py`) ve RSS otomatik yayını **tüm işler bittikten sonra**; yeni ilan olmadığı için acele yok.
- C5 ✅ `docs/COMMUNITY_PLAYBOOK.md`: kural kontrol listesi, aday topluluklar, Şablon A (reklamsız teknik ipucu + önce/sonra görseli), Şablon B (testçi çağrısı, yorum şartı yok), cevap şablonları.
- C6 ✅ `docs/WEEKLY_METRICS.md`: haftalık 7 sayı + karar kuralları + kayıt tablosu.
- Kurucu talebi: 16 pinin elle kurulumu yerel Claude oturumuna devredildi (`docs/ONE_TIME_TASK_PINTEREST_PINS.md`): tek seferlik, kullanıcı gözetiminde, insan hızında, ilk pin onaylı (Etsy görevleriyle aynı model). Sürekli/gözetimsiz tarayıcı botu kırmızı çizgisi aynen geçerli; kalıcı otomasyon = resmi API (sona).
- ✅ 16 pin yerel oturumla planlandı (kurucu beyanı, 2026-10-24): 26.10–03.11.2026, günde 2. İlk haftalık ölçüm 2026-11-02.

**2026-10-24 — Kurucu önceliği: pazar araştırması** (`docs/MARKET_RESEARCH.md`). Kararlar: Etsy API anahtarı alınacak → `scout_engine.py` (resmi API; yerel görev `ONE_TIME_TASK_SCOUT.md`); ürüne 16-bit PNG + STL eklendi (`build_depth_map16`, `write_relief_stl`; testli). Tekli ilan dijital dosyası 2 → 5 (2×8-bit, 2×16-bit, STL). Faz D niş verisine göre yeniden planlanacak.
