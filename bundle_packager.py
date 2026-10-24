#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bundle_packager.py  -  02_asset_factory: Mega Bundle kapak kolaji + teslimat PDF'i + yukleme ZIP'i

`outputs/` altindaki urun klasorlerini (batch_factory.py ciktisi) tek bir bundle'a toplar:

    outputs/_MEGA_BUNDLE_NORDIC/
        01_Bundle_Hero_Collage.jpg                  2000x2000 ana kapak (dairesel madalyon dizilimi + rozetler)
        Download_Instructions_and_License.pdf       Letter, tek sayfa: icerik, LightBurn rehberi, lisans, indirme butonu
        <Bundle>_*.zip                              depth map'ler (Standard + Inverted); her ZIP <= 20 MB (gerekirse bolunur)
        bundle_manifest.json                        teslim modu + Etsy'ye yuklenecek dosyalar (seo_generator okur)

Teslim modlari (--delivery):
  etsy  (varsayilan) ZIP parcalari + PDF dogrudan Etsy'ye yuklenir (her dosya <= 20 MB, toplam <= 5 dosya; kodda kontrol).
        PDF'te link yok; musteri dosyalari Etsy siparisinden indirir. Link sizintisi / kirik link riski yok.
  drive Etsy'ye yalniz PDF; ZIP'ler Google Drive'da. --download-url ZORUNLU (yoksa script durur).

Kullanim:
    python bundle_packager.py
    python bundle_packager.py --delivery drive --download-url "https://drive.google.com/..."
    python bundle_packager.py --theme "Celtic Knots" --products Knot_A Knot_B Knot_C

Bagimliliklar: opencv-python, numpy, Pillow, reportlab (pip install reportlab)
"""
from __future__ import annotations

import argparse
import io
import json
import math
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import batch_factory as bf
import first_launch_builder as flb

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
S = flb.MOCK_SIZE
PLACEHOLDER_URL = "https://drive.google.com/PASTE-YOUR-DRIVE-LINK-HERE"

COVER_NAME = "01_Bundle_Hero_Collage.jpg"
MAX_LABELED_TILES = 12
PDF_NAME = "Download_Instructions_and_License.pdf"


# --------------------------------------------------------------------------- #
# Urun tarama
# --------------------------------------------------------------------------- #
def list_products(outputs: Path, only: list[str] | None = None) -> list[Path]:
    prods = []
    for d in sorted(p for p in outputs.iterdir() if p.is_dir() and not p.name.startswith("_")):
        if only and d.name not in only:
            continue
        if (d / "01_Wood_Mockup.jpg").is_file() and (d / "02_Brass_Mockup.jpg").is_file() and depth_file(d):
            prods.append(d)
    return prods


def depth_file(prod: Path) -> Path | None:
    hits = sorted(prod.glob("*_3D_DepthMap_300DPI.png"))
    return hits[0] if hits else None


def inverted_file(prod: Path) -> Path | None:
    hits = sorted(prod.glob("*_3D_DepthMap_INVERTED_300DPI.png"))
    return hits[0] if hits else None


def pretty(name: str) -> str:
    """'01_Fenrir_Wolf' -> 'Fenrir Wolf'"""
    return re.sub(r"^\d+[_\s-]*", "", name).replace("_", " ").strip() or name


def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_") or "Bundle"


# --------------------------------------------------------------------------- #
# Kapak: dairesel madalyon kolaji
# --------------------------------------------------------------------------- #
def pick_tiles(products: list[Path]) -> list[Path]:
    """Urun basina bir madalyon: pirinc / ahsap dönüşümlü (gorsel cesitlilik)."""
    return [p / ("02_Brass_Mockup.jpg" if i % 2 == 0 else "01_Wood_Mockup.jpg") for i, p in enumerate(products)]


def best_grid(n: int, w: int, h: int, gap: int, row_extra: int = 0) -> tuple[int, int, int]:
    """(cols, rows, cell) - hucre capini en buyuten izgara. 5 madalyon -> ustte 3, altta 2 (ortali)."""
    best = (1, n, 0)
    for cols in range(1, n + 1):
        rows = math.ceil(n / cols)
        cell = min((w - gap * (cols - 1)) // cols, (h - gap * (rows - 1) - rows * row_extra) // rows)
        if cell > best[2] or (cell == best[2] and cols * rows < best[0] * best[1]):
            best = (cols, rows, cell)
    return best


def fit_size(draw, text: str, start: int, max_w: float, tracking: float, min_size: int = 20) -> int:
    size = start
    while size > min_size and flb.tracked_width(draw, text, flb.load_font(size), tracking) > max_w:
        size -= 2
    return size


def circle_tile(path: Path, size: int) -> Image.Image:
    """Mockup'taki madalyon cemberini kirpip dairesel (anti-alias kenarli) RGBA kare olarak dondurur."""
    ss = 3                                                     # supersample maske
    with Image.open(path) as im:
        im = im.convert("RGB")
        cx, cy, half = 1000, 955, 790
        crop = im.crop((cx - half, cy - half, cx + half, cy + half)).resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size * ss, size * ss), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size * ss - 1, size * ss - 1), fill=255)
    crop.putalpha(mask.resize((size, size), Image.LANCZOS))
    return crop


