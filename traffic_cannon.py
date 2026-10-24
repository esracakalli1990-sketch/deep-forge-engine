"""Faz C1: Pinterest pin gorselleri (1000x1500, 2:3) + pin metinleri.

Her urun icin 3 pin (farkli gorsel + farkli metin; Pinterest ayni pinin tekrarini sevmez):
  A_Hero       ahsap mockup + baslik paneli          -> pano "3D Depth Maps for Laser Engraving"
  B_Process    depth map -> ahsap gorunum (ust/alt)  -> pano "LightBurn 3D Slice & Laser Engraving Tips"
  C_Materials  ahsap / pirinc / arduvaz / depth 2x2  -> pano "Norse Mythology Laser Engraving Designs"
Bundle klasoru varsa (01_Bundle_Hero_Collage.jpg) 1 bundle pini.

Cikti: outputs/_Traffic_Cannon/<urun>_<A|B|C>_<ad>_2x3.jpg + pins.json (pin_scheduler.py girdisi)
       + SOCIAL_CAPTIONS_READY.txt (elle pin acarken kopyala-yapistir).
Linkler burada YOK: pin_scheduler.py --links ile eklenir (link_key = urun klasoru).
Kural: mockup'lar render -> gorselde "mockup render" notu; "calibrated"/CNC vaadi yok (testler zorlar).

Kullanim: python traffic_cannon.py [--outputs outputs]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

import batch_factory as bf
import bundle_packager as bp
import first_launch_builder as flb
import seo_generator as seo

BASE_DIR = Path(__file__).resolve().parent
TC_DIR = "_Traffic_Cannon"
PW, PH = 1000, 1500
AMBER, WHITE, MUTED = (212, 154, 54), (240, 240, 236), (150, 154, 162)
COVER = bp.COVER_NAME
BOARDS = {
    "A": "3D Depth Maps for Laser Engraving",
    "B": "LightBurn 3D Slice & Laser Engraving Tips",
    "C": "Norse Mythology Laser Engraving Designs",
    "BUNDLE": "Norse Mythology Laser Engraving Designs",
}
TITLE_MAX, DESC_MAX, ALT_MAX = 100, 500, 500


# --------------------------------------------------------------------------- #
# Gorsel yardimcilari
# --------------------------------------------------------------------------- #
def background() -> Image.Image:
    bg = bf.carbon_bg(PH)[:, (PH - PW) // 2:(PH - PW) // 2 + PW]
    return Image.fromarray(bf.to_u8(bg))


def load_rgb(path: Path, size: int) -> Image.Image:
    with Image.open(path) as im:
        return im.convert("RGB").resize((size, size), Image.LANCZOS)


def text_c(draw: ImageDraw.ImageDraw, cy: float, text: str, size: int, fill, tracking: float = 2.0, max_w: int = PW - 80) -> None:
    """Ortalanmis, tasarsa kuculen tek satir."""
    while size > 14:
        font = flb.load_font(size)
        if flb.tracked_width(draw, text, font, tracking) <= max_w:
            break
        size -= 2
    flb.draw_tracked(draw, PW / 2, cy, text, flb.load_font(size), fill, tracking)


def rule(draw: ImageDraw.ImageDraw, y: int, w: int = 120) -> None:
    draw.rectangle((PW / 2 - w / 2, y, PW / 2 + w / 2, y + 4), fill=AMBER)


def footer(draw: ImageDraw.ImageDraw, note: str = "Digital download  |  mockup render") -> None:
    text_c(draw, PH - 70, "FORGEDEPTHSTUDIO  ON  ETSY", 30, AMBER, 4)
    text_c(draw, PH - 32, note, 20, MUTED, 1)


def pin_hero(prod: Path, display: str) -> Image.Image:
    img = background()
    img.paste(load_rgb(prod / "01_Wood_Mockup.jpg", 1000), (0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 1000, PW, PH), fill=(18, 19, 22))
    text_c(d, 1075, display.upper(), 64, WHITE, 3)
    rule(d, 1120)
    text_c(d, 1180, "3D DEPTH MAP FOR LASER ENGRAVING", 38, AMBER, 2)
    text_c(d, 1250, "4000x4000 PNG  |  300 DPI  |  STANDARD + INVERTED", 28, WHITE, 1)
    text_c(d, 1300, "LightBurn 3D Slice  |  Glowforge  |  xTool", 26, MUTED, 1)
    footer(d)
    return img


def pin_process(prod: Path, display: str) -> Image.Image:
    img = background()
    d = ImageDraw.Draw(img)
    text_c(d, 62, display.upper(), 50, WHITE, 3)
    text_c(d, 112, "FROM DEPTH MAP TO LASER RELIEF", 32, AMBER, 2)
    s, x = 520, (PW - 520) // 2
    depth = load_rgb(bp.depth_file(prod), s)
    bf.rounded_paste(img, depth, (x, 150), 18)
    text_c(d, 150 + s + 26, "THE FILE YOU DOWNLOAD (8-bit grayscale)", 24, MUTED, 1)
    cx, ay = PW // 2, 150 + s + 50
    d.polygon([(cx - 26, ay), (cx + 26, ay), (cx, ay + 34)], fill=AMBER)
    bf.rounded_paste(img, load_rgb(prod / "01_Wood_Mockup.jpg", s), (x, ay + 46), 18)
    text_c(d, ay + 46 + s + 26, "ENGRAVED LOOK ON WOOD (mockup render)", 24, MUTED, 1)
    footer(d, "White = high, black = deep  |  Inverted version included")
    return img


def pin_materials(prod: Path, display: str) -> Image.Image:
    img = background()
    d = ImageDraw.Draw(img)
    text_c(d, 80, "ONE FILE, MANY MATERIALS", 50, WHITE, 3)
    rule(d, 125)
    text_c(d, 175, f"{display}  |  Norse 3D depth map", 32, AMBER, 1)
    t, g = 470, 16
    x0, y0 = (PW - 2 * t - g) // 2, 230
    tiles = [("01_Wood_Mockup.jpg", "WOOD"), ("02_Brass_Mockup.jpg", "BRASS"),
             ("03_Slate_Coaster_Mockup.jpg", "SLATE"), (bp.depth_file(prod).name, "DEPTH MAP")]
    for i, (f, label) in enumerate(tiles):
        x, y = x0 + (i % 2) * (t + g), y0 + (i // 2) * (t + g)
        p = prod / f
        tile = load_rgb(p, t) if p.is_file() else load_rgb(prod / "01_Wood_Mockup.jpg", t)
        bf.rounded_paste(img, tile, (x, y), 16)
        d.rounded_rectangle((x + 14, y + t - 58, x + 14 + 24 * len(label) + 28, y + t - 14), 10, fill=(18, 19, 22))
        d.text((x + 28, y + t - 51), label, font=flb.load_font(26), fill=AMBER)
    text_c(d, y0 + 2 * t + g + 70, "Diode  |  CO2  |  Fiber lasers", 34, WHITE, 2)
    footer(d)
    return img


def pin_bundle(bundle: Path, n: int) -> Image.Image:
    img = background()
    img.paste(load_rgb(bundle / COVER, 1000), (0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 1000, PW, PH), fill=(18, 19, 22))
    text_c(d, 1075, f"ALL {n} DESIGNS IN ONE DOWNLOAD", 54, WHITE, 2)
    rule(d, 1120)
    text_c(d, 1180, "3D DEPTH MAPS FOR LASER ENGRAVING", 36, AMBER, 2)
    text_c(d, 1250, f"{2 * n} PNG files  |  4000x4000  |  300 DPI", 28, WHITE, 1)
    text_c(d, 1300, "Standard + Inverted for every design", 26, MUTED, 1)
    footer(d)
    return img


# --------------------------------------------------------------------------- #
# Metinler
# --------------------------------------------------------------------------- #
def clip(text: str, n: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1].rsplit(" ", 1)[0].rstrip(",;|-") + "…"


def captions(prof: dict, variant: str) -> dict:
    name, blurb = prof["display"], prof["blurb"]
    kw = list(dict.fromkeys(prof["specific"][:4] + ["laser engraving file", "3d depth map", "lightburn 3d slice"]))
    if variant == "A":
        title = f"{name} 3D Depth Map for Laser Engraving | Norse Relief PNG File"
        desc = (f"{blurb} Ready-to-engrave 8-bit grayscale depth map: 4000x4000 px, 300 DPI, Standard + Inverted PNG. "
                "Made for LightBurn 3D Slice, Glowforge and xTool on wood, slate, brass and coins. "
                "Instant digital download from ForgeDepthStudio on Etsy. #laserengraving #lightburn #norsemythology")
        alt = f"Laser engraved {name} relief medallion on dark walnut wood (mockup render) with the title text below."
    elif variant == "B":
        title = f"How a Depth Map Becomes a Laser Relief | {name} Engraving"
        desc = (f"Grayscale depth maps tell your laser how deep to go: white stays high, black burns deepest. "
                f"Top: the {name} depth map file. Bottom: the engraved look on wood (mockup render). "
                "Tip: run a small test on scrap first and use 3D Slice in LightBurn. "
                "Inverted version included for setups that read depth the other way. #laserengravingideas #3dengraving")
        alt = f"Grayscale {name} depth map above an arrow pointing to the same design engraved on wood (mockup render)."
    else:
        title = f"{name} Laser Engraving Design on Wood, Brass and Slate | Depth Map"
        desc = (f"One {name} depth map file, many materials: wood signs, brass coins, slate coasters. "
                "Works with diode, CO2 and fiber lasers. 4000x4000 PNG, 300 DPI, Standard + Inverted. "
                "Great for Viking and Norse mythology gifts. #vikingdecor #lasercut #slatecoaster")
        alt = f"Four tiles of the {name} relief: walnut wood, brass, black slate coaster and the grayscale depth map."
    return dict(title=clip(title, TITLE_MAX), description=clip(desc, DESC_MAX), alt_text=clip(alt, ALT_MAX),
                keywords=", ".join(kw))


def bundle_captions(n: int, names: list[str]) -> dict:
    title = f"{n}-in-1 Norse Mythology Depth Map Bundle for Laser Engraving"
    desc = (f"{n} Norse mythology relief designs ({', '.join(names)}) as ready-to-engrave depth maps. "
            f"{2 * n} PNG files: Standard + Inverted, 4000x4000 px, 300 DPI. For LightBurn 3D Slice, Glowforge and xTool "
            "on wood, slate and brass. Instant download from ForgeDepthStudio on Etsy. #norsemythology #laserengraving")
    alt = f"Collage of {n} Norse mythology relief medallions engraved on wood (mockup render)."
    return dict(title=clip(title, TITLE_MAX), description=clip(desc, DESC_MAX), alt_text=clip(alt, ALT_MAX),
                keywords="norse mythology, laser engraving file, 3d depth map, viking laser bundle")


def check_text(pin: dict) -> None:
    blob = " ".join(str(pin[k]) for k in ("title", "description", "alt_text", "keywords")).lower()
    assert "calibrat" not in blob and "cnc" not in blob, pin["file"]
    assert len(pin["title"]) <= TITLE_MAX and len(pin["description"]) <= DESC_MAX and len(pin["alt_text"]) <= ALT_MAX


# --------------------------------------------------------------------------- #
def build(outputs: Path) -> tuple[Path, list[dict]]:
    out = outputs / TC_DIR
    out.mkdir(parents=True, exist_ok=True)
    pins: list[dict] = []
    prods = bp.list_products(outputs)
    if not prods:
        raise FileNotFoundError(f"{outputs}: urun yok (once batch_factory.py)")
    renders = {"A": ("Hero", pin_hero), "B": ("Process", pin_process), "C": ("Materials", pin_materials)}
    for i, prod in enumerate(prods):
        prof = seo.find_profile(prod.name, i)
        for v, (label, fn) in renders.items():
            f = out / f"{prod.name}_{v}_{label}_2x3.jpg"
            fn(prod, prof["display"]).save(f, quality=90, optimize=True)
            pins.append(dict(file=f.name, product=prod.name, variant=v, board=BOARDS[v], link_key=prod.name,
                             **captions(prof, v)))
    for bundle in seo.list_bundles(outputs):
        man = bundle / "bundle_manifest.json"
        names = json.loads(man.read_text())["products"] if man.is_file() else [p.name for p in prods]
        f = out / f"{bundle.name}_Bundle_2x3.jpg"
        pin_bundle(bundle, len(names)).save(f, quality=90, optimize=True)
        pins.append(dict(file=f.name, product=bundle.name, variant="BUNDLE", board=BOARDS["BUNDLE"], link_key=bundle.name,
                         **bundle_captions(len(names), [bp.pretty(n) for n in names])))
    for p in pins:
        check_text(p)
    (out / "pins.json").write_text(json.dumps(pins, indent=1, ensure_ascii=False), encoding="utf-8")
    lines = ["PINTEREST PIN TEXTS (copy-paste)", "=" * 40, ""]
    for p in pins:
        lines += [f"[{p['file']}]  board: {p['board']}", f"Title: {p['title']}", f"Description: {p['description']}",
                  f"Alt text: {p['alt_text']}", f"Link: <{p['link_key']} Etsy link>", ""]
    (out / "SOCIAL_CAPTIONS_READY.txt").write_text("\n".join(lines), encoding="utf-8")
    return out, pins


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--outputs", type=Path, default=BASE_DIR / "outputs")
    args = ap.parse_args()
    try:
        out, pins = build(args.outputs)
    except Exception as e:  # noqa: BLE001
        print(f"HATA: {e}", file=sys.stderr)
        return 1
    print(f"{len(pins)} pin -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
