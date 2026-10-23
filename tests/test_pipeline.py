"""Uretim hatti regresyon testleri: python -m pytest -q

Yavas test (tam urun hatti, ~40 sn) dahil; video uretimi test edilmez (ffmpeg gerektirir).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import batch_factory as bf  # noqa: E402

REAL_NAMES = ["01_Fenrir_Wolf", "02_Yggdrasil_Tree_of_Life", "03_Valkyrie_Warrior",
              "04_Vegvisir_Viking_Compass", "05_Odin_Allfather"]


# --------------------------------------------------------------------------- #
# Yardimcilar
# --------------------------------------------------------------------------- #
def medallion(bg: int, size: int = 900, r: int = 380, off=(0, 0), seed: int = 0):
    """Duz zemin uzerinde, zeminle kontrastli rim'i olan sentetik madalyon (BGR) + gercek (cx, cy, r)."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[:size, :size].astype(np.float32)
    cx, cy = size / 2 + off[0], size / 2 + off[1]
    d = np.hypot(xx - cx, yy - cy)
    tex = np.clip(120 + 60 * np.sin(xx / 17.0) * np.cos(yy / 23.0) + rng.normal(0, 6, (size, size)), 30, 225)
    rim_val = 230 if bg < 128 or bg == 128 else 40
    val = np.where(d < r - 22, tex, rim_val)
    a = np.clip(r + 0.5 - d, 0, 1)                       # anti-alias kenar
    img = val * a + bg * (1 - a)
    return np.repeat(img[..., None], 3, axis=2).astype(np.uint8), (cx, cy, r)


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)


def fake_product(root: Path, name: str, png_bytes: int = 200_000, with_mockups: bool = False) -> Path:
    d = root / name
    d.mkdir(parents=True)
    rng = np.random.default_rng(abs(hash(name)) % 2**32)
    for suffix in ("_3D_DepthMap_300DPI.png", "_3D_DepthMap_INVERTED_300DPI.png"):
        (d / f"{name}{suffix}").write_bytes(rng.bytes(png_bytes))      # boyut testi icin sikistirilamaz veri
    if with_mockups:
        tile = Image.new("RGB", (2000, 2000), (90, 60, 30))
        for f in ("01_Wood_Mockup.jpg", "02_Brass_Mockup.jpg"):
            tile.save(d / f, quality=60)
    return d


# --------------------------------------------------------------------------- #
# Auto-Rim & Background Zeroing
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("bg", [0, 128, 255])
def test_detect_medallion_on_any_background(bg):
    img, (cx, cy, r) = medallion(bg, off=(35, -20))
    det, info = bf.detect_medallion(img, None)
    assert det is not None, f"zemin {bg}: madalyon bulunamadi ({info})"
    dx, dy, dr = det[0] - cx, det[1] - cy, det[2] - r
    assert abs(dx) <= 2 and abs(dy) <= 2 and abs(dr) <= 3, f"zemin {bg}: sapma ({dx:.1f},{dy:.1f},{dr:.1f})"


def test_noise_falls_back_to_safe_circle():
    noise = (np.random.default_rng(1).random((600, 600, 3)) * 255).astype(np.uint8)
    det, _ = bf.detect_medallion(noise, None)
    assert det is None
    _, _, note = bf.auto_depth_normalizer(noise, None)
    assert "guvenli merkez" in note


