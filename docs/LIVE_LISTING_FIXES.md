# CANLI ILAN DUZELTMELERI (Faz A) — kopyala-yapistir

Neden: (1) "pre-calibrated / precision-calibrated" iddialari kaldirildi, (2) lazer odakli konumlandirma (basliklarda/etiketlerde CNC yok),
(3) Vegvisir etiketleri duzeltildi (eskiden 13 etiketin hicbiri "vegvisir" icermiyordu), (4) bundle artik dogrudan Etsy'den teslim.

## Her ilan icin (Etsy > Shop Manager > Listings > ilan > Edit)
1. **Title** alanini asagidaki basligla degistir.
2. **Tags**: eski 13 etiketi sil, asagidaki tek satiri yapistir.
3. **Description**: tamamini asagidaki metinle degistir.
4. Fiyat ve dijital dosyalar (tekli ilanlarda 2 PNG) AYNI kalir.

## Bundle ilani icin ek adim
- Digital files: eski Drive PDF'ini sil; bilgisayarinda `python bundle_packager.py --bundle-dir 06_Norse_Mythology_Bundle`
  calistir ve `06_Norse_Mythology_Bundle` klasorundeki **3 dosyayi** yukle (2 ZIP + yeni PDF; her biri < 20 MB).

## Gorseller (istege bagli ama onerilir)
Eski gorsellerde "PRE-CALIBRATED FOR LASER & CNC", "LIGHTBURN & CNC READY" ve "01 FENRIR WOLF" gibi numarali ad yaziyor.
Guncel kodla `python batch_factory.py` calistirip her ilanda **01_Wood_Mockup.jpg** ve **04_Comparison_Split_Guide.jpg** fotograflarini (ve istersen videoyu) degistir.

---

# ForgeDepthStudio - ALL LISTINGS READY

Singles **$4.99** | Bundle **$12.99** | Title 130-140 chars | 13 tags (<=20 chars each)

| # | Listing | Title chars | Price | Tags |
|---|---------|-------------|-------|------|
| 1 | Fenrir Wolf | 135 | $4.99 | 13 |
| 2 | Yggdrasil Tree of Life | 134 | $4.99 | 13 |
| 3 | Valkyrie Warrior | 132 | $4.99 | 13 |
| 4 | Vegvisir Viking Compass | 138 | $4.99 | 13 |
| 5 | Odin Allfather | 135 | $4.99 | 13 |
| 6 | 5-in-1 Nordic Mythology Mega Bundle | 140 | $12.99 | 13 |

---

## 1. Fenrir Wolf

**Title** (135 chars)

```
LightBurn 3D Depth Map Fenrir Wolf | Viking Wolf Laser Engraving File | Norse Mythology Relief PNG | Glowforge xTool Grayscale Bump Map
```

**Tags** (13, paste as one line)

```
fenrir wolf laser, viking wolf relief, norse wolf depth map, wolf engraving file, wolf coin design, norse mythology art, lightburn 3d slice, glowforge file, laser depth map, xtool d1 design, fiber laser coin, 3d illusion laser, slate coaster laser
```

**Price:** $4.99

**Description**

