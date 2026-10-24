#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
batch_factory.py  -  02_asset_factory: toplu urun uretimi

inputs/ icindeki TUM gorselleri (png/jpg/jpeg/webp) okur; her biri icin outputs/<urun_adi>/ altinda:

    <urun_adi>_3D_DepthMap_300DPI.png   4000x4000, 8-bit, 300 DPI, dairesel, disi #000000
    <urun_adi>_3D_DepthMap_INVERTED_300DPI.png   ayni, ama madalyonun ICI ters (255-piksel); disi yine #000000
    01_Wood_Mockup.jpg                  2000x2000  Koyu ceviz
    02_Brass_Mockup.jpg                 2000x2000  Antik pirinc madalyon
    03_Slate_Coaster_Mockup.jpg         2000x2000  Siyah arduvaz coaster + 'SLATE COASTER & WOOD READY' rozeti
    04_Comparison_Split_Guide.jpg       2000x2000  Ham depth map | sonuclar | teknik bilgi grafigi
    05_Listing_Video.mp4                10 sn, 1080x1080, 30 FPS (0-3 tarama, 3-6.5 ahsap zoom, 6.5-10 pirinc + slate)

Akilli Arka Plan Sifirlayici (Auto-Rim & Background Zeroing): kose parlakligi ile zemini (siyah / beyaz / gri)
anlar, madalyonun dis cemberini kontur uydurma + HoughCircles ile bulur, cember disini 2-3 px yumusak
kenarla saf #000000 yapar. Madalyonun ici ASLA ters cevrilmez. Bulunamazsa guvenli merkez daire kullanilir.
Renkli / dusuk kontrastli gorseller desature edilip CLAHE + Bilateral ile ayni 8-bit standarda getirilir.

Kullanim:
    python batch_factory.py
    python batch_factory.py --workers 2 --skip-existing
    python batch_factory.py --only Viking_Wolf --no-video

