# PROMPT_LIBRARY — Depth map'e uygun kaynak görsel kalıpları (Faz B2)

Amaç: AI ile üretilen kaynak görselde **ışık = derinlik** karışmasın. Depth map hattı parlaklığı yükseklik sayar;
yandan gelen ışık, gölge, parlama ve metal yansıması lazerde sahte çukur/tümsek olur. `remove_directional_light`
(B1) yalnızca dış halkalardaki geniş ışık eğimini temizler; **detaydaki gölgeyi temizleyemez**. Bu yüzden kaynak doğru üretilmeli.

## 1. Altın kurallar
1. **Düz, önden, gölgesiz ışık** (flat frontal lighting, no cast shadows). Yan ışık / rim light / dramatik ışık YOK.
2. **Mat, tek renk malzeme** (matte white clay / plaster / unpainted resin). Metal, altın, cam, parlak yüzey YOK.
3. **Tam karşıdan** (orthographic, straight-on, top-down). Perspektif, eğik açı YOK.
4. **Düz zemin, tek madalyon, ortada, kenarlar kesilmemiş**; arka plan düz siyah veya düz gri. Doku, sahne, dekor YOK.
5. **Yükseklik = parlaklık mantığı:** en yüksek kabartma en açık, zemin en koyu olsun (prompta "height map style" eklemek yardımcı olur).
6. Metin/harf, imza, filigran, logo YOK (lazerde okunmaz, ToS riski).
7. Telifli karakter / marka / gerçek kişi YOK (Etsy IP riski). Mitoloji figürleri kamu malıdır; belirli bir film/oyun tasarımına benzetme.

## 2. Ana kalıp (kopyala, `[KONU]`'yu değiştir)
```
A circular bas-relief medallion of [KONU], sculpted in matte white plaster,
viewed perfectly straight-on (orthographic, top-down), centered, full medallion visible with a raised border rim,
flat even frontal lighting, no shadows, no specular highlights, no reflections,
soft grayscale height-map look: highest relief brightest, background lowest and darkest,
plain solid black background, high detail, clean edges, no text, no watermark
```
**Negatif prompt (destekleyen araçlarda):**
```
side lighting, dramatic lighting, rim light, cast shadows, glossy, metallic, gold, bronze, reflections,
perspective, tilted, cropped, text, letters, watermark, signature, logo, background scene, colorful
```

## 3. Konu kalıpları (mevcut seri + Norse genişleme)
| Ürün | `[KONU]` |
|------|----------|
| Fenrir | a snarling Norse wolf head with flowing fur, knotwork border |
| Valkyrie | a winged Valkyrie warrior woman in profile with helmet and braids |
| Yggdrasil | the Norse world tree Yggdrasil with spreading branches and deep roots, knotwork border |
| Thor Mjolnir | Thor's hammer Mjolnir encircled by a serpent, Norse knotwork |
| Odin | the bearded Norse god Odin with two ravens, Huginn and Muninn |
| (yeni) Vegvisir | a Vegvisir Norse compass symbol with eight runic staves, shallow even relief |
| (yeni) Drakkar | a Viking longship with dragon prow on stylized waves |
| (yeni) Valknut | three interlocking triangles Valknut with knotwork, shallow even relief |

İpucu: sembol tipi konularda (Vegvisir, Valknut) "shallow even relief" ekle; aksi halde çizgiler fazla derin/keskin çıkar.

## 4. Kalite kapısı (otomatik — `batch_factory.py` notları)
`python batch_factory.py` sonundaki **=== OZET ===** bölümünde her ürün için:
- `isik izi: eksen=..°, guven=.., dis bant egimi %X -> %Y`
- **`!! QA`** → düzeltme sonrası dış bant eğimi hâlâ **> %10**: kaynak görsel yandan aydınlatılmış. **Yayınlama**; yukarıdaki kalıpla yeniden üret.
- `isik izi: eksen belirsiz (...) -> duzeltme uygulanmadi` → ışık izi bulunamadı (genelde iyi haber: düz ışık).

## 5. Manuel 20 saniyelik kontrol (yayından önce)
1. `04_Comparison_Split_Guide.jpg` aç: depth map'in **üst ve alt** (veya sol-sağ) halkaları aynı tonda mı? Bir taraf belirgin açık → reddet.
2. Konunun gölgede kalan yanı "oyuk" gibi görünüyor mu? Evet → reddet (düz ışıkla yeniden üret).
3. Inverted dosyada aynı kontrol (ters ton).