```
FENRIR WOLF - 3D LASER ENGRAVING DEPTH MAP | INSTANT DIGITAL DOWNLOAD

Fenrir, the monstrous wolf of Norse myth, sculpted as a deep, high-detail relief medallion. Two ready-to-use 4000x4000 px, 300 DPI, 8-bit grayscale 3D illusion depth maps for LightBurn, EZCAD, Glowforge and xTool - made for wood, slate coasters, brass and fiber-laser coins.

WHAT YOU GET (2 PNG FILES)
1) 01_Fenrir_Wolf_3D_DepthMap_300DPI.png  -  STANDARD (black = deepest)
2) 01_Fenrir_Wolf_3D_DepthMap_INVERTED_300DPI.png  -  INVERTED (white = deepest)
Both: 4000 x 4000 px | 300 DPI | 8-bit grayscale | circular medallion on pure black (#000000).

QUICK START - LIGHTBURN & EZCAD (starting points)
Setup                           | Mode             | Resolution                   | Start here
--------------------------------+------------------+------------------------------+---------------------------------------------
LightBurn - CO2 / wood, acrylic | 3D Slice         | 254-318 DPI (0.08-0.10 mm)   | Run a small test grid, build depth in passes
LightBurn - Diode / wood, slate | Jarvis or Stucki | 254-318 DPI (0.08-0.10 mm)   | Lower speed, check detail on scrap first
LightBurn - Fiber / galvo       | Grayscale image  | 500-1000 DPI (0.025-0.05 mm) | Test depth grid; adjust passes
EZCAD - Fiber / galvo coin      | Bitmap / gray    | 500-1000 DPI (0.025-0.05 mm) | Import PNG, set size, test power/freq

HOW TO USE
1) Download the files from Etsy (Purchases and reviews) right after payment.
2) Import the PNG into LightBurn / EZCAD / your CAM software and set your size - at 300 DPI the native size is 13.3 in (338 mm); scale down freely.
3) Choose the mode from the table above, run a quick test on scrap, then engrave.

STANDARD OR INVERTED?
Use the version that matches how your software maps brightness to depth - no 'Negative Image' toggle needed.
- STANDARD: black = deepest, white = highest.
- INVERTED: white = deepest, black = highest.
In both files the background outside the circle is pure black (#000000).

IMPORTANT NOTES
- This is a DIGITAL DOWNLOAD. No physical item is shipped.
- Preview images are computer-generated renderings for illustration. Actual results depend on your machine, power, speed, lens and material - always test first.
- Speed/power values are material- and machine-specific; the table gives starting points only.
- These are shading-based 3D illusion files made for laser engraving. CNC router users: results vary - test on scrap before production.

LICENSE
Personal and commercial use: you may make and sell unlimited physical products (engraved, carved or etched items) with these files.
You may NOT resell, share, gift or redistribute the digital files (original or modified), list them as digital downloads/bundles/templates, or use them to train AI/ML models.

ABOUT THIS DESIGN
Designed with AI-assisted sculpting and processed with our own depth-mapping algorithms for laser engraving.

Questions? Message ForgeDepthStudio on Etsy - we reply fast. Thank you!
```

**Files to upload:** `01_Fenrir_Wolf_3D_DepthMap_300DPI.png` (3.6 MB); `01_Fenrir_Wolf_3D_DepthMap_INVERTED_300DPI.png` (3.6 MB)

**Photos:** `01_Wood_Mockup.jpg` -> `04_Comparison_Split_Guide.jpg` -> `02_Brass_Mockup.jpg` -> `03_Slate_Coaster_Mockup.jpg`

---

## 2. Yggdrasil Tree of Life

**Title** (134 chars)

```
Slate Coaster Laser Engraving Yggdrasil Tree of Life | Norse World Tree Depth Map PNG | Diode CO2 Laser Relief File | Instant Download
```

**Tags** (13, paste as one line)

```
yggdrasil laser art, world tree engraving, tree of life relief, yggdrasil depth map, norse tree design, norse mythology art, slate coaster laser, diode laser design, fiber laser coin, 3d illusion laser, grayscale bump map, 3d engraving file, laser engraver png
```

**Price:** $4.99

**Description**