Bagimliliklar: opencv-python, numpy, Pillow (+ video icin ffmpeg).
"""
from __future__ import annotations

import argparse
import re
import sys
import time
import traceback
import unicodedata
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import first_launch_builder as flb
import make_listing_video as mlv

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "inputs"
OUTPUT_DIR = BASE_DIR / "outputs"
EXTS = {".png", ".jpg", ".jpeg", ".webp"}

F32 = np.float32
S = flb.MOCK_SIZE
AMBER = (212, 154, 54)
AMBER_HI = (255, 176, 40)


# --------------------------------------------------------------------------- #
# Isimlendirme / girdi toplama
# --------------------------------------------------------------------------- #
def product_name(path: Path) -> str:
    stem = unicodedata.normalize("NFKD", path.stem).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", stem).strip("_") or "product"


def collect_inputs(input_dir: Path, only: list[str] | None) -> list[tuple[str, Path]]:
    files = sorted(p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in EXTS)
    seen: dict[str, int] = {}
    out: list[tuple[str, Path]] = []
    for p in files:
        name = product_name(p)
        seen[name] = seen.get(name, 0) + 1
        if seen[name] > 1:
            name = f"{name}_{seen[name]}"
        if only and name not in only and p.stem not in only:
            continue
        out.append((name, p))
    return out


# --------------------------------------------------------------------------- #
# Auto-Depth Normalizer
# --------------------------------------------------------------------------- #
def load_bgr_alpha(path: Path) -> tuple[np.ndarray, np.ndarray | None]:
    img = cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Gorsel okunamadi: {path}")
    if img.dtype == np.uint16:
        img = np.round(img / 257.0).astype(np.uint8)
    elif img.dtype != np.uint8:
        img = cv2.normalize(img.astype(F32), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR), None
    if img.shape[2] == 4:
        alpha = img[..., 3]
        return img[..., :3].copy(), (None if alpha.min() > 250 else alpha)
    return img[..., :3].copy(), None


def _border_ring(a: np.ndarray, frac: float = 0.03) -> np.ndarray:
    b = max(2, int(frac * min(a.shape[:2])))
    parts = [a[:b], a[-b:], a[:, :b], a[:, -b:]]
    return np.concatenate([p.reshape(-1, *a.shape[2:]) for p in parts])


def _fit_circle(pts: np.ndarray) -> tuple[float, float, float]:
    """Kasa en-kucuk-kareler cember uydurma: x^2+y^2 = 2ax + 2by + c."""
    x, y = pts[:, 0], pts[:, 1]
    A = np.c_[2 * x, 2 * y, np.ones(len(x))]
    sol, *_ = np.linalg.lstsq(A, x * x + y * y, rcond=None)
    cx, cy = float(sol[0]), float(sol[1])
    return cx, cy, float(np.sqrt(max(sol[2] + cx * cx + cy * cy, 1e-6)))


def _robust_fit(pts: np.ndarray) -> tuple[float, float, float, float]:
    """Aykiri atan cember uydurma -> (cx, cy, r, bagil rms)."""
    cx, cy, r = _fit_circle(pts)
    for _ in range(3):
        res = np.abs(np.hypot(pts[:, 0] - cx, pts[:, 1] - cy) - r)
        keep = res <= max(2.0, 2.5 * float(np.median(res)))
        if keep.sum() < 30 or keep.all():
            break
        pts = pts[keep]
        cx, cy, r = _fit_circle(pts)
    res = np.abs(np.hypot(pts[:, 0] - cx, pts[:, 1] - cy) - r)
    return cx, cy, r, float(np.sqrt((res ** 2).mean()) / r)


def _refine_circle(gs: np.ndarray, cx: float, cy: float, r: float, iters: int = 2):
    """Radyal gradyan rafinesi: her aciyla [0.88r, 1.12r] araliginda EN DIS guclu kenari arar.
    Yumusak golge/halo gibi zayif gecisleri yok sayar, keskin madalyon kenarini yakalar."""
    sh, sw = gs.shape
    g32 = gs.astype(F32)
    th = np.linspace(0, 2 * np.pi, 360, endpoint=False)
    cos, sin = np.cos(th)[:, None], np.sin(th)[:, None]
    support = 0.0
    for _ in range(iters):
        rs = np.arange(0.88 * r, 1.12 * r, 0.5)[None, :]
        mx, my = (cx + rs * cos).astype(F32), (cy + rs * sin).astype(F32)
        prof = cv2.remap(g32, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        grad = np.abs(np.gradient(prof, axis=1)) * 2.0                      # gri seviye / px
        inb = (mx.min(1) > 2) & (mx.max(1) < sw - 3) & (my.min(1) > 2) & (my.max(1) < sh - 3)
        peak = grad.max(1)
        strong = inb & (peak > 6.0)
        if strong.sum() < 60:
            return cx, cy, r, 0.0
        outer = np.array([np.nonzero(grad[i] >= 0.5 * peak[i])[0].max() for i in range(len(th))])
        idx = np.array([max(0, o - 5) + int(np.argmax(grad[i, max(0, o - 5):o + 1])) for i, o in enumerate(outer)])
        rr = rs[0, idx]
        pts = np.c_[cx + rr * cos[:, 0], cy + rr * sin[:, 0]][strong]
        ncx, ncy, nr, rms = _robust_fit(pts)
        support = float(strong.mean())
        if rms > 0.02:
            return cx, cy, r, 0.0
        cx, cy, r = ncx, ncy, nr
    return cx, cy, r, support


def detect_medallion(bgr: np.ndarray, alpha: np.ndarray | None):
    """Madalyonun dis cemberini bulur (zemin siyah / beyaz / gri fark etmez).

    1) 4 kosedeki 20x20 px ortalama parlaklik = zemin modeli (kose degerleri tutarsizsa kenar halkasi medyani)
    2) |gri - zemin| esigi -> on plan -> dis kontur -> robust (aykiri atan) cember uydurma
    3) Uyum zayifsa HoughCircles yedegi
    Donus: ((cx, cy, r) | None, bilgi sozlugu)  - koordinatlar tam cozunurluk piksel.
    """
    h, w = bgr.shape[:2]
    k = min(1.0, 1000.0 / max(h, w))
    small = cv2.resize(bgr, None, fx=k, fy=k, interpolation=cv2.INTER_AREA) if k < 1 else bgr
    sh, sw = small.shape[:2]
    gs = cv2.GaussianBlur(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY), (0, 0), 1.5)

    c = max(4, int(round(20 * k)))
    corners = np.array([gs[:c, :c].mean(), gs[:c, -c:].mean(), gs[-c:, :c].mean(), gs[-c:, -c:].mean()])
    ring = _border_ring(gs)
    corner_px = np.concatenate([gs[:c, :c].ravel(), gs[:c, -c:].ravel(), gs[-c:, :c].ravel(), gs[-c:, -c:].ravel()])
    bg_lum = float(np.median(ring)) if corners.max() - corners.min() > 25 else float(corners.mean())
    info = {"bg_lum": bg_lum, "method": ""}
    if alpha is None and float(corner_px.std()) > 25:      # duz (tek renk) zemin degil: guvenilir tespit yok
        return None, info

    if alpha is not None:
        a_s = cv2.resize(alpha, (sw, sh), interpolation=cv2.INTER_AREA) if k < 1 else alpha
        fg = ((a_s > 16) * 255).astype(np.uint8)
    else:
        thr = max(14.0, min(60.0, 4.0 * float(corner_px.std())))
        fg = ((np.abs(gs.astype(F32) - bg_lum) > thr) * 255).astype(np.uint8)
    kk = max(3, int(0.01 * min(sh, sw))) | 1
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kk, kk)))
    cnts, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if cnts:
        cnt = max(cnts, key=cv2.contourArea)
        if cv2.contourArea(cnt) >= 0.03 * sh * sw:
            pts = cnt[:, 0, :].astype(np.float64)
            inner = (pts[:, 0] > 2) & (pts[:, 0] < sw - 3) & (pts[:, 1] > 2) & (pts[:, 1] < sh - 3)
            if inner.sum() >= 50:
                pts = pts[inner]                       # kareden tasan (kirpilmis) kenar noktalarini at
            cx, cy, r, rms = _robust_fit(pts)
            if rms < 0.03 and 0.15 * max(sh, sw) < r < 0.8 * max(sh, sw):
                rcx, rcy, rr, sup = _refine_circle(gs, cx, cy, r)
                if sup >= 0.8:                         # kenar halkasi cerceveye degiyorsa rafine guvenilmez
                    cx, cy, r = rcx, rcy, rr
                info["method"] = f"kontur uydurma (rms={rms * 100:.2f}%, kenar destegi={sup * 100:.0f}%)"
                return (cx / k, cy / k, r / k), info

    circles = cv2.HoughCircles(gs, cv2.HOUGH_GRADIENT, dp=1.2, minDist=min(sh, sw) / 2.0, param1=120, param2=40,
                               minRadius=int(0.2 * min(sh, sw)), maxRadius=int(0.75 * max(sh, sw)))
    if circles is not None:
        cx, cy, r = (float(v) for v in circles[0, 0])
        rcx, rcy, rr, sup = _refine_circle(gs, cx, cy, r)
        if sup >= 0.6:                                  # Hough sadece kenar destegi guclu ise kabul
            info["method"] = f"HoughCircles + radyal rafine (destek={sup * 100:.0f}%)"
            return (rcx / k, rcy / k, rr / k), info
    return None, info


def feather_circle(size: int, radius: float, feather: float = 1.25) -> np.ndarray:
    """Kenari `feather` px'lik anti-alias gecisli dairesel maske (disi tam 0)."""
    ax = np.arange(size, dtype=F32) - F32((size - 1) / 2.0)
    dist = np.sqrt(ax[None, :] ** 2 + ax[:, None] ** 2)
    return np.clip((F32(radius) - dist) / F32(feather) + 0.5, 0.0, 1.0).astype(F32)


