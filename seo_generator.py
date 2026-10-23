#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
seo_generator.py  -  04_seo_listing_brain: Etsy listing paketi (baslik, 13 etiket, aciklama, fiyat)

`outputs/` altindaki her urun klasorune ve bundle klasorune `ETSY_LISTING_SEO.txt`, ayrica
`outputs/ALL_LISTINGS_READY.md` (hepsi bir arada) uretir.

Kurallar (kodda zorlanir):
  - Baslik 130-140 karakter; ilk ~40 karakter en yuksek alici niyetli anahtar kelimeyle baslar.
  - Tekil urun basliklari birbirinin kopyasi degildir (keyword cannibalization): her urun farkli
    cihaz/yazilim terimiyle acilir (LightBurn, Fiber Laser Coin, Slate Coaster, Glowforge, xTool D1/P2, Diode Laser).
  - Tam 13 etiket, her biri <= 20 karakter, cok kelimeli, tekrarsiz.
  - Aciklama: paket icerigi (Standard + Inverted), LightBurn/EZCAD hizli baslangic, AI beyani, lisans.

Kullanim:
    python seo_generator.py
    python seo_generator.py --price 4.99 --bundle-price 12.99 --theme "Nordic Mythology"

Bagimlilik yok (sadece standart kutuphane).
"""
from __future__ import annotations

import argparse
import itertools
import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

TITLE_MIN, TITLE_MAX = 130, 140
TAG_COUNT, TAG_MAX = 13, 20
PRICE_SINGLE, PRICE_BUNDLE = 4.99, 12.99

AI_NOTE = ("Designed with AI-assisted sculpting and processed with our own depth-mapping "
           "algorithms for laser engraving.")

# --------------------------------------------------------------------------- #
# Icerik kutuphanesi
# --------------------------------------------------------------------------- #
# Her profil: intent = basligi acan yuksek niyetli ifade, segs = onem sirasina gore ek segmentler,
# specific = urune ozel etiketler, must = basliktaki cihaz terimini etikette de tasiyan etiketler.
PROFILES: dict[str, dict] = {
    "fenrir": dict(
        display="Fenrir Wolf",
        intent="LightBurn 3D Depth Map",
        segs=["Viking Wolf Laser Engraving File", "Norse Mythology Relief PNG", "Glowforge xTool Grayscale Bump Map",
              "4000x4000 300 DPI Instant Download"],
        specific=["fenrir wolf laser", "viking wolf relief", "norse wolf depth map", "wolf engraving file",
                  "wolf coin design", "norse mythology art"],
        must=["lightburn 3d slice", "glowforge file"],
        blurb="Fenrir, the monstrous wolf of Norse myth, sculpted as a deep, high-detail relief medallion.",
    ),
    "valkyrie": dict(
        display="Valkyrie Warrior",
        intent="Fiber Laser Coin Relief File",
        segs=["Viking Shield Maiden Depth Map PNG", "EZCAD Galvo Grayscale Bitmap", "LightBurn 3D Slice 4000x4000 300 DPI",
              "Norse Mythology Commercial Use"],
        specific=["valkyrie laser file", "valkyrie coin relief", "shield maiden art", "viking warrior art",
                  "norse warrior laser", "norse mythology art"],
        must=["fiber laser coin", "ezcad galvo file"],
        blurb="The Valkyrie, Odin's chooser of the slain, sculpted as a fierce high-relief warrior medallion.",
    ),
    "yggdrasil": dict(
        display="Yggdrasil Tree of Life",
        intent="Slate Coaster Laser Engraving",
        segs=["Norse World Tree Depth Map PNG", "Diode CO2 Laser Relief File", "xTool D1 Glowforge Grayscale 300 DPI",
              "Norse Mythology Digital Download"],
        specific=["yggdrasil laser art", "world tree engraving", "tree of life relief", "yggdrasil depth map",
                  "norse tree design", "norse mythology art"],
        must=["slate coaster laser", "diode laser design"],
        blurb="Yggdrasil, the World Tree that holds the nine realms, sculpted as an intricate relief medallion.",
    ),
    "thor": dict(
        display="Thor Mjolnir",
        intent="Glowforge 3D Engraving File",
        segs=["Hammer 3D Heightmap Bump Map PNG", "LightBurn Fiber Laser Coin Design", "Glowforge xTool Grayscale 300 DPI",
              "Norse Viking Digital Download"],
        specific=["thor hammer laser", "mjolnir engraving", "thor laser relief", "mjolnir depth map",
                  "thunder god relief", "viking hammer design"],
        must=["glowforge file", "grayscale bump map"],
        blurb="Thor and his hammer Mjolnir, the thunder god of Norse myth, sculpted as a powerful relief medallion.",
    ),
    "vegvisir": dict(
        display="Vegvisir Viking Compass",
        intent="Glowforge 3D Engraving File",
        segs=["Norse Runic Compass Relief PNG", "LightBurn xTool Diode CO2 Grayscale", "4000x4000 300 DPI Instant Download",
              "Viking Symbol Commercial Use"],
        specific=["vegvisir laser file", "vegvisir engraving", "viking compass art", "vegvisir depth map",
                  "norse rune compass", "viking symbol laser"],
        must=["glowforge file", "grayscale bump map"],
        blurb="Vegvisir, the Norse runic compass said to guide its bearer through storms, sculpted as a detailed relief medallion.",
    ),
    "odin": dict(
        display="Odin Allfather",
        intent="xTool D1 P2 Laser Engraving File",
        segs=["Norse God Depth Map Relief PNG", "Slate Coaster Diode CO2 Grayscale", "LightBurn Glowforge 4000x4000 300 DPI",
              "Viking Mythology Digital Download"],
        specific=["odin laser engraving", "allfather depth map", "odin raven relief", "norse god laser art",
                  "odin coin relief", "viking god design"],
        must=["xtool d1 design", "laser engraver png"],
        blurb="Odin the Allfather, the one-eyed ruler of Asgard, sculpted as a commanding relief medallion.",
    ),
}

# Bilinmeyen urunler icin rotasyonlu yedek kutuphane
ROT_INTENTS = ["LightBurn 3D Depth Map", "Fiber Laser Coin Relief File", "Slate Coaster Laser Engraving",
               "Glowforge 3D Engraving File", "xTool D1 P2 Laser Engraving File", "Diode Laser 3D Illusion File"]
ROT_MUST = [["lightburn 3d slice", "glowforge file"], ["fiber laser coin", "ezcad galvo file"],
            ["slate coaster laser", "diode laser design"], ["glowforge file", "grayscale bump map"],
            ["xtool d1 design", "laser engraver png"], ["diode laser design", "co2 laser 3d art"]]

TAG_POOL = ["laser depth map", "lightburn 3d slice", "glowforge file", "xtool d1 design", "fiber laser coin",
            "3d illusion laser", "slate coaster laser", "grayscale bump map", "3d engraving file", "laser engraver png",
            "ezcad galvo file", "300 dpi depth map", "wood engraving art", "viking laser art", "norse laser file",
            "commercial use file", "laser relief design", "4000px heightmap", "diode laser design", "co2 laser 3d art"]

TITLE_FILLERS = ["Instant Download", "Commercial Use", "PNG Heightmap", "Digital File", "Laser Ready File"]


# --------------------------------------------------------------------------- #
# Baslik / etiket uretimi
# --------------------------------------------------------------------------- #
def fit_title(intent: str, name: str, segs: list[str]) -> str:
    """intent + isim ile acar; segmentlerin oncelik sirasini koruyan alt kumesini, 130-140 karakter araligina
    en yakin (<=140) olacak sekilde secer."""
    head = f"{intent} {name}"
    pool = segs + [f for f in TITLE_FILLERS if f.lower() not in " ".join(segs).lower()]
    best: tuple[float, str] | None = None
    n = len(pool)
    for r in range(0, n + 1):
        for combo in itertools.combinations(range(n), r):
            title = head + "".join(f" | {pool[i]}" for i in combo)
            if not (TITLE_MIN <= len(title) <= TITLE_MAX):
                continue
            # oncelik: ilk segmentler (segs) mutlaka, sonra uzunluk 138'e yakin
            score = sum((3.0 - 0.5 * i) if i < len(segs) else 0.5 for i in combo) - abs(len(title) - 138) * 0.05
            if best is None or score > best[0]:
                best = (score, title)
    if best is None:
        raise ValueError(f"130-140 karakterlik baslik kurulamadi: {head!r}")
    return best[1]


def build_tags(specific: list[str], must: list[str], offset: int, extra: list[str] | None = None) -> list[str]:
    tags: list[str] = []

    def add(t: str) -> None:
        t = re.sub(r"\s+", " ", t.strip().lower())
        if t and len(t) <= TAG_MAX and len(t.split()) >= 2 and t not in tags and len(tags) < TAG_COUNT:
            tags.append(t)

    for t in specific[:6] + must + (extra or []):
        add(t)
    rot = TAG_POOL[offset % len(TAG_POOL):] + TAG_POOL[:offset % len(TAG_POOL)]
    for t in rot:
        add(t)
    validate_tags(tags)
    return tags


def validate_tags(tags: list[str]) -> None:
    assert len(tags) == TAG_COUNT, f"Tam {TAG_COUNT} etiket gerekli, {len(tags)} var: {tags}"
    assert len(set(tags)) == TAG_COUNT, f"Tekrarlayan etiket var: {tags}"
    for tag in tags:
        assert len(tag) <= TAG_MAX, f"Etiket {TAG_MAX} karakteri asiyor ({len(tag)}): {tag!r}"
        assert len(tag.split()) >= 2, f"Etiket cok kelimeli (long-tail) olmali: {tag!r}"


# --------------------------------------------------------------------------- #
# Aciklama bloklari
# --------------------------------------------------------------------------- #
def table(rows: list[tuple[str, ...]]) -> str:
    widths = [max(len(r[i]) for r in rows) for i in range(len(rows[0]))]
    lines = [" | ".join(c.ljust(widths[i]) for i, c in enumerate(r)).rstrip() for r in rows]
    lines.insert(1, "-+-".join("-" * w for w in widths))
    return "\n".join(lines)


QUICK_START = [
    ("Setup", "Mode", "Resolution", "Start here"),
    ("LightBurn - CO2 / wood, acrylic", "3D Slice", "254-318 DPI (0.08-0.10 mm)", "Run a small test grid, build depth in passes"),
    ("LightBurn - Diode / wood, slate", "Jarvis or Stucki", "254-318 DPI (0.08-0.10 mm)", "Lower speed, check detail on scrap first"),
    ("LightBurn - Fiber / galvo", "Grayscale image", "500-1000 DPI (0.025-0.05 mm)", "Test depth grid; adjust passes"),
    ("EZCAD - Fiber / galvo coin", "Bitmap / gray", "500-1000 DPI (0.025-0.05 mm)", "Import PNG, set size, test power/freq"),
]

COMMON_TAIL = """HOW TO USE
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
{ai_note}