```
YGGDRASIL TREE OF LIFE - 3D LASER ENGRAVING DEPTH MAP | INSTANT DIGITAL DOWNLOAD

Yggdrasil, the World Tree that holds the nine realms, sculpted as an intricate relief medallion. Two ready-to-use 4000x4000 px, 300 DPI, 8-bit grayscale 3D illusion depth maps for LightBurn, EZCAD, Glowforge and xTool - made for wood, slate coasters, brass and fiber-laser coins.

WHAT YOU GET (2 PNG FILES)
1) 02_Yggdrasil_Tree_of_Life_3D_DepthMap_300DPI.png  -  STANDARD (black = deepest)
2) 02_Yggdrasil_Tree_of_Life_3D_DepthMap_INVERTED_300DPI.png  -  INVERTED (white = deepest)
Both: 4000 x 4000 px | 300 DPI | 8-bit grayscale | circular medallion on pure black (#000000).

QUICK START - LIGHTBURN & EZCAD (starting points)
Setup                           | Mode             | Resolution                   | Start here
--------------------------------+------------------+------------------------------+---------------------------------------------
LightBurn - CO2 / wood, acrylic | 3D Slice         | 254-318 DPI (0.08-0.10 mm)   | Run a small test grid, build depth in passes
LightBurn - Diode / wood, slate | Jarvis or Stucki | 254-318 DPI (0.08-0.10 mm)   | Lower speed, check detail on scrap first
LightBurn - Fiber / galvo       | Grayscale image  | 500-1000 DPI (0.025-0.05 mm) | Test depth grid; adjust passes
EZCAD - Fiber / galvo coin      | Bitmap / gray    | 500-1000 DPI (0.025-0.05 mm) | Import PNG, set size, test power/freq

HOW TO USE
1) Download the files from Etsy (Purchases and reviews) right after payment.
2) Import the PNG into LightBurn / EZCAD / your CAM software and set your size - at 300 DPI the native size is 13.3 in (338 mm); scale down freely.
3) Choose the mode from the table above, run a quick test on scrap, then engrave.

STANDARD OR INVERTED?
Use the version that matches how your software maps brightness to depth - no 'Negative Image' toggle needed.
- STANDARD: black = deepest, white = highest.
- INVERTED: white = deepest, black = highest.
In both files the background outside the circle is pure black (#000000).

IMPORTANT NOTES
- This is a DIGITAL DOWNLOAD. No physical item is shipped.
- Preview images are computer-generated renderings for illustration. Actual results depend on your machine, power, speed, lens and material - always test first.
- Speed/power values are material- and machine-specific; the table gives starting points only.
- These are shading-based 3D illusion files made for laser engraving. CNC router users: results vary - test on scrap before production.

LICENSE
Personal and commercial use: you may make and sell unlimited physical products (engraved, carved or etched items) with these files.
You may NOT resell, share, gift or redistribute the digital files (original or modified), list them as digital downloads/bundles/templates, or use them to train AI/ML models.

ABOUT THIS DESIGN
Designed with AI-assisted sculpting and processed with our own depth-mapping algorithms for laser engraving.

Questions? Message ForgeDepthStudio on Etsy - we reply fast. Thank you!
```

**Files to upload:** `02_Yggdrasil_Tree_of_Life_3D_DepthMap_300DPI.png` (3.6 MB); `02_Yggdrasil_Tree_of_Life_3D_DepthMap_INVERTED_300DPI.png` (3.6 MB)

**Photos:** `01_Wood_Mockup.jpg` -> `04_Comparison_Split_Guide.jpg` -> `02_Brass_Mockup.jpg` -> `03_Slate_Coaster_Mockup.jpg`

---

## 3. Valkyrie Warrior

**Title** (132 chars)

```
Fiber Laser Coin Relief File Valkyrie Warrior | Viking Shield Maiden Depth Map PNG | EZCAD Galvo Grayscale Bitmap | Instant Download
```

**Tags** (13, paste as one line)

```
valkyrie laser file, valkyrie coin relief, shield maiden art, viking warrior art, norse warrior laser, norse mythology art, fiber laser coin, ezcad galvo file, 3d engraving file, laser engraver png, 300 dpi depth map, wood engraving art, viking laser art
```

**Price:** $4.99

**Description**

