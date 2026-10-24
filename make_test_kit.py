"""Faz B3: ucretsiz test kiti (1 tasarim) -> gercek makinede deneme + yapilandirilmis geri bildirim.

Cikti: outputs/_TEST_KIT/ForgeDepthStudio_Test_Kit_<Urun>.zip
  - <urun>_3D_DepthMap_300DPI.png + _INVERTED_ (mevcut urun ciktisindan)
  - Test_Guide.pdf        (1 sayfa: kit, 5 adimli test, neye bakilir, 5 soru)
  - FEEDBACK_FORM.txt     (ayni 5 soru, kopyala-yapistir cevap icin)

Kural: test kiti Etsy yorumu karsiliginda VERILMEZ (Etsy tesvikli yorum yasagi); metin bunu acikca soyler.
Kullanim: python make_test_kit.py --product 01_Fenrir_Wolf [--outputs outputs]
"""
from __future__ import annotations

import argparse
import io
import sys
import zipfile
from pathlib import Path

import bundle_packager as bp
import first_launch_builder as flb

BASE_DIR = Path(__file__).resolve().parent
KIT_DIR = "_TEST_KIT"
GUIDE_NAME = "Test_Guide.pdf"
FORM_NAME = "FEEDBACK_FORM.txt"

STEPS = [
    "Pick ONE scrap piece you know well (plywood, basswood, slate or anodized aluminum).",
    "Import the STANDARD PNG at 50 mm diameter. Mode: 3D Slice (CO2/fiber) or Jarvis (diode). 254-318 DPI.",
    "Use your own usual grayscale/3D settings for that material - these files are NOT tuned to any specific machine.",
    "If the relief looks reversed on your setup, repeat with the INVERTED PNG.",
    "Take one straight-on photo and one low-angle (side light) photo of the result, then answer the 5 questions.",
]
LOOK_FOR = [
    "Is one side of the outer ring deeper/darker than the opposite side? (should be even)",
    "Do shadows in the design engrave as fake holes or ridges?",
    "Banding, stepping or a halo at the outer edge?",
]
QUESTIONS = [
    "Machine, laser type and wattage (e.g. xTool S1 20W diode / 60W CO2 / 30W fiber) + material used.",
    "Image mode, DPI, speed/power and passes you used (copy from your software).",
    "Depth result 1-5: did the relief read correctly (high areas high, low areas low)? Which file: Standard or Inverted?",
    "Any problem from the 'What to look for' list? Where (top/bottom/left/right/center)?",
    "Would this file save you time vs. making your own depth map? What would you fairly pay per design?",
]
FAIR_PLAY = ("This kit is free and has NO strings attached: you are NOT asked to buy anything or to leave an Etsy review, "
             "and your feedback does not need to be positive. We only quote your words publicly if you say so in writing.")
LICENSE = ("Test license: you may engrave this design and keep or sell the physical pieces. "
           "Please do not share, resell or redistribute the digital files.")


def form_text(product: str) -> str:
    lines = [f"ForgeDepthStudio TEST KIT - FEEDBACK ({product})", "=" * 52, "",
             "Reply by Etsy message to ForgeDepthStudio, or where you received this kit.", ""]
    for i, q in enumerate(QUESTIONS, 1):
        lines += [f"{i}) {q}", "   Answer: ", ""]
    lines += ["Photos (optional): attach the straight-on + low-angle photos.",
              "May we quote your answer publicly (name optional)?  YES / NO", "", FAIR_PLAY, "", LICENSE, ""]
    return "\n".join(lines)


def make_guide_pdf(out_path: Path, product: str) -> None:
    from reportlab.lib.colors import HexColor, white
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.utils import ImageReader, simpleSplit
    from reportlab.pdfgen import canvas

    W, H = letter
    M = 40.0
    CW = W - 2 * M
    DARK, AMBER, INK, GREY = HexColor("#14161a"), HexColor("#D49A36"), HexColor("#1b1d21"), HexColor("#5b5f66")
    c = canvas.Canvas(str(out_path), pagesize=letter)
    c.setTitle(f"{product} - Free Test Kit Guide")
    c.setAuthor("ForgeDepthStudio")

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
    c.drawString(122, H - 44, "FREE TEST KIT - ENGRAVING GUIDE")
    c.setFillColor(AMBER)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(122, H - 64, product[:70])
    c.setFillColor(HexColor("#a9adb5"))
    c.setFont("Helvetica", 9)
    c.drawString(122, H - 80, "ForgeDepthStudio  |  3D Laser Engraving Depth Maps")
    y = H - 122

    def section(title: str) -> None:
        nonlocal y
        y -= 10
        c.setFillColor(AMBER)
        c.rect(M, y - 3, 5, 14, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(M + 12, y, title)
        y -= 18

    def para(text: str, size: float = 9.0, font: str = "Helvetica", color=INK, indent: float = 0.0) -> None:
        nonlocal y
        c.setFillColor(color)
        c.setFont(font, size)
        for ln in simpleSplit(text, font, size, CW - indent):
            c.drawString(M + indent, y, ln)
            y -= size * 1.35

    section("WHAT'S IN THIS KIT")
    para("2 PNG files: STANDARD (black = deepest, white = highest) and INVERTED (white = deepest). "
         "4000 x 4000 px  |  300 DPI  |  8-bit grayscale  |  circular design on pure black (#000000).")
    section("5-STEP TEST (about 20 minutes)")
    for i, s in enumerate(STEPS, 1):
        para(f"{i}.  {s}", indent=6)
    section("WHAT TO LOOK FOR")
    for s in LOOK_FOR:
        para(f"-  {s}", indent=6)
    section("YOUR FEEDBACK - 5 QUESTIONS (also in FEEDBACK_FORM.txt)")
    for i, q in enumerate(QUESTIONS, 1):
        para(f"{i}.  {q}", indent=6)
    para("Reply by Etsy message to ForgeDepthStudio, or where you received this kit. Photos are very welcome.",
         8.6, "Helvetica-Bold", GREY)
    section("FAIR PLAY & LICENSE")
    para(FAIR_PLAY, 8.6, color=GREY)
    para(LICENSE, 8.6, color=GREY)
    if y < M:
        raise RuntimeError("Test_Guide.pdf tek sayfaya sigmadi")
    c.showPage()
    c.save()


def build_kit(product_dir: Path, out_root: Path) -> Path:
    std, inv = bp.depth_file(product_dir), bp.inverted_file(product_dir)
    if not std or not inv:
        raise FileNotFoundError(f"{product_dir.name}: Standard/Inverted PNG yok (once batch_factory.py)")
    name = bp.pretty(product_dir.name)
    kit = out_root / KIT_DIR / f"ForgeDepthStudio_Test_Kit_{bp.safe_name(name)}"
    kit.mkdir(parents=True, exist_ok=True)
    make_guide_pdf(kit / GUIDE_NAME, name)
    (kit / FORM_NAME).write_text(form_text(name), encoding="utf-8")
    zpath = kit.with_suffix(".zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_STORED) as zf:
        for f in (std, inv, kit / GUIDE_NAME, kit / FORM_NAME):
            zf.write(f, f"{kit.name}/{f.name}")
    return zpath


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--product", required=True, help="urun klasoru adi, ornek 01_Fenrir_Wolf")
    ap.add_argument("--outputs", type=Path, default=BASE_DIR / "outputs")
    args = ap.parse_args()
    try:
        z = build_kit(args.outputs / args.product, args.outputs)
    except Exception as e:  # noqa: BLE001
        print(f"HATA: {e}", file=sys.stderr)
        return 1
    print(f"Test kiti -> {z}  ({z.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