Questions? Message ForgeDepthStudio on Etsy - we reply fast. Thank you!"""


def describe_single(prof: dict, std_name: str, inv_name: str) -> str:
    return f"""{prof['display'].upper()} - 3D LASER ENGRAVING DEPTH MAP | INSTANT DIGITAL DOWNLOAD

{prof['blurb']} Two ready-to-use 4000x4000 px, 300 DPI, 8-bit grayscale 3D illusion depth maps for LightBurn, EZCAD, Glowforge and xTool - made for wood, slate coasters, brass and fiber-laser coins.

WHAT YOU GET (2 PNG FILES)
1) {std_name}  -  STANDARD (black = deepest)
2) {inv_name}  -  INVERTED (white = deepest)
Both: 4000 x 4000 px | 300 DPI | 8-bit grayscale | circular medallion on pure black (#000000).

QUICK START - LIGHTBURN & EZCAD (starting points)
{table(QUICK_START)}

""" + COMMON_TAIL.format(ai_note=AI_NOTE)


def describe_bundle(n: int, theme: str, names: list[str], price: float, single_price: float,
                    files: list[str], delivery: str) -> str:
    total = n * single_price
    save_pct = round((1 - price / total) * 100)
    lines = "\n".join(f"{i}) {nm}" for i, nm in enumerate(names, 1))
    if delivery == "drive":
        receive = ("Etsy delivers a PDF (Download_Instructions_and_License.pdf) right after payment. "
                   "Click its download button to get all files from our cloud folder.")
    else:
        receive = ("Instant download from Etsy right after payment (Purchases and reviews):\n"
                   + "\n".join(f"- {f}" for f in files))
    return f"""{n}-IN-1 {theme.upper()} MEGA BUNDLE - 3D LASER ENGRAVING DEPTH MAPS | COMMERCIAL USE

{n} premium {theme} relief medallions in one download: ready-to-use 4000x4000 px, 300 DPI, 8-bit grayscale 3D illusion depth maps for LightBurn, EZCAD, Glowforge and xTool. Buy all {n} for ${price:.2f} instead of ${total:.2f} - SAVE {save_pct}% vs buying them one by one.

WHAT'S INSIDE ({n} DESIGNS x 2 VERSIONS = {2 * n} PNG FILES)
{lines}
Every design comes as STANDARD (black = deepest) and INVERTED (white = deepest), 4000 x 4000 px | 300 DPI | 8-bit grayscale | circular medallion on pure black (#000000).

HOW YOU RECEIVE THE FILES
{receive}

QUICK START - LIGHTBURN & EZCAD (starting points)
{table(QUICK_START)}

""" + COMMON_TAIL.format(ai_note=AI_NOTE)


# --------------------------------------------------------------------------- #
# Urun / bundle tarama
# --------------------------------------------------------------------------- #
def pretty(name: str) -> str:
    return re.sub(r"^\d+[_\s-]*", "", name).replace("_", " ").strip() or name


def find_profile(folder: str, idx: int) -> dict:
    low = folder.lower()
    for key, prof in PROFILES.items():
        if key in low:
            return {**prof, "key": key}
    disp = pretty(folder)
    words = re.sub(r"[^a-z0-9 ]", "", disp.lower()).split()
    w0 = words[0] if words else "relief"
    w01 = " ".join(words[:2]) if len(words) > 1 else w0
    spec = [f"{w0} laser file", f"{w0} engraving", f"{w0} depth map", f"{w01} laser", f"{w01} art",
            f"{w0} relief design", f"{w0} laser art"]
    return dict(
        key=folder.lower(), display=disp, intent=ROT_INTENTS[idx % len(ROT_INTENTS)],
        segs=["3D Relief Depth Map PNG", "LightBurn Glowforge xTool Grayscale", "4000x4000 300 DPI Instant Download",
              "Commercial Use Digital Download"],
        specific=spec, must=ROT_MUST[idx % len(ROT_MUST)],
        blurb=f"{disp}, sculpted as a deep, high-detail relief medallion.",
    )


def list_products(outputs: Path) -> list[Path]:
    return [d for d in sorted(outputs.iterdir())
            if d.is_dir() and not d.name.startswith("_") and next(d.glob("*_3D_DepthMap_300DPI.png"), None)]


def list_bundles(outputs: Path) -> list[Path]:
    return [d for d in sorted(outputs.iterdir())
            if d.is_dir() and (d / "01_Bundle_Hero_Collage.jpg").is_file()]


def mb(path: Path) -> str:
    return f"{path.stat().st_size / 1e6:.1f} MB"


# --------------------------------------------------------------------------- #
# Listing nesneleri
# --------------------------------------------------------------------------- #
def build_single(folder: Path, idx: int, price: float) -> dict:
    prof = find_profile(folder.name, idx)
    title = fit_title(prof["intent"], prof["display"], prof["segs"])
    tags = build_tags(prof["specific"], prof["must"], offset=idx * 4)
    std = next(folder.glob("*_3D_DepthMap_300DPI.png"))
    inv = next(folder.glob("*_3D_DepthMap_INVERTED_300DPI.png"), None)
    if inv is None:
        raise FileNotFoundError(f"{folder.name}: INVERTED depth map yok. Once `python batch_factory.py` calistir.")
    photos = [("01_Wood_Mockup.jpg", "hero (ahsap oyma)"), ("04_Comparison_Split_Guide.jpg", "guven: ham depth map -> sonuc + teknik bilgi"),
              ("02_Brass_Mockup.jpg", "pirinc / fiber lazer"), ("03_Slate_Coaster_Mockup.jpg", "arduvaz coaster")]
    return dict(
        kind="single", folder=folder, name=prof["display"], title=title, tags=tags, price=price,
        description=describe_single(prof, std.name, inv.name),
        photos=[(f, d) for f, d in photos if (folder / f).is_file()],
        video="05_Listing_Video.mp4" if (folder / "05_Listing_Video.mp4").is_file() else None,
        upload=[(std.name, mb(std)), (inv.name, mb(inv))],
    )


def build_bundle(folder: Path, products: list[Path], theme: str, price: float, single_price: float) -> dict:
    n = len(products)
    names = [find_profile(p.name, i)["display"] for i, p in enumerate(products)]
    segs = ["Viking Laser Files PNG", "LightBurn Glowforge xTool", "Fiber Laser Coin Slate Coaster Wood",
            "300 DPI Commercial Use"]
    title = fit_title(f"{n}-in-1 Mega Bundle Laser Engraving Depth Maps", theme, segs)
    th = theme.split()[0].lower()
    specific = ["mega bundle laser", "laser file bundle", f"{n} laser depth maps", f"{th} laser bundle", "viking laser bundle",
                "lightburn bundle"]
    must = ["glowforge bundle", "fiber laser coin set", "laser coaster bundle", "slate coaster bundle", "xtool design bundle"]
    tags = build_tags(specific, must, offset=3)
    pdf = folder / "Download_Instructions_and_License.pdf"
    manifest = folder / "bundle_manifest.json"
    meta = json.loads(manifest.read_text(encoding="utf-8")) if manifest.is_file() else {}
    delivery = meta.get("delivery", "etsy")
    if delivery == "drive":                         # Etsy'ye yalniz PDF; ZIP'ler Drive'da
        upload = [(pdf.name, mb(pdf))] if pdf.is_file() else []
    else:                                           # Etsy'ye ZIP'ler + PDF (her biri <= 20 MB, toplam <= 5 dosya)
        names_ = meta.get("etsy_files") or [z.name for z in sorted(folder.glob("*.zip"))] + [pdf.name]
        upload = [(nm, mb(folder / nm)) for nm in names_ if (folder / nm).is_file()]
    return dict(
        kind="bundle", folder=folder, name=f"{n}-in-1 {theme} Mega Bundle", title=title, tags=tags, price=price,
        description=describe_bundle(n, theme, names, price, single_price, [u[0] for u in upload], delivery),
        photos=[("01_Bundle_Hero_Collage.jpg", "ana kapak (hero collage)")], video=None, upload=upload,
        saving=round((1 - price / (n * single_price)) * 100), n=n, single_price=single_price,
    )


# --------------------------------------------------------------------------- #
# Cikti bicimleri
# --------------------------------------------------------------------------- #
CHECKLIST = """- Listing type: Digital download (no shipping profile); quantity unlimited.
- Etsy creativity / AI disclosure: declare AI-assisted creation in the listing's 'how it's made' fields and keep the AI note in the description (check Etsy's current wording in Shop Manager).
- Upload each digital file under the Etsy per-file size limit (20 MB) and per-listing file-count limit - verify both in the listing editor.
- Title <=140 chars, 13 tags (each <=20 chars) - already validated by seo_generator.py.
- Photos: keep the order below; the video goes in the video slot."""


def render_txt(L: dict) -> str:
    tags_line = ", ".join(L["tags"])
    out = [f"ETSY LISTING - {L['name']}", "=" * 72, "",
           f"TITLE ({len(L['title'])} chars)", L["title"], "",
           f"TAGS ({len(L['tags'])}) - paste as one line", tags_line,
           "(" + "; ".join(f"{t}={len(t)}" for t in L["tags"]) + ")", "",
           f"PRICE: ${L['price']:.2f}"]
    if L["kind"] == "bundle":
        out.append(f"  ({L['n']} x ${L['single_price']:.2f} = ${L['n'] * L['single_price']:.2f}; bundle saves {L['saving']}%)")
    out += ["", "DESCRIPTION", "-" * 72, L["description"], "-" * 72, "",
            "FILES TO UPLOAD (digital)"] + [f"- {n}  ({s})" for n, s in L["upload"]] + ["",
            "LISTING PHOTOS (in this order)"] + [f"{i}. {f}  - {d}" for i, (f, d) in enumerate(L["photos"], 1)]
    if L["video"]:
        out.append(f"Video: {L['video']}")
    out += ["", "CHECKLIST", CHECKLIST, ""]
    return "\n".join(out)


def render_md(listings: list[dict], price: float, bundle_price: float) -> str:
    out = ["# ForgeDepthStudio - ALL LISTINGS READY", "",
           f"Singles **${price:.2f}** | Bundle **${bundle_price:.2f}** | Title 130-140 chars | 13 tags (<=20 chars each)", "",
           "| # | Listing | Title chars | Price | Tags |", "|---|---------|-------------|-------|------|"]
    for i, L in enumerate(listings, 1):
        out.append(f"| {i} | {L['name']} | {len(L['title'])} | ${L['price']:.2f} | {len(L['tags'])} |")
    out.append("")
    for i, L in enumerate(listings, 1):
        out += [f"---", "", f"## {i}. {L['name']}", "",
                f"**Title** ({len(L['title'])} chars)", "", "```", L["title"], "```", "",
                f"**Tags** ({len(L['tags'])}, paste as one line)", "", "```", ", ".join(L["tags"]), "```", "",
                f"**Price:** ${L['price']:.2f}" + (f" ({L['n']} x ${L['single_price']:.2f} = ${L['n'] * L['single_price']:.2f}; saves {L['saving']}%)"
                                                  if L["kind"] == "bundle" else ""), "",
                "**Description**", "", "```", L["description"], "```", "",
                "**Files to upload:** " + "; ".join(f"`{n}` ({s})" for n, s in L["upload"]), "",
                "**Photos:** " + " -> ".join(f"`{f}`" for f, _ in L["photos"]) + (f" | **Video:** `{L['video']}`" if L["video"] else ""), ""]
    out += ["---", "", "## Checklist", "", CHECKLIST, ""]
    return "\n".join(out)


def check_uniqueness(listings: list[dict]) -> None:
    singles = [L for L in listings if L["kind"] == "single"]
    leads = [L["title"][:40].lower() for L in singles]
    assert len(set(leads)) == len(leads), f"Basliklarin ilk 40 karakteri tekrar ediyor: {leads}"
    assert len({L["title"].lower() for L in listings}) == len(listings), "Birebir ayni baslik var"
    for L in listings:
        assert TITLE_MIN <= len(L["title"]) <= TITLE_MAX, f"Baslik {len(L['title'])} karakter: {L['title']}"
        validate_tags(L["tags"])
    for L in listings:
        assert "calibrat" not in (L["title"] + L["description"]).lower(), f"Kanitlanamayan iddia: {L['name']}"
        assert "cnc" not in L["title"].lower() and not any("cnc" in t for t in L["tags"]), f"CNC vaadi (lazer odakli karar): {L['name']}"
        if L["kind"] == "single":
            assert L["title"].lower().count(L["name"].lower()) == 1, f"Urun adi baslikta tam 1 kez olmali: {L['title']}"
            generic = set(TAG_POOL) | {t for m in ROT_MUST for t in m}
            specific = [t for t in L["tags"] if t not in generic]
            assert len(specific) >= 4, f"Urune ozel >=4 etiket gerekli: {L['name']} -> {specific}"
    # Anahtar kelime cannibalization: ayni acilis ifadesi (ilk 3 kelime) iki urunde olmasin
    firsts = [" ".join(L["title"].lower().split()[:3]) for L in singles]
    assert len(set(firsts)) == len(firsts), f"Ayni acilis ifadesi tekrar ediyor: {firsts}"


def main() -> int:
    ap = argparse.ArgumentParser(description="outputs/ icin Etsy listing SEO paketlerini uretir.")
    ap.add_argument("--outputs", type=Path, default=OUTPUT_DIR)
    ap.add_argument("--theme", default="Nordic Mythology", help="bundle temasi")
    ap.add_argument("--price", type=float, default=PRICE_SINGLE, help="tekil urun fiyati (USD)")
    ap.add_argument("--bundle-price", type=float, default=PRICE_BUNDLE, help="bundle fiyati (USD)")
    args = ap.parse_args()

    if not args.outputs.is_dir():
        print(f"HATA: {args.outputs} yok. Once `python batch_factory.py` calistir.", file=sys.stderr)
        return 1
    products = list_products(args.outputs)
    if not products:
        print("HATA: outputs/ icinde urun klasoru yok.", file=sys.stderr)
        return 1

    listings = [build_single(p, i, args.price) for i, p in enumerate(products)]
    for b in list_bundles(args.outputs):
        listings.append(build_bundle(b, products, args.theme, args.bundle_price, args.price))
    check_uniqueness(listings)

    for L in listings:
        (L["folder"] / "ETSY_LISTING_SEO.txt").write_text(render_txt(L), encoding="utf-8")
        print(f"  {L['folder'].name}/ETSY_LISTING_SEO.txt  (baslik {len(L['title'])} kr, {len(L['tags'])} etiket, ${L['price']:.2f})")
    md = args.outputs / "ALL_LISTINGS_READY.md"
    md.write_text(render_md(listings, args.price, args.bundle_price), encoding="utf-8")
    print(f"  {md}")
    if not any(L["kind"] == "bundle" for L in listings):
        print("UYARI: bundle klasoru bulunamadi (`python bundle_packager.py` calistir), bundle listing'i uretilmedi.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