```
VALKYRIE WARRIOR - 3D LASER ENGRAVING DEPTH MAP | INSTANT DIGITAL DOWNLOAD

The Valkyrie, Odin's chooser of the slain, sculpted as a fierce high-relief warrior medallion. Two ready-to-use 4000x4000 px, 300 DPI, 8-bit grayscale 3D illusion depth maps for LightBurn, EZCAD, Glowforge and xTool - made for wood, slate coasters, brass and fiber-laser coins.

WHAT YOU GET (2 PNG FILES)
1) 03_Valkyrie_Warrior_3D_DepthMap_300DPI.png  -  STANDARD (black = deepest)
2) 03_Valkyrie_Warrior_3D_DepthMap_INVERTED_300DPI.png  -  INVERTED (white = deepest)
Both: 4000 x 4000 px | 300 DPI | 8-bit grayscale | circular medallion on pure black (#000000).

QUICK START - LIGHTBURN & EZCAD (starting points)
Setup                           | Mode             | Resolution                   | Start here
--------------------------------+------------------+------------------------------+---------------------------------------------
LightBurn - CO2 / wood, acrylic | 3D Slice         | 254-318 DPI (0.08-0.10 mm)   | Run a small test grid, build depth in passes
LightBurn - Diode / wood, slate | Jarvis or Stucki | 254-318 DPI (0.08-0.10 mm)   | Lower speed, check detail on scrap first
LightBurn - Fiber / galvo       | Grayscale image  | 500-1000 DPI (0.025-0.05 mm) | Test depth grid; adjust passes
EZCAD - Fiber / galvo coin      | Bitmap / gray    | 500-1000 DPI (0.025-0.05 mm) | Import PNG, set size, test power/freq

HOW TO USE
1) Download the files from Etsy (Purchases and reviews) right after payment.
2) Import the PNG into LightBurn / EZCAD / your CAM software and set your size - at 300 DPI the native size is 13.3 in (338 mm); scale down freely.
3) Choose the mode from the table above, run a quick test on scrap, then engrave.

STANDARD OR INVERTED?
Use the version that matches how your software maps brightness to depth - no 'Negative Image' toggle needed.
- STANDARD: black = deepest, white = highest.
- INVERTED: white = deepest, black = highest.
In both files the background outside the circle is pure black (#000000).

IMPORTANT NOTES
- This is a DIGITAL DOWNLOAD. No physical item is shipped.
- Preview images are computer-generated renderings for illustration. Actual results depend on your machine, power, speed, lens and material - always test first.
- Speed/power values are material- and machine-specific; the table gives starting points only.
- These are shading-based 3D illusion files made for laser engraving. CNC router users: results vary - test on scrap before production.

LICENSE
Personal and commercial use: you may make and sell unlimited physical products (engraved, carved or etched items) with these files.
You may NOT resell, share, gift or redistribute the digital files (original or modified), list them as digital downloads/bundles/templates, or use them to train AI/ML models.

ABOUT THIS DESIGN
Designed with AI-assisted sculpting and processed with our own depth-mapping algorithms for laser engraving.

Questions? Message ForgeDepthStudio on Etsy - we reply fast. Thank you!
```

**Files to upload:** `03_Valkyrie_Warrior_3D_DepthMap_300DPI.png` (3.6 MB); `03_Valkyrie_Warrior_3D_DepthMap_INVERTED_300DPI.png` (3.6 MB)

**Photos:** `01_Wood_Mockup.jpg` -> `04_Comparison_Split_Guide.jpg` -> `02_Brass_Mockup.jpg` -> `03_Slate_Coaster_Mockup.jpg`

---

## 4. Vegvisir Viking Compass

**Title** (138 chars)

```
Glowforge 3D Engraving File Vegvisir Viking Compass | Norse Runic Compass Relief PNG | LightBurn xTool Diode CO2 Grayscale | PNG Heightmap
```

**Tags** (13, paste as one line)

```
vegvisir laser file, vegvisir engraving, viking compass art, vegvisir depth map, norse rune compass, viking symbol laser, glowforge file, grayscale bump map, wood engraving art, viking laser art, norse laser file, commercial use file, laser relief design
```

**Price:** $4.99

**Description**