def make_bundle_cover(products: list[Path], out_path: Path, title: str, top_title: str, sub_badge: str) -> None:
    img = Image.fromarray(bf.to_u8(bf.carbon_bg(S)), "RGB")
    d = ImageDraw.Draw(img)

    # Ust baslik
    flb.draw_tracked(d, S / 2, 62, "FORGEDEPTHSTUDIO", flb.load_font(32), bf.AMBER, 8)
    ts = fit_size(d, top_title, 70, S - 140, 4)
    flb.draw_tracked(d, S / 2, 128, top_title, flb.load_font(ts), (246, 200, 96), 4)
    sub = "WOOD | BRASS | SLATE | 4000x4000px 8-BIT GRAYSCALE"
    flb.draw_tracked(d, S / 2, 190, sub, flb.load_font(fit_size(d, sub, 30, S - 160, 3)), (190, 192, 198), 3)

    # Madalyon izgarasi
    tiles = pick_tiles(products)
    labeled = len(tiles) <= MAX_LABELED_TILES                 # buyuk pakette etiketler ust uste biner
    label_h = 62 if labeled else 0
    gx0, gy0, gw, gh, gap = 60, 235, S - 120, 1400, 26
    cols, rows, cell = best_grid(len(tiles), gw, gh, gap, label_h)
    total_h = rows * (cell + label_h) + (rows - 1) * gap
    y_start = gy0 + max(0, (gh - total_h) // 2)

    spots = []
    for idx in range(len(tiles)):
        r, c = divmod(idx, cols)
        in_row = cols if r < rows - 1 else len(tiles) - cols * (rows - 1)
        row_w = in_row * cell + (in_row - 1) * gap
        spots.append((gx0 + (gw - row_w) // 2 + c * (cell + gap), y_start + r * (cell + label_h + gap)))

    def rings(dr):                                            # parilti halkalari (karolarin altinda)
        for (x, y) in spots:
            dr.ellipse((x - 6, y - 6, x + cell + 6, y + cell + 6), outline=255, width=8)

    img = bf.glow_add(img, rings, bf.AMBER_HI, 12, 0.55)

    for (x, y), tile, prod in zip(spots, tiles, products):
        ct = circle_tile(tile, cell)
        img.paste(ct, (x, y), ct)
        d = ImageDraw.Draw(img)
        d.ellipse((x - 2, y - 2, x + cell + 1, y + cell + 1), outline=bf.AMBER_HI, width=4)
        if not labeled:
            continue
        cap = pretty(prod.name).upper()
        flb.draw_tracked(d, x + cell / 2, y + cell + 34, cap,
                         flb.load_font(fit_size(d, cap, 32, cell, 3, 18)), (244, 220, 168), 3)

    # Rozetler: ana baslik + alt bilgi
    img = flb.add_badge(img, title, size=56, center_xy=(S // 2, 1745))
    img = flb.add_badge(img, sub_badge, size=34, center_xy=(S // 2, 1885)).convert("RGB")
    flb.save_jpg(img, out_path)


# --------------------------------------------------------------------------- #
# Teslimat PDF'i (reportlab)
# --------------------------------------------------------------------------- #
def wrap_chars(text: str, font: str, size: float, width: float) -> list[str]:
    """Bosluksuz uzun URL'leri de bolen satir kaydirma."""
    from reportlab.pdfbase.pdfmetrics import stringWidth
    lines, cur = [], ""
    for ch in text:
        if stringWidth(cur + ch, font, size) > width:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    return lines + ([cur] if cur else [])


def _drive_button(c, y, M, W, CW, bh, download_url, AMBER, GREY, HexColor, para):
    """Drive modu: tiklanabilir indirme butonu + yedek duz link. Yeni y doner."""
    c.setFillColor(AMBER)
    c.roundRect(M, y - bh, CW, bh, 10, stroke=0, fill=1)
    c.setStrokeColor(HexColor("#7a5714"))
    c.setLineWidth(1.5)
    c.roundRect(M, y - bh, CW, bh, 10, stroke=1, fill=0)
    c.setFillColor(HexColor("#16120a"))
    c.setFont("Helvetica-Bold", 17)
    c.drawCentredString(W / 2, y - bh / 2 - 6, "CLICK HERE TO DOWNLOAD YOUR FILES")
    c.linkURL(download_url, (M, y - bh, M + CW, y), relative=0, thickness=0)
    y -= bh + 12
    y = para_at(c, y, M, CW, "Opens Google Drive. Download the ZIP file(s) and unzip them on your computer.", GREY)
    y = para_at(c, y, M, CW, "Button not working? Copy and paste this link into your browser:", GREY)
    c.setFillColor(HexColor("#1d4e89"))
    c.setFont("Helvetica", 7.6)
    for ln in wrap_chars(download_url, "Helvetica", 7.6, CW):
        c.drawString(M, y, ln)
        y -= 9.5
    return y - 8


def para_at(c, y, M, CW, text, color, size=8.6, font="Helvetica"):
    from reportlab.lib.utils import simpleSplit
    c.setFillColor(color)
    c.setFont(font, size)
    for ln in simpleSplit(text, font, size, CW):
        c.drawString(M, y, ln)
        y -= size * 1.35
    return y


def make_delivery_pdf(products: list[Path], out_path: Path, bundle_name: str, download_url: str | None,
                      etsy_files: list[str] | None = None) -> None:
    """download_url verilirse (drive modu) tiklanabilir indirme butonu; yoksa (etsy modu) dosyalarin
    Etsy siparisinde oldugunu anlatan bolum."""
    try:
        from reportlab.lib.colors import HexColor, white
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.utils import ImageReader, simpleSplit
        from reportlab.pdfgen import canvas
    except ImportError:
        raise SystemExit("HATA: reportlab gerekli -> pip install reportlab")

    W, H = letter
    M = 36.0
    CW = W - 2 * M
    c = canvas.Canvas(str(out_path), pagesize=letter)
    c.setTitle(f"{bundle_name} - Download Instructions & License")
    c.setAuthor("ForgeDepthStudio")
    DARK, AMBER, INK, GREY = HexColor("#14161a"), HexColor("#D49A36"), HexColor("#1b1d21"), HexColor("#5b5f66")
    GREEN, RED, PALE = HexColor("#2e8b57"), HexColor("#c0392b"), HexColor("#f4f1ea")

    # --- Baslik bandi
    c.setFillColor(DARK)
    c.rect(0, H - 96, W, 96, stroke=0, fill=1)
    c.setFillColor(AMBER)
    c.rect(0, H - 100, W, 4, stroke=0, fill=1)
    buf = io.BytesIO()
    flb.render_logo().save(buf, format="PNG")
    buf.seek(0)
    c.drawImage(ImageReader(buf), 28, H - 90, 78, 78, mask="auto")
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 19)
    c.drawString(122, H - 44, "DOWNLOAD INSTRUCTIONS & LICENSE")
    c.setFillColor(AMBER)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(122, H - 64, bundle_name[:70])
    c.setFillColor(HexColor("#a9adb5"))
    c.setFont("Helvetica", 9)
    c.drawString(122, H - 80, "ForgeDepthStudio  |  3D Laser Engraving Depth Maps")

    y = H - 100 - 22

    def section(title: str) -> None:
        nonlocal y
        c.setFillColor(AMBER)
        c.rect(M, y - 3, 5, 14, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(M + 12, y, title)
        y -= 18

    def para(text: str, size: float = 9.0, font: str = "Helvetica", color=INK, width: float = CW, lead: float | None = None) -> None:
        nonlocal y
        lead = lead or size * 1.35
        c.setFillColor(color)
        c.setFont(font, size)
        for ln in simpleSplit(text, font, size, width):
            c.drawString(M, y, ln)
            y -= lead

    # --- 1) Paket ozeti
    section("YOUR PACKAGE")
    n = len(products)
    has_inv = all(inverted_file(p) for p in products)
    if has_inv:
        para(f"{n} ready-to-engrave design{'s' if n != 1 else ''}, each in TWO versions: STANDARD and INVERTED ({2 * n} PNG files). "
             "Each file: 4000 x 4000 px  |  300 DPI  |  8-bit grayscale  |  circular design on pure black (#000000).")
        para("STANDARD: black = deepest, white = highest.   INVERTED: white = deepest, black = highest.", 8.8, "Helvetica-Bold")
    else:
        para(f"{n} ready-to-engrave design{'s' if n != 1 else ''}. Each file: 4000 x 4000 px  |  300 DPI  |  8-bit grayscale PNG  |  "
             "circular design on pure black (#000000).")
    y -= 2
    shown = products[:12]
    half = math.ceil(len(shown) / 2)
    c.setFont("Helvetica", 8.6)
    c.setFillColor(GREY)
    for i, p in enumerate(shown):
        col, row = divmod(i, half)
        c.drawString(M + 8 + col * (CW / 2), y - row * 11.5, f"{i + 1:02d}  {pretty(p.name)[:42]}")
    y -= half * 11.5
    if n > len(shown):
        c.drawString(M + 8, y, f"+ {n - len(shown)} more designs in the download")
        y -= 11.5
    y -= 8

    # --- 2) Indirme bolumu
    bh = 52
    if not download_url:
        c.setFillColor(AMBER)
        c.roundRect(M, y - bh, CW, bh, 10, stroke=0, fill=1)
        c.setFillColor(HexColor("#16120a"))
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(W / 2, y - bh / 2 - 6, "YOUR FILES ARE IN YOUR ETSY PURCHASE")
        y -= bh + 12
        para("On Etsy: You > Purchases and reviews > Download files. Download every file below, then unzip:", 8.6, color=GREY)
        for nm in (etsy_files or []):
            para(f"- {nm}", 8.2, color=INK)
        y -= 8
    else:
        y = _drive_button(c, y, M, W, CW, bh, download_url, AMBER, GREY, HexColor, para)

    # --- 3) LightBurn ayarlari
    section("RECOMMENDED LIGHTBURN SETTINGS (STARTING POINTS)")
    cols_w = [70, 150, 108, CW - 70 - 150 - 108]
    hdr = ["Image mode", "Best for", "Resolution", "Tip"]
    rows = [
        ("3D Slice", "CO2, fiber & galvo: layered depth engraving in wood, slate, brass",
         "254-318 DPI (0.08-0.10 mm line interval)", "Build depth in several passes. Run a small test grid first, then scale up."),
        ("Jarvis", "Diode & CO2 on wood: smooth tonal shading",
         "254-318 DPI", "Usually soft gradients with little banding - a good first choice for diode lasers."),
        ("Stucki", "Fine detail on slate, coated & anodized surfaces",
         "254-318 DPI", "Crisp, detailed dither. Compare with Jarvis on a scrap piece."),
    ]
    fs, lead = 8.0, 10.0
    c.setFillColor(DARK)
    c.rect(M, y - 15, CW, 16, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 8.4)
    x = M
    for w_, t in zip(cols_w, hdr):
        c.drawString(x + 5, y - 11, t)
        x += w_
    y -= 16
    for ri, row in enumerate(rows):
        wrapped = [simpleSplit(t, "Helvetica-Bold" if ci == 0 else "Helvetica", fs, w_ - 10) for ci, (t, w_) in enumerate(zip(row, cols_w))]
        rh = max(len(w) for w in wrapped) * lead + 7
        c.setFillColor(PALE if ri % 2 == 0 else white)
        c.rect(M, y - rh, CW, rh, stroke=0, fill=1)
        x = M
        for ci, (lines, w_) in enumerate(zip(wrapped, cols_w)):
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold" if ci == 0 else "Helvetica", fs)
            for li, ln in enumerate(lines):
                c.drawString(x + 5, y - 11 - li * lead, ln)
            x += w_
        y -= rh
    c.setStrokeColor(HexColor("#cfcac0"))
    c.setLineWidth(0.6)
    c.line(M, y, M + CW, y)
    y -= 12
    if has_inv:
        para("Pick the version that matches your software's brightness-to-depth setting (STANDARD: black = deepest, INVERTED: "
             "white = deepest). No 'Negative Image' toggle needed.", 8.4, color=GREY)
    else:
        para("Black = lowest / deepest, white = highest. If your software engraves white deeper, enable 'Negative Image'.", 8.4, color=GREY)
    para("Pure black surrounds the circular design: set the job to the circle so the background is not engraved.", 8.4, color=GREY)
    para("Speed and power depend on your machine, wattage and material. Always test on scrap before the final piece.", 8.4, color=GREY)
    y -= 8

    # --- 4) Lisans
    section("COMMERCIAL USE LICENSE")
    colw = CW / 2 - 10
    may = ["Use the files to make physical products (engraved, carved or etched items) and sell them.",
           "Make unlimited physical items on any laser or CNC machine.",
           "Resize, crop and mirror the design to fit your material."]
    maynot = ["Resell, share, gift or redistribute the digital files, original or modified.",
              "List the files (or parts of them) as digital downloads, bundles or templates.",
              "Claim the artwork as your own digital design or register it as your copyright.",
              "Use the files to train AI or machine-learning models."]
    top_y = y
    yl = yr = top_y
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(GREEN)
    c.drawString(M, yl, "YOU MAY")
    c.setFillColor(RED)
    c.drawString(M + CW / 2 + 10, yr, "YOU MAY NOT")
    yl -= 14
    yr -= 14
    for text in may:
        c.setStrokeColor(GREEN)
        c.setLineWidth(1.6)
        c.line(M + 1, yl + 2.5, M + 4, yl - 0.8)
        c.line(M + 4, yl - 0.8, M + 9, yl + 6)
        c.setFillColor(INK)
        c.setFont("Helvetica", 8.4)
        for ln in simpleSplit(text, "Helvetica", 8.4, colw - 16):
            c.drawString(M + 15, yl, ln)
            yl -= 10.5
        yl -= 3
    for text in maynot:
        x0 = M + CW / 2 + 10
        c.setStrokeColor(RED)
        c.setLineWidth(1.6)
        c.line(x0 + 1, yr - 0.5, x0 + 8, yr + 6.5)
        c.line(x0 + 1, yr + 6.5, x0 + 8, yr - 0.5)
        c.setFillColor(INK)
        c.setFont("Helvetica", 8.4)
        for ln in simpleSplit(text, "Helvetica", 8.4, colw - 16):
            c.drawString(x0 + 15, yr, ln)
            yr -= 10.5
        yr -= 3
    y = min(yl, yr) - 4
    para("One license per purchaser or business. Digital files are non-refundable; if anything is wrong with your files, "
         "message us on Etsy and we will fix it right away.", 8.4, color=GREY)

    # --- Alt bilgi bandi
    foot_h = 40
    if y < foot_h + 8:
        raise RuntimeError(f"PDF icerigi tek sayfaya sigmadi (y={y:.0f}). Urun listesi/metni kisalt.")
    c.setFillColor(DARK)
    c.rect(0, 0, W, foot_h, stroke=0, fill=1)
    c.setFillColor(AMBER)
    c.rect(0, foot_h, W, 2.5, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9.5)
    c.drawCentredString(W / 2, 24, "Thank you for your purchase!  Questions? Message ForgeDepthStudio on Etsy.")
    c.setFillColor(HexColor("#a9adb5"))
    c.setFont("Helvetica", 7.6)
    c.drawCentredString(W / 2, 11, "(c) ForgeDepthStudio. All rights reserved. Files are licensed, not sold.")
    c.showPage()
    c.save()


# --------------------------------------------------------------------------- #
ZIP_LIMIT_MB = 20.0
ETSY_MAX_FILES = 5


def pack_groups(files: list[Path], limit: int) -> list[list[Path]]:
    """Sirayi bozmadan, her grup toplam boyutu <= limit olacak sekilde acgozlu paketleme."""
    groups: list[list[Path]] = []
    cur: list[Path] = []
    size = 0
    for f in files:
        sz = f.stat().st_size + 512                      # zip basligi payi
        if cur and size + sz > limit:
            groups.append(cur)
            cur, size = [], 0
        cur.append(f)
        size += sz
    if cur:
        groups.append(cur)
    return groups


def write_zip(path: Path, files: list[Path], root: str) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED) as z:         # PNG zaten sikisik
        for f in files:
            z.write(f, f"{root}/{f.name}")


def build_zips(products: list[Path], out_dir: Path, root: str, limit_mb: float) -> list[Path]:
    """Standard + Inverted PNG'leri paketler. Hepsi limite sigiyorsa tek ZIP; sigmiyorsa Standard ve Inverted ayri
    ZIP'lere (gerekirse Part1, Part2...) bolunur: iki surum de teslim edilir, her dosya <= limit."""
    limit = int(limit_mb * 1_000_000 * 0.99)
    std = [depth_file(p) for p in products]
    inv = [f for f in (inverted_file(p) for p in products) if f]
    for old in out_dir.glob("*.zip"):
        old.unlink()
    outs: list[Path] = []
    total = sum(f.stat().st_size + 512 for f in std + inv)
    if total <= limit:
        z = out_dir / f"{root}_Files.zip"
        write_zip(z, std + inv, root)
        outs.append(z)
    else:
        for label, files in (("STANDARD", std), ("INVERTED", inv)):
            if not files:
                continue
            groups = pack_groups(files, limit)
            for i, g in enumerate(groups, 1):
                part = "" if len(groups) == 1 else f"_Part{i}of{len(groups)}"
                z = out_dir / f"{root}_{label}_Files{part}.zip"
                write_zip(z, g, root)
                outs.append(z)
    return outs


def main() -> int:
    ap = argparse.ArgumentParser(description="outputs/ urunlerinden Mega Bundle kapagi, teslimat PDF'i ve ZIP uretir.")
    ap.add_argument("--outputs", type=Path, default=OUTPUT_DIR)
    ap.add_argument("--theme", default="NORDIC MYTHOLOGY", help="Bundle temasi (rozet/baslikta kullanilir)")
    ap.add_argument("--bundle-dir", default=None, help="cikti klasor adi (vars: _MEGA_BUNDLE_<TEMANIN ILK KELIMESI>)")
    ap.add_argument("--delivery", choices=["etsy", "drive"], default="etsy",
                    help="etsy: ZIP+PDF Etsy'ye (varsayilan); drive: Etsy'ye yalniz PDF, ZIP'ler Drive'da")
    ap.add_argument("--download-url", default=None, help="drive modunda ZORUNLU Google Drive paylasim linki")
    ap.add_argument("--products", nargs="*", help="sadece bu urun klasorleri (sirayla)")
    ap.add_argument("--zip-limit-mb", type=float, default=ZIP_LIMIT_MB, help="her ZIP icin ust sinir (Etsy: 20 MB)")
    args = ap.parse_args()

    if args.delivery == "drive" and (not args.download_url or args.download_url == PLACEHOLDER_URL
                                     or not args.download_url.startswith("http")):
        print("HATA: drive modunda gecerli --download-url zorunlu (musteriye bozuk link gitmesin).", file=sys.stderr)
        return 1
    if not args.outputs.is_dir():
        print(f"HATA: {args.outputs} yok. Once `python batch_factory.py` calistir.", file=sys.stderr)
        return 1
    products = list_products(args.outputs, args.products)
    if not products:
        print("HATA: bundle'a girecek tam urun klasoru bulunamadi (01/02 mockup + depth map gerekli).", file=sys.stderr)
        return 1
    n = len(products)
    theme = args.theme.upper()
    title = f"{n}-IN-1 {theme} MEGA BUNDLE"
    sub_badge = "300 DPI 3D DEPTH MAPS | COMMERCIAL USE"
    bundle_dir = args.bundle_dir or f"_MEGA_BUNDLE_{safe_name(theme.split()[0]).upper()}"
    out_dir = args.outputs / bundle_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"{n} urun: {', '.join(p.name for p in products)}  | teslim modu: {args.delivery}")
    make_bundle_cover(products, out_dir / COVER_NAME, title, "3D LASER ENGRAVING DEPTH MAP COLLECTION", sub_badge)
    print(f"  kapak    -> {out_dir / COVER_NAME}")
    zips = build_zips(products, out_dir, safe_name(title), args.zip_limit_mb)
    oversize = [z for z in zips if z.stat().st_size / 1e6 > args.zip_limit_mb]
    if oversize:
        print(f"HATA: {', '.join(z.name for z in oversize)} {args.zip_limit_mb:.0f} MB sinirini asiyor "
              "(tek dosya cok buyuk).", file=sys.stderr)
        return 1
    etsy_files = [z.name for z in zips] + [PDF_NAME] if args.delivery == "etsy" else [PDF_NAME]
    if len(etsy_files) > ETSY_MAX_FILES:
        print(f"HATA: Etsy'ye {len(etsy_files)} dosya gerekiyor (sinir {ETSY_MAX_FILES}). "
              "Paketi kucult veya --delivery drive kullan.", file=sys.stderr)
        return 1
    make_delivery_pdf(products, out_dir / PDF_NAME, title.title().replace("-In-1", "-in-1"),
                      args.download_url if args.delivery == "drive" else None,
                      [z.name for z in zips])
    print(f"  PDF      -> {out_dir / PDF_NAME}")
    has_inv = all(inverted_file(p) for p in products)
    print(f"  ZIP      -> {len(zips)} dosya ({'Standard + Inverted' if has_inv else 'sadece Standard'})")
    for z in zips:
        print(f"             {z.name}  {z.stat().st_size / 1e6:.1f} MB")
    manifest = {"delivery": args.delivery, "title": title, "products": [p.name for p in products],
                "etsy_files": etsy_files, "download_url": args.download_url if args.delivery == "drive" else None}
    (out_dir / "bundle_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"  ETSY'YE YUKLENECEK ({len(etsy_files)}/{ETSY_MAX_FILES}): {', '.join(etsy_files)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
