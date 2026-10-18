#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bundle_packager.py  -  02_asset_factory: Mega Bundle kapak kolaji + teslimat PDF'i + yukleme ZIP'i

`outputs/` altindaki urun klasorlerini (batch_factory.py ciktisi) tek bir bundle'a toplar:

    outputs/_MEGA_BUNDLE_NORDIC/
        01_Bundle_Hero_Collage.jpg                  2000x2000 ana kapak (dairesel madalyon dizilimi + rozetler)
        Download_Instructions_and_License.pdf       Letter, tek sayfa: icerik, LightBurn rehberi, lisans, indirme butonu
        <Bundle>_Files_for_Drive.zip                Drive'a yuklenecek depth map'ler (+ PDF)

Etsy dijital dosya siniri 20 MB: 5'li bundle ~18 MB, 10'lu ~36 MB. Guvenli yol: ZIP'i Google Drive'a yukle,
paylasim linkini --download-url ile ver; Etsy'e sadece kucuk PDF yuklenir (tiklanabilir indirme butonu).

Kullanim:
    python bundle_packager.py --download-url "https://drive.google.com/..."
    python bundle_packager.py --theme "Celtic Knots" --products Knot_A Knot_B Knot_C

Bagimliliklar: opencv-python, numpy, Pillow, reportlab (pip install reportlab)
"""
from __future__ import annotations

import argparse
import io
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
    label_h = 62
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


def make_delivery_pdf(products: list[Path], out_path: Path, bundle_name: str, download_url: str) -> None:
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

    # --- 2) Indirme butonu
    bh = 52
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
    para("Opens Google Drive. Choose Download to save everything as one ZIP, then unzip on your computer.", 8.6, color=GREY)
    para("Button not working? Copy and paste this link into your browser:", 8.6, color=GREY)
    c.setFillColor(HexColor("#1d4e89"))
    c.setFont("Helvetica", 7.6)
    for ln in wrap_chars(download_url, "Helvetica", 7.6, CW):
        c.drawString(M, y, ln)
        y -= 9.5
    y -= 8

    # --- 3) LightBurn ayarlari
    section("RECOMMENDED LIGHTBURN SETTINGS (STARTING POINTS)")
    cols_w = [70, 150, 108, CW - 70 - 150 - 108]
    hdr = ["Image mode", "Best for", "Resolution", "Tip"]
    rows = [
        ("3D Slice", "CO2, fiber & galvo: true depth relief in wood, slate, brass",
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
def build_zip(products: list[Path], pdf_path: Path, zip_path: Path, root: str) -> None:
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED) as z:     # PNG zaten sikisik
        for p in products:
            f = depth_file(p)
            z.write(f, f"{root}/{f.name}")
        z.write(pdf_path, f"{root}/{PDF_NAME}")


def main() -> int:
    ap = argparse.ArgumentParser(description="outputs/ urunlerinden Mega Bundle kapagi, teslimat PDF'i ve ZIP uretir.")
    ap.add_argument("--outputs", type=Path, default=OUTPUT_DIR)
    ap.add_argument("--theme", default="NORDIC MYTHOLOGY", help="Bundle temasi (rozet/baslikta kullanilir)")
    ap.add_argument("--bundle-dir", default=None, help="cikti klasor adi (vars: _MEGA_BUNDLE_<TEMANIN ILK KELIMESI>)")
    ap.add_argument("--download-url", default=PLACEHOLDER_URL, help="Google Drive / bulut paylasim linki")
    ap.add_argument("--products", nargs="*", help="sadece bu urun klasorleri (sirayla)")
    args = ap.parse_args()

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

    print(f"{n} urun: {', '.join(p.name for p in products)}")
    make_bundle_cover(products, out_dir / COVER_NAME, title, "3D LASER ENGRAVING DEPTH MAP COLLECTION", sub_badge)
    print(f"  kapak    -> {out_dir / COVER_NAME}")
    make_delivery_pdf(products, out_dir / PDF_NAME, title.title().replace("-In-1", "-in-1"), args.download_url)
    print(f"  PDF      -> {out_dir / PDF_NAME}")
    zip_path = out_dir / f"{safe_name(title)}_Files_for_Drive.zip"
    build_zip(products, out_dir / PDF_NAME, zip_path, safe_name(title))
    zmb = zip_path.stat().st_size / 1e6
    print(f"  ZIP      -> {zip_path} ({zmb:.1f} MB)" + ("  [20 MB ustu: Drive'a yukle, Etsy'e PDF'i ver]" if zmb > 20 else ""))
    if args.download_url == PLACEHOLDER_URL:
        print("UYARI: --download-url verilmedi, PDF'teki buton yer tutucu link iceriyor.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