```
VEGVISIR VIKING COMPASS - 3D LASER ENGRAVING DEPTH MAP | INSTANT DIGITAL DOWNLOAD

Vegvisir, the Norse runic compass said to guide its bearer through storms, sculpted as a detailed relief medallion. Two ready-to-use 4000x4000 px, 300 DPI, 8-bit grayscale 3D illusion depth maps for LightBurn, EZCAD, Glowforge and xTool - made for wood, slate coasters, brass and fiber-laser coins.

WHAT YOU GET (2 PNG FILES)
1) 04_Vegvisir_Viking_Compass_3D_DepthMap_300DPI.png  -  STANDARD (black = deepest)
2) 04_Vegvisir_Viking_Compass_3D_DepthMap_INVERTED_300DPI.png  -  INVERTED (white = deepest)
Both: 4000 x 4000 px | 300 DPI | 8-bit grayscale | circular medallion on pure black (#000000).

QUICK START - LIGHTBURN & EZCAD (starting points)
Setup                           | Mode             | Resolution                   | Start here
--------------------------------+------------------+------------------------------+---------------------------------------------
LightBurn - CO2 / wood, acrylic | 3D Slice         | 254-318 DPI (0.08-0.10 mm)   | Run a small test grid, build depth in passes
LightBurn - Diode / wood, slate | Jarvis or Stucki | 254-318 DPI (0.08-0.10 mm)   | Lower speed, check detail on scrap first
LightBurn - Fiber / galvo       | Grayscale image  | 500-1000 DPI (0.025-0.05 mm) | Test depth grid; adjust passes
EZCAD - Fiber / galvo coin      | Bitmap / gray    | 500-1000 DPI (0.025-0.05 mm) | Import PNG, set size, test power/freq

HOW TO USE
1) Download the files from Etsy (Purchases and reviews) right after payment.
2) Import the PNG into LightBurn / EZCAD / your CAM software and set your size - at 300 DPI the native size is 13.3 in (338 mm); scale down freely.
3) Choose the mode from the table above, run a quick test on scrap, then engrave.

STANDARD OR INVERTED?
Use the version that matches how your software maps brightness to depth - no 'Negative Image' toggle needed.
- STANDARD: black = deepest, white = highest.
- INVERTED: white = deepest, black = highest.
In both files the background outside the circle is pure black (#000000).

IMPORTANT NOTES
- This is a DIGITAL DOWNLOAD. No physical item is shipped.
- Preview images are computer-generated renderings for illustration. Actual results depend on your machine, power, speed, lens and material - always test first.
- Speed/power values are material- and machine-specific; the table gives starting points only.
- These are shading-based 3D illusion files made for laser engraving. CNC router users: results vary - test on scrap before production.

LICENSE
Personal and commercial use: you may make and sell unlimited physical products (engraved, carved or etched items) with these files.
You may NOT resell, share, gift or redistribute the digital files (original or modified), list them as digital downloads/bundles/templates, or use them to train AI/ML models.

ABOUT THIS DESIGN
Designed with AI-assisted sculpting and processed with our own depth-mapping algorithms for laser engraving.

Questions? Message ForgeDepthStudio on Etsy - we reply fast. Thank you!
```

**Files to upload:** `04_Vegvisir_Viking_Compass_3D_DepthMap_300DPI.png` (3.5 MB); `04_Vegvisir_Viking_Compass_3D_DepthMap_INVERTED_300DPI.png` (3.5 MB)

**Photos:** `01_Wood_Mockup.jpg` -> `04_Comparison_Split_Guide.jpg` -> `02_Brass_Mockup.jpg` -> `03_Slate_Coaster_Mockup.jpg`

---

## 5. Odin Allfather

**Title** (135 chars)

```
xTool D1 P2 Laser Engraving File Odin Allfather | Norse God Depth Map Relief PNG | Slate Coaster Diode CO2 Grayscale | Instant Download
```

**Tags** (13, paste as one line)

```
odin laser engraving, allfather depth map, odin raven relief, norse god laser art, odin coin relief, viking god design, xtool d1 design, laser engraver png, laser relief design, 4000px heightmap, diode laser design, co2 laser 3d art, laser depth map
```

**Price:** $4.99

**Description**