# --------------------------------------------------------------------------- #
# Tam urun hatti (video haric)
# --------------------------------------------------------------------------- #
def test_full_product_pipeline(tmp_path):
    img, _ = medallion(255, size=1100, r=480)              # beyaz zemin: en zor vaka
    src = tmp_path / "in.png"
    Image.fromarray(img[..., ::-1]).save(src)
    out = tmp_path / "out"
    res = bf.process_product("Test_Medal", str(src), str(out), no_video=True, skip_existing=False)
    assert res["status"] == "ok", res["error"]

    d = out / "Test_Medal"
    std = np.asarray(Image.open(d / "Test_Medal_3D_DepthMap_300DPI.png"))
    with Image.open(d / "Test_Medal_3D_DepthMap_INVERTED_300DPI.png") as im:
        assert im.size == (4000, 4000) and im.mode == "L" and round(im.info["dpi"][0]) == 300
        inv = np.asarray(im)
    assert std.shape == (4000, 4000)
    for a in (std, inv):
        assert all(int(a[y, x]) == 0 for y in (0, -1) for x in (0, -1)), "koseler #000000 degil"
    c = slice(1200, 2800)
    assert np.abs(std[c, c].astype(int) + inv[c, c].astype(int) - 255).max() <= 1
    for f in ("01_Wood_Mockup.jpg", "02_Brass_Mockup.jpg", "03_Slate_Coaster_Mockup.jpg", "04_Comparison_Split_Guide.jpg"):
        with Image.open(d / f) as im:
            assert im.size == (2000, 2000), f


# --------------------------------------------------------------------------- #
# SEO kurallari (gercek urun adlariyla)
# --------------------------------------------------------------------------- #
def test_seo_rules_with_real_names(tmp_path):
    for n in REAL_NAMES:
        fake_product(tmp_path, n, png_bytes=1000)
    r = run("seo_generator.py", "--outputs", str(tmp_path))
    assert r.returncode == 0, r.stderr
    md = (tmp_path / "ALL_LISTINGS_READY.md").read_text(encoding="utf-8")
    titles = re.findall(r"\*\*Title\*\* \(\d+ chars\)\n\n```\n(.*?)\n```", md)
    assert len(titles) == 5
    assert any("Vegvisir Viking Compass" in t for t in titles)
    assert all("cnc" not in t.lower() for t in titles)
    assert "calibrat" not in md.lower()


# --------------------------------------------------------------------------- #
# Bundle teslim modlari
# --------------------------------------------------------------------------- #
def test_bundle_etsy_delivery_and_seo(tmp_path):
    for n in REAL_NAMES:
        fake_product(tmp_path, n, png_bytes=3_600_000, with_mockups=True)    # gercek boyuta yakin
    r = run("bundle_packager.py", "--outputs", str(tmp_path), "--bundle-dir", "06_Norse_Mythology_Bundle")
    assert r.returncode == 0, r.stderr
    bdir = tmp_path / "06_Norse_Mythology_Bundle"
    man = json.loads((bdir / "bundle_manifest.json").read_text())
    assert man["delivery"] == "etsy" and man["download_url"] is None
    assert len(man["etsy_files"]) <= 5 and "Download_Instructions_and_License.pdf" in man["etsy_files"]
    for f in man["etsy_files"]:
        assert (bdir / f).stat().st_size <= 20_000_000, f

    r = run("seo_generator.py", "--outputs", str(tmp_path))
    assert r.returncode == 0, r.stderr
    txt = (bdir / "ETSY_LISTING_SEO.txt").read_text(encoding="utf-8")
    for f in man["etsy_files"]:
        assert f in txt, f"bundle listing'i {f} dosyasini yuklemeyi soylemiyor"


def test_bundle_drive_mode_requires_link(tmp_path):
    fake_product(tmp_path, "01_Fenrir_Wolf", png_bytes=1000, with_mockups=True)
    r = run("bundle_packager.py", "--outputs", str(tmp_path), "--delivery", "drive")
    assert r.returncode == 1 and "download-url" in r.stderr


# --------------------------------------------------------------------------- #
# Kanitlanamayan iddia taramasi
# --------------------------------------------------------------------------- #
def test_no_calibration_claims_in_product_text():
    pat = re.compile(r"(pre|precision)[- ]calibrated", re.I)
    for p in ROOT.glob("*.py"):
        assert not pat.search(p.read_text(encoding="utf-8")), p.name