def auto_depth_normalizer(bgr: np.ndarray, alpha: np.ndarray | None):
    """Akilli Arka Plan Sifirlayici (Auto-Rim & Background Zeroing).

    Madalyonun dis cemberini bulur, etrafinda kare kirpar ve cember disini yumusak kenarla saf siyah
    yapacak maskeyi dondurur. Madalyonun ICI ASLA ters cevrilmez (yuksek = acik, cukur = koyu kalir).
    Bulunamazsa guvenli merkez dairesel maske kullanilir.
    -> (gri uint8 WORK x WORK, mask float32 WORK x WORK, bilgi metni)
    """
    h, w = bgr.shape[:2]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    det, info = detect_medallion(bgr, alpha)
    if det is None:
        cx, cy, r = w / 2.0, h / 2.0, 0.49 * min(h, w)
        note = "madalyon bulunamadi -> guvenli merkez dairesel maske"
    else:
        (cx, cy, r) = det
        note = f"madalyon bulundu: merkez=({cx:.0f},{cy:.0f}) r={r:.0f}, {info['method']}"
    bg_kind = "beyaz/acik" if info["bg_lum"] > 180 else "siyah/koyu" if info["bg_lum"] < 40 else "gri"
    note += f", zemin {bg_kind} ({info['bg_lum']:.0f})"

    side = max(64, int(round(2 * r * 1.03)))
    x0, y0 = int(round(cx - side / 2)), int(round(cy - side / 2))
    pad = max(0, -x0, -y0, x0 + side - w, y0 + side - h)
    g_full = cv2.copyMakeBorder(gray, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=float(info["bg_lum"]))
    gc = g_full[y0 + pad:y0 + pad + side, x0 + pad:x0 + pad + side]
    gc = cv2.resize(gc, (flb.WORK_SIZE, flb.WORK_SIZE),
                    interpolation=cv2.INTER_AREA if side > flb.WORK_SIZE else cv2.INTER_LANCZOS4)

    # Maske yaricapi: algilanan kenardan biraz iceride (zemin rengi karisan kenar pikselleri halo yapmasin)
    r_work = flb.WORK_SIZE / 2.0 / 1.03
    mask = feather_circle(flb.WORK_SIZE, r_work * 0.994 - 1.5, 1.25)       # ~2.5 px @ 4000
    inside = mask > 0.5
    gc = np.where(inside, gc, np.uint8(float(gc[inside].mean()))).astype(np.uint8)   # CLAHE halesi olmasin
    return gc, mask, note


# --------------------------------------------------------------------------- #
# Faz B1 - Isik izi temizleme (directional light removal)
# --------------------------------------------------------------------------- #
# AI render'larinda ust/yan isik, egimli yuzeylerde (rim, halka, dugum bandi) aciya bagli parlaklik egimi
# birakir; parlaklik = yukseklik varsayiminda bu, halkanin "egik" oyulmasi demektir. Isik yonu tum gorselde
# ayni oldugundan dis bantlardaki 1. acisal harmonigin fazi bu eksende toplanir; konu (kurt, yuz) ise rastgele
# fazlar uretir. Yontem: ekseni dis bantlardan tahmin et, her yaricapta yalniz bu eksendeki 1. harmonigi
# cikar, merkezdeki konuya dokunma. Yaricap boyunca ortalama (kubbe/rim profili) korunur.
DELIGHT_MIN_CONF = 0.5          # eksen tutarliligi bunun altindaysa (isik belirsiz) duzeltme uygulanmaz
DELIGHT_QA_LIMIT = 10.0         # duzeltme sonrasi dis bant isik egimi (%) bunu asarsa uyari