```
ODIN ALLFATHER - 3D LASER ENGRAVING DEPTH MAP | INSTANT DIGITAL DOWNLOAD

Odin the Allfather, the one-eyed ruler of Asgard, sculpted as a commanding relief medallion. Two ready-to-use 4000x4000 px, 300 DPI, 8-bit grayscale 3D illusion depth maps for LightBurn, EZCAD, Glowforge and xTool - made for wood, slate coasters, brass and fiber-laser coins.

WHAT YOU GET (2 PNG FILES)
1) 05_Odin_Allfather_3D_DepthMap_300DPI.png  -  STANDARD (black = deepest)
2) 05_Odin_Allfather_3D_DepthMap_INVERTED_300DPI.png  -  INVERTED (white = deepest)
Both: 4000 x 4000 px | 300 DPI | 8-bit grayscale | circular medallion on pure black (#000000).

QUICK START - LIGHTBURN & EZCAD (starting points)
Setup                           | Mode             | Resolution                   | Start here
--------------------------------+------------------+------------------------------+---------------------------------------------
LightBurn - CO2 / wood, acrylic | 3D Slice         | 254-318 DPI (0.08-0.10 mm)   | Run a small test grid, build depth in passes
LightBurn - Diode / wood, slate | Jarvis or Stucki | 254-318 DPI (0.08-0.10 mm)   | Lower speed, check detail on scrap first
LightBurn - Fiber / galvo       | Grayscale image  | 500-1000 DPI (0.025-0.05 mm) | Test depth grid; adjust passes
EZCAD - Fiber / galvo coin      | Bitmap / gray    | 500-1000 DPI (0.025-0.05 mm) | Import PNG, set size, test power/freq

HOW TO USE
1) Download the files from Etsy (Purchases and reviews) right after payment.
2) Import the PNG into LightBurn / EZCAD / your CAM software and set your size - at 300 DPI the native size is 13.3 in (338 mm); scale down freely.
3) Choose the mode from the table above, run a quick test on scrap, then engrave.

STANDARD OR INVERTED?
Use the version that matches how your software maps brightness to depth - no 'Negative Image' toggle needed.
- STANDARD: black = deepest, white = highest.
- INVERTED: white = deepest, black = highest.
In both files the background outside the circle is pure black (#000000).

IMPORTANT NOTES
- This is a DIGITAL DOWNLOAD. No physical item is shipped.
- Preview images are computer-generated renderings for illustration. Actual results depend on your machine, power, speed, lens and material - always test first.
- Speed/power values are material- and machine-specific; the table gives starting points only.
- These are shading-based 3D illusion files made for laser engraving. CNC router users: results vary - test on scrap before production.

LICENSE
Personal and commercial use: you may make and sell unlimited physical products (engraved, carved or etched items) with these files.
You may NOT resell, share, gift or redistribute the digital files (original or modified), list them as digital downloads/bundles/templates, or use them to train AI/ML models.

ABOUT THIS DESIGN
Designed with AI-assisted sculpting and processed with our own depth-mapping algorithms for laser engraving.

Questions? Message ForgeDepthStudio on Etsy - we reply fast. Thank you!
```

**Files to upload:** `05_Odin_Allfather_3D_DepthMap_300DPI.png` (3.5 MB); `05_Odin_Allfather_3D_DepthMap_INVERTED_300DPI.png` (3.5 MB)

**Photos:** `01_Wood_Mockup.jpg` -> `04_Comparison_Split_Guide.jpg` -> `02_Brass_Mockup.jpg` -> `03_Slate_Coaster_Mockup.jpg`

---

## 6. 5-in-1 Nordic Mythology Mega Bundle

**Title** (140 chars)

```
5-in-1 Mega Bundle Laser Engraving Depth Maps Nordic Mythology | Viking Laser Files PNG | LightBurn Glowforge xTool | 300 DPI Commercial Use
```

**Tags** (13, paste as one line)

```
mega bundle laser, laser file bundle, 5 laser depth maps, nordic laser bundle, viking laser bundle, lightburn bundle, glowforge bundle, fiber laser coin set, laser coaster bundle, slate coaster bundle, xtool design bundle, xtool d1 design, fiber laser coin
```

**Price:** $12.99 (5 x $4.99 = $24.95; saves 48%)

**Description**

```
5-IN-1 NORDIC MYTHOLOGY MEGA BUNDLE - 3D LASER ENGRAVING DEPTH MAPS | COMMERCIAL USE

5 premium Nordic Mythology relief medallions in one download: ready-to-use 4000x4000 px, 300 DPI, 8-bit grayscale 3D illusion depth maps for LightBurn, EZCAD, Glowforge and xTool. Buy all 5 for $12.99 instead of $24.95 - SAVE 48% vs buying them one by one.

WHAT'S INSIDE (5 DESIGNS x 2 VERSIONS = 10 PNG FILES)
1) Fenrir Wolf
2) Yggdrasil Tree of Life
3) Valkyrie Warrior
4) Vegvisir Viking Compass
5) Odin Allfather
Every design comes as STANDARD (black = deepest) and INVERTED (white = deepest), 4000 x 4000 px | 300 DPI | 8-bit grayscale | circular medallion on pure black (#000000).

HOW YOU RECEIVE THE FILES
Instant download from Etsy right after payment (Purchases and reviews):
- 5_IN_1_NORDIC_MYTHOLOGY_MEGA_BUNDLE_STANDARD_Files.zip
- 5_IN_1_NORDIC_MYTHOLOGY_MEGA_BUNDLE_INVERTED_Files.zip
- Download_Instructions_and_License.pdf

QUICK START - LIGHTBURN & EZCAD (starting points)
Setup                           | Mode             | Resolution                   | Start here
--------------------------------+------------------+------------------------------+---------------------------------------------
LightBurn - CO2 / wood, acrylic | 3D Slice         | 254-318 DPI (0.08-0.10 mm)   | Run a small test grid, build depth in passes
LightBurn - Diode / wood, slate | Jarvis or Stucki | 254-318 DPI (0.08-0.10 mm)   | Lower speed, check detail on scrap first
LightBurn - Fiber / galvo       | Grayscale image  | 500-1000 DPI (0.025-0.05 mm) | Test depth grid; adjust passes
EZCAD - Fiber / galvo coin      | Bitmap / gray    | 500-1000 DPI (0.025-0.05 mm) | Import PNG, set size, test power/freq

HOW TO USE
1) Download the files from Etsy (Purchases and reviews) right after payment.
2) Import the PNG into LightBurn / EZCAD / your CAM software and set your size - at 300 DPI the native size is 13.3 in (338 mm); scale down freely.
3) Choose the mode from the table above, run a quick test on scrap, then engrave.

STANDARD OR INVERTED?
Use the version that matches how your software maps brightness to depth - no 'Negative Image' toggle needed.
- STANDARD: black = deepest, white = highest.
- INVERTED: white = deepest, black = highest.
In both files the background outside the circle is pure black (#000000).

IMPORTANT NOTES
- This is a DIGITAL DOWNLOAD. No physical item is shipped.
- Preview images are computer-generated renderings for illustration. Actual results depend on your machine, power, speed, lens and material - always test first.
- Speed/power values are material- and machine-specific; the table gives starting points only.
- These are shading-based 3D illusion files made for laser engraving. CNC router users: results vary - test on scrap before production.

LICENSE
Personal and commercial use: you may make and sell unlimited physical products (engraved, carved or etched items) with these files.
You may NOT resell, share, gift or redistribute the digital files (original or modified), list them as digital downloads/bundles/templates, or use them to train AI/ML models.

ABOUT THIS DESIGN
Designed with AI-assisted sculpting and processed with our own depth-mapping algorithms for laser engraving.

Questions? Message ForgeDepthStudio on Etsy - we reply fast. Thank you!
```

**Files to upload:** `5_IN_1_NORDIC_MYTHOLOGY_MEGA_BUNDLE_STANDARD_Files.zip` (17.7 MB); `5_IN_1_NORDIC_MYTHOLOGY_MEGA_BUNDLE_INVERTED_Files.zip` (17.7 MB); `Download_Instructions_and_License.pdf` (0.3 MB)

**Photos:** `01_Bundle_Hero_Collage.jpg`

---

## Checklist

- Listing type: Digital download (no shipping profile); quantity unlimited.
- Etsy creativity / AI disclosure: declare AI-assisted creation in the listing's 'how it's made' fields and keep the AI note in the description (check Etsy's current wording in Shop Manager).
- Upload each digital file under the Etsy per-file size limit (20 MB) and per-listing file-count limit - verify both in the listing editor.
- Title <=140 chars, 13 tags (each <=20 chars) - already validated by seo_generator.py.
- Photos: keep the order below; the video goes in the video slot.