def _polar(gray: np.ndarray, radius: float, nr: int, nth: int) -> np.ndarray:
    c = (gray.shape[0] - 1) / 2.0
    return cv2.warpPolar(gray.astype(F32), (nr, nth), (c, c), radius, cv2.WARP_POLAR_LINEAR)


def _harmonic1(pol: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """pol: satir=aci, sutun=yaricap. Her yaricap icin 1. acisal harmonik katsayilari (a1, b1)."""
    th = np.linspace(0, 2 * np.pi, pol.shape[0], endpoint=False)[:, None]
    return 2 * (pol * np.cos(th)).mean(0), 2 * (pol * np.sin(th)).mean(0)


def _mask_radius(mask: np.ndarray) -> float:
    return float(np.sqrt((mask > 0.5).sum() / np.pi))


def light_axis(gray: np.ndarray, mask: np.ndarray, r_lo: float = 0.6, r_hi: float = 0.97) -> tuple[float, float]:
    """Dis bantlardan isik ekseni (radyan, 0..pi) ve tutarlilik guveni (0..1)."""
    nr = 600
    a1, b1 = _harmonic1(_polar(gray, _mask_radius(mask), nr, 720))
    cols = np.arange(int(r_lo * nr), int(r_hi * nr))
    amp, ph = np.hypot(a1[cols], b1[cols]), np.arctan2(b1[cols], a1[cols])
    vx, vy = (amp * np.cos(2 * ph)).sum(), (amp * np.sin(2 * ph)).sum()     # eksen (yon degil): 2x aci
    return float(0.5 * np.arctan2(vy, vx)), float(np.hypot(vx, vy) / (amp.sum() + 1e-6))


def light_bias_pct(img: np.ndarray, phi: float, r_lo: float = 0.6, r_hi: float = 0.97) -> float:
    """Dis bantlarda isik eksenindeki aciya bagli parlaklik egiminin medyani (tepe-tepe, % / 255)."""
    small = cv2.resize(img, (1000, 1000), interpolation=cv2.INTER_AREA) if img.shape[0] > 1000 else img
    nr = 600
    a1, b1 = _harmonic1(_polar(small, _mask_radius((small > 0).astype(F32)), nr, 720))
    cols = np.arange(int(r_lo * nr), int(r_hi * nr))
    return float(np.median(np.abs(a1[cols] * np.cos(phi) + b1[cols] * np.sin(phi)))) * 2 / 255 * 100


def remove_directional_light(gray: np.ndarray, mask: np.ndarray, r_start: float = 0.50, r_full: float = 0.62):
    """-> (duzeltilmis gri uint8, phi | None, guven). Guven dusukse gorsel degistirilmez (phi=None)."""
    phi, conf = light_axis(gray, mask)
    if conf < DELIGHT_MIN_CONF:
        return gray, None, conf
    s, nr, nth = gray.shape[0], 1000, 1440
    c, R = (s - 1) / 2.0, _mask_radius(mask)
    g = gray.astype(F32)
    a1, b1 = _harmonic1(_polar(g, R, nr, nth))
    k = cv2.GaussianBlur((a1 * np.cos(phi) + b1 * np.sin(phi)).reshape(1, -1).astype(F32), (0, 0), 1.5).ravel()
    w = flb.smoothstep(r_start, r_full, np.arange(nr, dtype=F32) / nr)          # merkez konuya dokunma
    th = np.linspace(0, 2 * np.pi, nth, endpoint=False)[:, None]
    corr = cv2.warpPolar(((k * w)[None, :] * np.cos(th - phi)).astype(F32), (s, s), (c, c), R,
                         cv2.WARP_POLAR_LINEAR | cv2.WARP_INVERSE_MAP)
    inside = mask > 0.5
    out = np.clip(g - corr * inside, 0, 255)
    out[~inside] = out[inside].mean()                   # normalizer sozlesmesi: disari notr (CLAHE halesi olmasin)
    return out.astype(np.uint8), phi, conf


# --------------------------------------------------------------------------- #
# Ortak gorsel yardimcilari
# --------------------------------------------------------------------------- #
def carbon_bg(size: int) -> np.ndarray:
    yy, xx = np.mgrid[0:size, 0:size].astype(F32)
    per = 6.0
    weave = np.sin(xx * np.pi / per) * np.sin(yy * np.pi / per)
    twill = np.sin((xx + yy) * np.pi / (2 * per))
    r = np.hypot(xx - size / 2, yy - size * 0.40) / (size * 0.75)
    lum = (0.085 + 0.012 * weave + 0.007 * twill) * (1.2 - 0.6 * np.clip(r, 0, 1.2) ** 1.5)
    return lum[..., None] * np.array([1.0, 1.03, 1.10], F32)


def to_u8(rgb01: np.ndarray) -> np.ndarray:
    return np.clip(rgb01 * 255.0 + 0.5, 0, 255).astype(np.uint8)


def crop_window(img: np.ndarray, cx: float, cy: float, w: int, h: int, border=cv2.BORDER_CONSTANT) -> np.ndarray:
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    pad = max(0, -x0, -y0, x0 + w - img.shape[1], y0 + h - img.shape[0])
    if pad:
        img = cv2.copyMakeBorder(img, pad, pad, pad, pad, border, value=0)
    return img[y0 + pad:y0 + pad + h, x0 + pad:x0 + pad + w]


def glow_add(img: Image.Image, draw_fn, color: tuple[int, int, int], blur: float, gain: float = 0.8) -> Image.Image:
    m = Image.new("L", img.size, 0)
    draw_fn(ImageDraw.Draw(m))
    m = m.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(img.convert("RGB"), F32) + np.asarray(m, F32)[..., None] / 255.0 * np.array(color, F32) * gain
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")


def rounded_paste(dst: Image.Image, src: Image.Image, xy: tuple[int, int], radius: int = 14) -> None:
    mask = Image.new("L", src.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, src.size[0] - 1, src.size[1] - 1), radius, fill=255)
    dst.paste(src, xy, mask)


# --------------------------------------------------------------------------- #
# 03 - Siyah arduvaz (slate) coaster
# --------------------------------------------------------------------------- #
def render_slate_mockup(depth: np.ndarray) -> Image.Image:
    R, cx, cy = 760, 1000, 960
    rng = np.random.default_rng(21)
    yy, xx = np.mgrid[0:S, 0:S].astype(F32)

    # Zemin: sicak gri beton
    pool = np.exp(-np.hypot(xx - 620, yy - 480) / 1300.0)
    conc = 0.50 + 0.16 * pool + 0.10 * (flb.fbm(rng, S, S, 6, 6, 5) - 0.5) + 0.05 * (flb.fbm(rng, S, S, 500, 500, 2) - 0.5)
    bg = conc[..., None] * np.array([1.0, 0.985, 0.955], F32)

    # Duzensiz (kirik) kenarli coaster silueti
    ang = (np.arctan2(yy - cy, xx - cx) + np.pi) / (2 * np.pi)

    def periodic(n: int, amp: float) -> np.ndarray:
        knots = rng.normal(0, 1, n)
        a = ang * n
        i0 = np.floor(a).astype(np.int32) % n
        i1 = (i0 + 1) % n
        f = a - np.floor(a)
        f = f * f * (3 - 2 * f)
        return (knots[i0] * (1 - f) + knots[i1] * f).astype(F32) * amp

    r_edge = R + periodic(48, 6.0) + periodic(160, 1.8)
    dist = np.hypot(xx - cx, yy - cy)
    top = np.clip(r_edge - dist + 0.5, 0, 1)

    # Kalinlik (yan yuz): ust yuzun sag-alta kaymis kopyasi
    m = np.float32([[1, 0, -9], [0, 1, -16]])
    side = cv2.warpAffine(top, m, (S, S), flags=cv2.INTER_LINEAR)
    body = np.maximum(top, side)

    # Yukseklik: kenar pah + oyma kabartma + yuzey puruzu
    edge_d = cv2.distanceTransform((top > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    bevel = flb.smoothstep(0.0, 14.0, edge_d)
    df = 2 * (R - 90)
    rel = np.zeros((S, S), F32)
    flb.paste_center(rel, cv2.resize(depth, (df, df), interpolation=cv2.INTER_AREA).astype(F32) / 255.0, cx, cy)
    etch = np.clip(rel, 0, 1) ** 1.15
    rough = flb.fbm(rng, S, S, 260, 260, 4) - 0.5
    hs = cv2.GaussianBlur(bevel * F32(8.0) + etch * F32(5.0) + rough * F32(1.6), (0, 0), 0.7)
    gx, gy = flb.height_gradients(hs)
    (nx, ny, nz), shade, ndh = flb.shade_terms(gx, gy)
    shadow = flb.cast_shadow(hs, steps=16, step_px=1.4)
    ao = flb.cavity(hs, 6, 8)

    # Albedo: koyu mat arduvaz (katmanli damar + benekler) -> lazerle acilan gumusi-beyaz
    streak = flb.fbm(rng, S, S, 70, 4, 3) - 0.5
    specks = flb.smoothstep(0.78, 0.92, flb.fbm(rng, S, S, 500, 500, 2)) * 0.05
    slate = np.clip(0.072 + 0.035 * streak + 0.02 * rough + specks, 0.02, 0.2)[..., None] * np.array([0.96, 1.0, 1.07], F32)
    grain = 0.80 + 0.20 * flb.fbm(rng, S, S, 900, 900, 2)
    silver = np.array([0.78, 0.80, 0.84], F32) * grain[..., None]
    w = (np.clip((etch - 0.30) / 0.62, 0, 1) ** 1.4 * 0.92)[..., None]      # sadece acik kabarti beyazlasir
    albedo = slate * (1 - w) + silver * w

    light = (0.34 + 0.95 * shade * (1.0 - 0.55 * shadow)) * (1.0 - 0.45 * ao)
    col = albedo * light[..., None] * np.array([1.0, 0.97, 0.92], F32)
    col += ((ndh ** 18) * 0.05 * (1 - w[..., 0]))[..., None] * np.array([0.8, 0.85, 1.0], F32)
    side_col = (0.030 + 0.02 * flb.fbm(rng, S, S, 200, 20, 2))[..., None] * np.array([0.95, 1.0, 1.08], F32)

    def shifted_blur(dx, dy, sigma):
        mm = np.float32([[1, 0, -dx], [0, 1, -dy]])
        return cv2.GaussianBlur(cv2.warpAffine(body, mm, (S, S), flags=cv2.INTER_LINEAR), (0, 0), sigma)

    drop = np.clip(0.55 * shifted_blur(26, 46, 38) + 0.55 * shifted_blur(6, 10, 7), 0, 0.85)
    out = bg * (1 - drop[..., None])
    side_a = np.clip(side - top, 0, 1)[..., None]
    out = out * (1 - side_a) + side_col * side_a
    out = out * (1 - top[..., None]) + np.clip(col, 0, 1) * top[..., None]
    r_n = np.hypot(xx - S / 2, yy - S / 2) / (S * 0.72)
    out *= (1.0 - 0.28 * r_n ** 2)[..., None]
    out += rng.normal(0, 0.006, (S, S, 1)).astype(F32)
    img = Image.fromarray(to_u8(np.clip(out, 0, 1)), "RGB")
    return flb.add_badge(img, "SLATE COASTER & WOOD READY").convert("RGB")


# --------------------------------------------------------------------------- #
# 04 - Karsilastirma / teknik guven gorseli
# --------------------------------------------------------------------------- #
def render_comparison_guide(depth: np.ndarray, wood_rgb: np.ndarray, brass_rgb: np.ndarray, title: str) -> Image.Image:
    img = Image.fromarray(to_u8(carbon_bg(S)), "RGB")
    d = ImageDraw.Draw(img)

    # Panel geometrisi
    s = 0.55
    pw, ph_r, gap_v, top = 880, 640, 24, 200
    ph_l = 2 * ph_r + gap_v
    x_l, x_r = 60, 60 + pw + 120
    y_b = top + ph_l

    # Ham depth map: ahsap mockup'taki daire konumuna hizali, siyah tuval
    k = S / flb.MOCK_SIZE
    dd = int(round(1400 * k))
    canvas = np.zeros((S, S), np.uint8)
    y0 = int(round(S / 2 + (-40) * k - dd / 2))
    x0 = int(round(S / 2 - dd / 2))
    canvas[y0:y0 + dd, x0:x0 + dd] = cv2.resize(depth, (dd, dd), interpolation=cv2.INTER_AREA)
    depth_small = cv2.resize(cv2.cvtColor(canvas, cv2.COLOR_GRAY2RGB), None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    left = crop_window(depth_small, S * s / 2, (S / 2 - 40) * s, pw, ph_l)

    def panel(rgb: np.ndarray, cy_src: float) -> np.ndarray:
        sm = cv2.resize(rgb, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        return crop_window(sm, S * s / 2, cy_src * s, pw, ph_r, cv2.BORDER_REFLECT_101)

    wood_p = panel(wood_rgb, 960)
    brass_p = panel(brass_rgb, 950)
    for arr, xy in ((left, (x_l, top)), (wood_p, (x_r, top)), (brass_p, (x_r, top + ph_r + gap_v))):
        rounded_paste(img, Image.fromarray(np.ascontiguousarray(arr)), xy)
    d = ImageDraw.Draw(img)
    for (x, y, w_, h_) in ((x_l, top, pw, ph_l), (x_r, top, pw, ph_r), (x_r, top + ph_r + gap_v, pw, ph_r)):
        d.rounded_rectangle((x, y, x + w_, y + h_), 14, outline=AMBER, width=3)

    # Lazer dikisi + ok
    mid_x, mid_y = x_l + pw + 60, top + ph_l // 2

    def seam(dr):
        dr.line((mid_x, top, mid_x, y_b), fill=255, width=6)
        dr.polygon([(mid_x - 26, mid_y - 36), (mid_x + 34, mid_y), (mid_x - 26, mid_y + 36)], fill=255)

    img = glow_add(img, seam, AMBER_HI, 14, 0.9)
    d = ImageDraw.Draw(img)
    d.line((mid_x, top, mid_x, mid_y - 46), fill=AMBER_HI, width=3)
    d.line((mid_x, mid_y + 46, mid_x, y_b), fill=AMBER_HI, width=3)
    d.polygon([(mid_x - 22, mid_y - 30), (mid_x + 28, mid_y), (mid_x - 22, mid_y + 30)], fill=(255, 226, 150))

    # Etiketler
    def tag(text: str, x: int, y: int) -> None:
        f = flb.load_font(28)
        tw = flb.tracked_width(d, text, f, 2)
        d.rounded_rectangle((x, y, x + tw + 36, y + 52), 10, fill=(14, 15, 17), outline=AMBER, width=2)
        flb.draw_tracked(d, x + 18 + tw / 2, y + 26, text, f, (244, 220, 168), 2)

    tag("RAW 8-BIT DEPTH MAP", x_l + 20, top + 20)
    tag("ENGRAVED IN WALNUT", x_r + 20, top + 20)
    tag("ANTIQUE BRASS RELIEF", x_r + 20, top + ph_r + gap_v + 20)

    # Baslik
    f = flb.load_font(66)
    flb.draw_tracked(d, S / 2, 82, "FROM DEPTH MAP TO PERFECT ENGRAVING", f, (246, 200, 96), 4)
    f2 = flb.load_font(32)
    flb.draw_tracked(d, S / 2, 150, f"{title.upper()}  |  OPTIMIZED FOR LASER ENGRAVING", f2, (190, 192, 198), 3)

    # Istatistik kartlari
    cy0, ch, cw, cg = y_b + 40, 210, 600, 40
    stats = [("4000 x 4000 px", "HIGH-RES CANVAS"), ("300 DPI", "PRECISION DETAIL"), ("8-BIT GRAYSCALE", "DEPTH-MAP PNG")]
    for i, (big, small_t) in enumerate(stats):
        x = 60 + i * (cw + cg)
        d.rounded_rectangle((x, cy0, x + cw, cy0 + ch), 16, fill=(18, 19, 22), outline=AMBER, width=3)
        d.rectangle((x + 3, cy0 + 22, x + 12, cy0 + ch - 22), fill=AMBER_HI)
        size = 62
        while True:
            fb = flb.load_font(size)
            if flb.tracked_width(d, big, fb, 2) <= cw - 70 or size <= 28:
                break
            size -= 2
        flb.draw_tracked(d, x + 20 + (cw - 20) / 2, cy0 + 85, big, fb, (246, 200, 96), 2)
        flb.draw_tracked(d, x + 20 + (cw - 20) / 2, cy0 + 155, small_t, flb.load_font(30), (200, 202, 208), 4)

    # Uyumluluk cubugu
    by0, bh = cy0 + ch + 36, 110
    d.rounded_rectangle((60, by0, S - 60, by0 + bh), 16, fill=(212, 154, 54), outline=(255, 214, 140), width=3)
    line = "4000x4000px 300 DPI | LightBurn, Glowforge, xTool & EZCAD Ready"
    size = 44
    while True:
        fb = flb.load_font(size)
        if flb.tracked_width(d, line, fb, 1.5) <= S - 200 or size <= 20:
            break
        size -= 2
    flb.draw_tracked(d, S / 2, by0 + bh / 2, line, fb, (22, 18, 12), 1.5)
    return img


# --------------------------------------------------------------------------- #
# Tek urun hatti
# --------------------------------------------------------------------------- #
FILES = ["01_Wood_Mockup.jpg", "02_Brass_Mockup.jpg", "03_Slate_Coaster_Mockup.jpg",
         "04_Comparison_Split_Guide.jpg", "05_Listing_Video.mp4"]


def inverted_name(name: str) -> str:
    return f"{name}_3D_DepthMap_INVERTED_300DPI.png"


def make_inverted(g: np.ndarray, m: np.ndarray) -> np.ndarray:
    """Madalyonun ICI ters (255 - ton); cember DISI maske ile saf #000000 kalir."""
    return np.clip((255.0 - g.astype(F32)) * m + 0.5, 0, 255).astype(np.uint8)


def verify_inverted(depth: np.ndarray, inv: np.ndarray) -> None:
    """Merkez bolgede depth + inverted == 255 (+-1); koseler ve cember disi 0 olmali."""
    c = slice(800, 3200)
    s = depth[c, c].astype(np.int16) + inv[c, c].astype(np.int16)
    if np.abs(s - 255).max() > 1:
        raise RuntimeError("Inverted dogrulamasi basarisiz: ic bolge 255 - depth degil.")
    if not all(int(inv[y, x]) == 0 for y in (0, -1) for x in (0, -1)):
        raise RuntimeError("Inverted dogrulamasi basarisiz: koseler #000000 degil.")


def verify_depth(path: Path) -> str:
    with Image.open(path) as im:
        dpi = im.info.get("dpi", (0, 0))
        ok = im.size == (flb.DEPTH_SIZE, flb.DEPTH_SIZE) and im.mode == "L" and round(dpi[0]) == 300
        a = np.asarray(im)
    corners_black = int(a[0, 0]) == 0 and int(a[0, -1]) == 0 and int(a[-1, 0]) == 0 and int(a[-1, -1]) == 0
    mb = path.stat().st_size / 1e6
    if not (ok and corners_black):
        raise RuntimeError(f"Depth map dogrulamasi basarisiz (boyut/mod/DPI/kose): {path}")
    return f"{mb:.1f} MB" + ("" if mb < 20 else "  !! >20 MB (Etsy siniri)")


def process_product(name: str, src: str, out_root: str, no_video: bool, skip_existing: bool,
                    delight: bool = True) -> dict:
    t0 = time.time()
    out_dir = Path(out_root) / name
    depth_name = f"{name}_3D_DepthMap_300DPI.png"
    res = {"name": name, "status": "ok", "notes": [], "seconds": 0.0, "error": ""}
    try:
        need = [depth_name, inverted_name(name)] + FILES[:-1] + ([] if no_video else [FILES[-1]])
        if skip_existing and all((out_dir / f).is_file() for f in need):
            res["status"] = "skipped"
            return res
        out_dir.mkdir(parents=True, exist_ok=True)

        bgr, alpha = load_bgr_alpha(Path(src))
        gray, mask, info = auto_depth_normalizer(bgr, alpha)
        res["notes"].append(info)

        phi = None
        if delight:
            gray_in = gray
            gray, phi, conf = remove_directional_light(gray, mask)
            if phi is None:
                res["notes"].append(f"isik izi: eksen belirsiz (guven={conf:.2f}) -> duzeltme uygulanmadi")
            else:
                before = light_bias_pct(flb.build_depth_map(gray_in, mask), phi)

        depth, g_tone, m_full = flb.build_depth_map(gray, mask, return_parts=True)
        if delight and phi is not None:
            after = light_bias_pct(depth, phi)
            flag = "" if after <= DELIGHT_QA_LIMIT else f"  !! QA: >%{DELIGHT_QA_LIMIT:.0f}, gorseli kontrol et"
            res["notes"].append(f"isik izi: eksen={np.degrees(phi) % 180:.0f} derece, guven={conf:.2f}, "
                                f"dis bant egimi %{before:.1f} -> %{after:.1f}{flag}")
        flb.save_png(depth, out_dir / depth_name)
        res["notes"].append("depth " + verify_depth(out_dir / depth_name))

        inv = make_inverted(g_tone, m_full)
        verify_inverted(depth, inv)
        flb.save_png(inv, out_dir / inverted_name(name))
        res["notes"].append("inverted " + verify_depth(out_dir / inverted_name(name)))
        del g_tone, m_full, inv

        wood_img = flb.render_wood_mockup(depth)
        flb.save_jpg(wood_img, out_dir / FILES[0])
        wood_rgb = np.asarray(wood_img.convert("RGB"))

        brass = flb.render_brass_mockup(depth)
        flb.save_jpg(brass, out_dir / FILES[1])
        brass_rgb = to_u8(brass)

        slate = render_slate_mockup(depth)
        flb.save_jpg(slate, out_dir / FILES[2])
        slate_rgb = np.asarray(slate)

        flb.save_jpg(render_comparison_guide(depth, wood_rgb, brass_rgb, re.sub(r"^\d+[_\s-]*", "", name).replace("_", " ")), out_dir / FILES[3])

        if not no_video:
            summary = mlv.build_video(depth, cv2.cvtColor(wood_rgb, cv2.COLOR_RGB2BGR),
                                      [cv2.cvtColor(brass_rgb, cv2.COLOR_RGB2BGR),
                                       cv2.cvtColor(slate_rgb, cv2.COLOR_RGB2BGR)],
                                      out_dir / FILES[4], quiet=True)
            res["notes"].append("video " + summary)
    except Exception as e:  # tek urun hatasi digerlerini durdurmaz
        res["status"] = "FAILED"
        res["error"] = f"{type(e).__name__}: {e}"
        traceback.print_exc()
    res["seconds"] = time.time() - t0
    return res


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description="inputs/ klasorunu toplu isler, outputs/<urun>/ uretir.")
    ap.add_argument("--inputs", type=Path, default=INPUT_DIR)
    ap.add_argument("--outputs", type=Path, default=OUTPUT_DIR)
    ap.add_argument("--only", nargs="*", help="sadece bu urun adlarini isle")
    ap.add_argument("--skip-existing", action="store_true", help="tam seti olan urunleri atla")
    ap.add_argument("--no-video", action="store_true", help="MP4 uretme (hizli)")
    ap.add_argument("--workers", type=int, default=1, help="paralel urun sayisi (her biri ~2 GB RAM)")
    ap.add_argument("--no-delight", action="store_true", help="isik izi temizlemeyi kapat (karsilastirma icin)")
    args = ap.parse_args()

    if not args.inputs.is_dir():
        args.inputs.mkdir(parents=True, exist_ok=True)
        print(f"'{args.inputs}' olusturuldu. Gorselleri (png/jpg/jpeg/webp) buraya koyup tekrar calistir.")
        return 1
    jobs = collect_inputs(args.inputs, args.only)
    if not jobs:
        print(f"HATA: {args.inputs} icinde islenecek gorsel yok.", file=sys.stderr)
        return 1
    args.outputs.mkdir(parents=True, exist_ok=True)
    print(f"{len(jobs)} urun isleniyor -> {args.outputs}")

    results: list[dict] = []
    t0 = time.time()
    job_args = lambda n, p: (n, str(p), str(args.outputs), args.no_video, args.skip_existing,  # noqa: E731
                             not args.no_delight)
    if args.workers > 1 and len(jobs) > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs = {ex.submit(process_product, *job_args(n, p)): n for n, p in jobs}
            for f in as_completed(futs):
                r = f.result()
                results.append(r)
                print(f"  [{r['status']}] {r['name']} ({r['seconds']:.0f} sn)")
    else:
        for n, p in jobs:
            print(f"-> {n}")
            r = process_product(*job_args(n, p))
            results.append(r)
            print(f"  [{r['status']}] {r['name']} ({r['seconds']:.0f} sn)")

    print("\n=== OZET ===")
    for r in sorted(results, key=lambda x: x["name"]):
        print(f"{r['status']:8s} {r['name']:<32s} {r['seconds']:5.0f} sn")
        for note in r["notes"]:
            print(f"           - {note}")
        if r["error"]:
            print(f"           ! {r['error']}")
    failed = [r for r in results if r["status"] == "FAILED"]
    print(f"\n{len(results) - len(failed)}/{len(results)} basarili, toplam {time.time() - t0:.0f} sn.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
