#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
first_launch_builder.py  -  Forge Depth Studio / Etsy launch pack generator

Tek dosya, harici model yok. Bagimliliklar: opencv-python, numpy, Pillow

    pip install opencv-python numpy Pillow

Girdi : ./input_wolf.png   (script ile ayni klasorde)
Cikti : ./etsy_launch_pack/
        Viking_Wolf_3D_DepthMap_300DPI.png
        01_Main_Cover_Wood_Engraving_Mockup.jpg
        02_Brass_Coin_Relief_Mockup.jpg
        Shop_Logo_500x500.png
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE_DIR = Path(__file__).resolve().parent
INPUT_PATH = BASE_DIR / "input_wolf.png"
OUT_DIR = BASE_DIR / "etsy_launch_pack"

WORK_SIZE = 2000      # on isleme cozunurlugu (depth map)
DEPTH_SIZE = 4000     # teslim edilen depth map
MOCK_SIZE = 2000      # vitrin fotograflari
DPI = (300, 300)

F32 = np.float32


# --------------------------------------------------------------------------- #
# Genel yardimcilar
# --------------------------------------------------------------------------- #
def smoothstep(e0: float, e1: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def norm01(a: np.ndarray) -> np.ndarray:
    lo, hi = float(a.min()), float(a.max())
    return (a - lo) / (hi - lo + 1e-8)


def circle_mask(size: int, radius: float | None = None) -> np.ndarray:
    """Kenari 1px anti-alias'li (0..1) dairesel maske; disi tam 0."""
    r = size / 2.0 if radius is None else radius
    c = (size - 1) / 2.0
    ax = np.arange(size, dtype=F32) - F32(c)
    dist = np.sqrt(ax[None, :] ** 2 + ax[:, None] ** 2)
    return np.clip(F32(r + 0.5) - dist, 0.0, 1.0).astype(F32)


def load_gray(path: Path) -> np.ndarray:
    data = np.fromfile(str(path), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Gorsel okunamadi: {path}")
    if img.dtype == np.uint16:
        img = np.round(img / 257.0).astype(np.uint8)
    elif img.dtype != np.uint8:
        img = cv2.normalize(img.astype(F32), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    if img.ndim == 2:
        return img
    if img.shape[2] == 4:  # seffaflik -> siyah zemin uzerine
        alpha = img[..., 3:4].astype(F32) / 255.0
        img = np.round(img[..., :3].astype(F32) * alpha).astype(np.uint8)
    return cv2.cvtColor(img[..., :3], cv2.COLOR_BGR2GRAY)


def center_square(img: np.ndarray) -> np.ndarray:
    h, w = img.shape[:2]
    s = min(h, w)
    y0, x0 = (h - s) // 2, (w - s) // 2
    return img[y0:y0 + s, x0:x0 + s]


def save_png(arr_or_img, path: Path, **kw) -> None:
    img = arr_or_img if isinstance(arr_or_img, Image.Image) else Image.fromarray(arr_or_img)
    img.save(path, format="PNG", dpi=DPI, optimize=True, **kw)


def save_jpg(rgb01: np.ndarray | Image.Image, path: Path) -> None:
    if isinstance(rgb01, Image.Image):
        img = rgb01.convert("RGB")
    else:
        img = Image.fromarray(np.clip(rgb01 * 255.0 + 0.5, 0, 255).astype(np.uint8), "RGB")
    img.save(path, format="JPEG", quality=95, subsampling=0, optimize=True, dpi=DPI)


# --------------------------------------------------------------------------- #
# 1) Depth map
# --------------------------------------------------------------------------- #
def build_depth_map(gray: np.ndarray) -> np.ndarray:
    g = center_square(gray)
    interp = cv2.INTER_AREA if g.shape[0] > WORK_SIZE else cv2.INTER_LANCZOS4
    g = cv2.resize(g, (WORK_SIZE, WORK_SIZE), interpolation=interp)

    g = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(g)
    g = cv2.bilateralFilter(g, 9, 60, 9)
    g = cv2.bilateralFilter(g, 9, 40, 7)

    # Daire icindeki tonlari 0-255'e ger (derinlik kontrasti)
    inside = circle_mask(WORK_SIZE) > 0.5
    lo, hi = np.percentile(g[inside], (0.5, 99.5))
    g = np.clip((g.astype(F32) - lo) / max(hi - lo, 1.0) * 255.0, 0, 255).astype(np.uint8)

    g = cv2.resize(g, (DEPTH_SIZE, DEPTH_SIZE), interpolation=cv2.INTER_LANCZOS4)
    m = circle_mask(DEPTH_SIZE)                      # disi saf #000000
    return np.clip(g.astype(F32) * m + 0.5, 0, 255).astype(np.uint8)


# --------------------------------------------------------------------------- #
# Prosedurel doku & isik yardimcilari
# --------------------------------------------------------------------------- #
def value_noise(rng, h: int, w: int, cy: int, cx: int) -> np.ndarray:
    grid = rng.random((cy + 3, cx + 3)).astype(F32)
    return cv2.resize(grid, (w, h), interpolation=cv2.INTER_CUBIC)


def fbm(rng, h: int, w: int, cy: int, cx: int, octaves: int = 4, gain: float = 0.5) -> np.ndarray:
    out = np.zeros((h, w), F32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        out += F32(amp) * norm01(value_noise(rng, h, w, cy * 2 ** o, cx * 2 ** o))
        tot += amp
        amp *= gain
    return norm01(out / tot)


def make_walnut(size: int, rng) -> np.ndarray:
    """Koyu ceviz agaci - prosedurel RGB (0..1)."""
    h = w = size
    yy = np.linspace(0, 1, h, dtype=F32)[:, None]
    warp = fbm(rng, h, w, 3, 5, 3)
    mid = fbm(rng, h, w, 22, 9, 4)
    t = yy * 11.0 + (warp - 0.5) * 1.6 + (mid - 0.5) * 0.45
    rings = (0.5 + 0.5 * np.sin(2 * np.pi * t)) ** 1.4
    fiber = fbm(rng, h, w, 650, 12, 3, 0.55)       # x yonunde uzun lifler
    pores = fbm(rng, h, w, 1000, 55, 2)
    streak = fbm(rng, h, w, 120, 3, 3)
    v = norm01(0.30 * rings + 0.34 * fiber + 0.12 * mid + 0.24 * streak)
    v = v * (1.0 - 0.40 * smoothstep(0.60, 0.82, pores))

    stops = np.array([0.0, 0.30, 0.62, 1.0])
    cols = np.array([(24, 14, 9), (46, 28, 18), (76, 49, 31), (118, 79, 50)], np.float64) / 255.0
    rgb = np.stack([np.interp(v, stops, cols[:, i]) for i in range(3)], -1).astype(F32)
    return rgb


# Sol-ust, 45 derece yukseklik isigi. Goruntu koordinati: x sag, y asagi.
L_VEC = np.array([-0.5, -0.5, np.sqrt(0.5)], F32)
_H = L_VEC + np.array([0, 0, 1], F32)
H_VEC = (_H / np.linalg.norm(_H)).astype(F32)
LIGHT_XY = (-np.sqrt(0.5), -np.sqrt(0.5))


def height_gradients(hs: np.ndarray):
    gx = cv2.Sobel(hs, cv2.CV_32F, 1, 0, ksize=3) / 8.0
    gy = cv2.Sobel(hs, cv2.CV_32F, 0, 1, ksize=3) / 8.0
    return gx, gy


def shade_terms(gx: np.ndarray, gy: np.ndarray):
    """Yuzey normali n = (-gx,-gy,1)/|.|  ->  (n, diffuse/L.z, n.H)"""
    inv = 1.0 / np.sqrt(gx * gx + gy * gy + 1.0)
    nx, ny, nz = -gx * inv, -gy * inv, inv
    ndl = np.clip(nx * L_VEC[0] + ny * L_VEC[1] + nz * L_VEC[2], 0.0, 1.0)
    ndh = np.clip(nx * H_VEC[0] + ny * H_VEC[1] + nz * H_VEC[2], 0.0, 1.0)
    return (nx, ny, nz), ndl / L_VEC[2], ndh


def cast_shadow(hs: np.ndarray, steps: int = 20, step_px: float = 1.5, tan_elev: float = 1.0) -> np.ndarray:
    """Yukseklik haritasindan isik yonune dogru isin izleme (yumusak golge)."""
    hh, ww = hs.shape
    best = np.zeros_like(hs)
    for k in range(1, steps + 1):
        m = np.float32([[1, 0, k * step_px * LIGHT_XY[0]], [0, 1, k * step_px * LIGHT_XY[1]]])
        sh = cv2.warpAffine(hs, m, (ww, hh), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                            borderMode=cv2.BORDER_REPLICATE)
        best = np.maximum(best, sh - hs - F32(k * step_px * tan_elev))
    return cv2.GaussianBlur(np.clip(best / 3.0, 0, 1), (0, 0), 1.5)


def cavity(hs: np.ndarray, sigma: float, cap: float) -> np.ndarray:
    """Ambient occlusion yaklasimi: bulanik yukseklik - yukseklik."""
    return np.clip(cv2.GaussianBlur(hs, (0, 0), sigma) - hs, 0, cap) / cap


def paste_center(canvas: np.ndarray, patch: np.ndarray, cx: int, cy: int) -> None:
    ph, pw = patch.shape[:2]
    y0, x0 = cy - ph // 2, cx - pw // 2
    canvas[y0:y0 + ph, x0:x0 + pw] = patch


# --------------------------------------------------------------------------- #
# Yazi yardimcilari
# --------------------------------------------------------------------------- #
_BOLD_FONTS = [
    "DejaVuSans-Bold.ttf", "arialbd.ttf", "Arial Bold.ttf", "LiberationSans-Bold.ttf",
    "Helvetica-Bold.ttf", "SegoeUI-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf",
]


def load_font(size: int):
    for name in _BOLD_FONTS:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)   # Pillow >= 10.1
    except TypeError:
        return ImageFont.load_default()


def tracked_width(draw, text: str, font, tracking: float) -> float:
    return sum(draw.textlength(ch, font=font) for ch in text) + tracking * (len(text) - 1)


def draw_tracked(draw, cx: float, cy: float, text: str, font, fill, tracking: float) -> None:
    """Harf araligi ayarli, yatay+dikey ortalanmis yazi."""
    l, t, r, b = draw.textbbox((0, 0), "H", font=font)
    x = cx - tracked_width(draw, text, font, tracking) / 2.0
    y = cy - (t + b) / 2.0
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking


def add_badge(img: Image.Image, text: str) -> Image.Image:
    """Sag alt kose endustriyel rozet/bant."""
    img = img.convert("RGBA")
    W, H = img.size
    probe = ImageDraw.Draw(img)
    size = 36
    while True:
        font = load_font(size)
        tw = tracked_width(probe, text, font, 2.5)
        if tw <= W * 0.72 or size <= 16:
            break
        size -= 2
    pad_x, bh, margin = 54, 92, 64
    bw = int(tw + pad_x * 2 + 26)
    x1, y1 = W - margin, H - margin
    x0, y0 = x1 - bw, y1 - bh

    # golge
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x0 + 8, y0 + 14, x1 + 8, y1 + 14), 12, fill=(0, 0, 0, 170))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(16)))

    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle((x0, y0, x1, y1), 12, fill=(17, 18, 20, 232), outline=(212, 154, 54, 255), width=3)
    d.rounded_rectangle((x0 + 9, y0 + 9, x1 - 9, y1 - 9), 6, outline=(212, 154, 54, 90), width=1)
    d.rectangle((x0 + 3, y0 + 3, x0 + 24, y1 - 3), fill=(212, 154, 54, 255))     # amber serit
    for (rx, ry) in ((x0 + 13, y0 + 14), (x0 + 13, y1 - 14)):                    # perçinler
        d.ellipse((rx - 3, ry - 3, rx + 3, ry + 3), fill=(60, 40, 14, 255))
    for (rx, ry) in ((x1 - 16, y0 + 16), (x1 - 16, y1 - 16)):
        d.ellipse((rx - 4, ry - 4, rx + 4, ry + 4), fill=(70, 72, 76, 255), outline=(140, 142, 148, 255))
    draw_tracked(d, (x0 + 26 + x1 - 16) / 2.0, (y0 + y1) / 2.0, text, font, (244, 220, 168, 255), 2.5)
    return Image.alpha_composite(img, ov)


# --------------------------------------------------------------------------- #
# 2) Ceviz ahsap oyma mockup
# --------------------------------------------------------------------------- #
def render_wood_mockup(depth: np.ndarray) -> Image.Image:
    S, D = MOCK_SIZE, 1400
    rng = np.random.default_rng(7)
    wood = make_walnut(S, rng)

    d = cv2.resize(depth, (D, D), interpolation=cv2.INTER_AREA).astype(F32) / 255.0
    x0, y0 = (S - D) // 2, (S - D) // 2 - 40
    h = np.ones((S, S), F32)                       # 1 = islenmemis yuzey
    h[y0:y0 + D, x0:x0 + D] = 1.0 - circle_mask(D) * (1.0 - d)

    hs = cv2.GaussianBlur(h * F32(24.0), (0, 0), 1.4)          # ~4 mm oyma -> piksel
    gx, gy = height_gradients(hs)
    (nx, ny, nz), shade, ndh = shade_terms(gx, gy)
    shadow = cast_shadow(hs)
    ao = np.clip(0.65 * cavity(hs, 9, 10) + 0.5 * cavity(hs, 32, 14), 0, 1)

    # Lazer yanigi: derin = koyu + color burn
    burn = cv2.GaussianBlur(np.clip(1.0 - h, 0, 1), (0, 0), 0.7)[..., None]
    base = wood * (1.0 - 0.55 * burn) * (1.0 + 0.0 * burn)
    s = np.clip(1.0 - 0.72 * burn ** 0.9, 0.05, 1.0)
    cburn = np.clip(1.0 - (1.0 - wood) / s, 0, 1)
    char = np.array([0.20, 0.13, 0.09], F32)
    base = base * (1 - 0.40 * burn) + (cburn * 0.5 + char * 0.5) * 0.40 * burn
    base = np.clip(base, 0, 1)

    light_col = np.array([1.00, 0.88, 0.70], F32)
    spec_col = np.array([1.00, 0.86, 0.62], F32)
    ambient = 0.30 * (1.0 - 0.65 * ao)
    key = 0.92 * shade * (1.0 - 0.78 * shadow) * (1.0 - 0.35 * ao)
    spec = (ndh ** 26) * 0.10 * (1.0 - shadow)
    col = base * ((ambient + key)[..., None] * light_col) + spec[..., None] * spec_col

    # Studyo isigi: sol-ust sicak, kenarlarda vinyet
    yy, xx = np.mgrid[0:S, 0:S].astype(F32)
    grad = 1.22 - 0.50 * ((xx + yy) / (2.0 * S))
    r = np.sqrt((xx - S / 2) ** 2 + (yy - S / 2) ** 2) / (S * 0.72)
    col *= (grad * (1.0 - 0.35 * r ** 2.2))[..., None]
    col += rng.normal(0, 0.008, (S, S, 1)).astype(F32)              # film greni
    col = np.clip(col, 0, 1) ** F32(1 / 1.12)

    img = Image.fromarray(np.clip(col * 255 + 0.5, 0, 255).astype(np.uint8), "RGB")
    return add_badge(img, "3D DEPTH MAP | 300 DPI PNG | LIGHTBURN & CNC READY")


# --------------------------------------------------------------------------- #
# 3) Antik pirinc madalyon mockup
# --------------------------------------------------------------------------- #
def render_brass_mockup(depth: np.ndarray) -> np.ndarray:
    S, R, cx, cy = MOCK_SIZE, 770, 1000, 950
    rng = np.random.default_rng(11)
    yy, xx = np.mgrid[0:S, 0:S].astype(F32)
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)

    # Antrasit zemin (hafif firca dokusu + sol-ust isik havuzu)
    pool = np.exp(-np.sqrt((xx - 600) ** 2 + (yy - 450) ** 2) / 1150.0)
    brushed = fbm(rng, S, S, 900, 5, 2) - 0.5
    bg_lum = 0.090 + 0.085 * pool + 0.030 * brushed
    bg = bg_lum[..., None] * np.array([1.0, 1.02, 1.08], F32)

    # Madalyon yukseklik haritasi
    coin = np.clip(F32(R + 0.5) - dist, 0, 1)
    bevel = smoothstep(0.0, 1.0, np.clip((R - dist) / 16.0, 0, 1))
    rim = np.exp(-(((dist - (R - 58)) / 20.0) ** 2))
    groove = np.exp(-(((dist - (R - 100)) / 5.0) ** 2))
    field_r = R - 104
    df = 2 * field_r
    rel = np.zeros((S, S), F32)
    paste_center(rel, cv2.resize(depth, (df, df), interpolation=cv2.INTER_AREA).astype(F32) / 255.0, cx, cy)
    fw = np.clip((field_r - dist) / 3.0 + 0.5, 0, 1)
    h = (0.20 * bevel + 0.20 * rim - 0.06 * groove) * coin + 0.46 * fw * rel * coin

    hs = cv2.GaussianBlur(h * F32(62.0), (0, 0), 0.9)
    gx, gy = height_gradients(hs)
    # Mikro pürüz (firca/doku) -> normallere hafif bozulma
    gx += (fbm(rng, S, S, 700, 700, 2) - 0.5) * 0.35
    gy += (fbm(rng, S, S, 700, 700, 2) - 0.5) * 0.35
    (nx, ny, nz), diff, ndh = shade_terms(gx, gy)
    shadow = cast_shadow(hs, steps=22, step_px=1.6)
    ao = np.clip(0.7 * cavity(hs, 8, 9) + 0.5 * cavity(hs, 28, 14), 0, 1)

    # Albedo: yukseklige gore pirinc rampasi + patina + kir
    t = np.clip(h / 0.85, 0, 1)
    stops = np.array([0.0, 0.30, 0.65, 1.0])
    cols = np.array([(40, 25, 13), (110, 76, 32), (178, 134, 60), (228, 190, 108)], np.float64) / 255.0
    alb = np.stack([np.interp(t, stops, cols[:, i]) for i in range(3)], -1).astype(F32)
    alb *= (1.0 - 0.60 * ao)[..., None]
    pat = smoothstep(0.55, 0.78, fbm(rng, S, S, 10, 10, 4)) * np.clip(0.35 + 1.1 * ao, 0, 1)
    pat = np.clip(pat * 0.8, 0, 1)
    alb = alb * (1 - pat[..., None]) + pat[..., None] * np.array([0.22, 0.27, 0.19], F32)
    grime = smoothstep(0.62, 0.85, fbm(rng, S, S, 380, 380, 2))
    alb *= (1.0 - 0.35 * grime)[..., None]

    # Metalik aydinlatma: diffuse + ortam yansimasi + keskin & genis specular
    env = np.clip(0.5 - 0.8 * (nx + ny), 0, 1)
    spec = (0.95 * ndh ** 90 + 0.30 * ndh ** 14) * (1 - 0.75 * pat) * (1 - 0.5 * ao)
    lit = 0.16 + 0.55 * diff * (1 - 0.7 * shadow) + 0.60 * env ** 1.6 * (1 - 0.5 * shadow)
    col = alb * (lit * (1 - 0.45 * ao))[..., None]
    col += spec[..., None] * (1 - 0.8 * shadow[..., None]) * np.array([1.0, 0.89, 0.64], F32)

    # Zemin uzerine yerlestir + drop shadow
    def shifted_blur(dx, dy, sigma):
        m = np.float32([[1, 0, -dx], [0, 1, -dy]])
        sm = cv2.warpAffine(coin, m, (S, S), flags=cv2.INTER_LINEAR, borderValue=0)
        return cv2.GaussianBlur(sm, (0, 0), sigma)

    drop = np.clip(0.78 * shifted_blur(30, 44, 36) + 0.55 * shifted_blur(7, 11, 7), 0, 0.92)
    bg = bg * (1.0 - drop[..., None])
    out = bg * (1 - coin[..., None]) + np.clip(col, 0, 1) * coin[..., None]
    out *= (1.0 - 0.30 * (np.sqrt((xx - S / 2) ** 2 + (yy - S / 2) ** 2) / (S * 0.72)) ** 2)[..., None]
    out += rng.normal(0, 0.006, (S, S, 1)).astype(F32)
    return np.clip(out, 0, 1)


# --------------------------------------------------------------------------- #
# 4) Magaza logosu
# --------------------------------------------------------------------------- #
def render_logo() -> Image.Image:
    K = 4                                  # supersampling
    W = 500 * K
    rng = np.random.default_rng(3)

    # Karbon fiber dokulu antrasit zemin
    yy, xx = np.mgrid[0:W, 0:W].astype(F32)
    per = 3.0 * K
    weave = np.sin(xx * np.pi / per) * np.sin(yy * np.pi / per)
    twill = np.sin((xx + yy) * np.pi / (2 * per))
    r = np.sqrt((xx - W / 2) ** 2 + (yy - W * 0.42) ** 2) / (W * 0.62)
    lum = (0.082 + 0.014 * weave + 0.008 * twill) * (1.25 - 0.75 * np.clip(r, 0, 1.2) ** 1.6)
    lum += rng.normal(0, 0.003, (W, W)).astype(F32)
    bg = (np.clip(lum, 0, 1)[..., None] * np.array([1.0, 1.03, 1.10], F32) * 255.0)

    amber = (255, 176, 40)
    core = (255, 224, 140)

    def P(pts):
        return [(x * K, y * K) for x, y in pts]

    anvil = [(146, 150), (326, 150), (326, 172), (294, 181), (286, 207), (302, 232),
             (332, 232), (332, 250), (168, 250), (168, 232), (198, 232), (214, 207),
             (208, 184), (178, 176), (160, 164)]
    beam = [(340, 92), (262, 148)]
    slices = [((190, 264), (310, 264)), ((206, 274), (294, 274)), ((222, 284), (278, 284))]

    def draw_icon(d, color, w):
        d.ellipse(P([(250 - 128, 185 - 128), (250 + 128, 185 + 128)]), outline=color, width=int(w * 0.8 * K))
        d.line(P(anvil + [anvil[0]]), fill=color, width=int(w * K), joint="curve")
        d.line(P(beam), fill=color, width=int(w * 0.9 * K))
        for a, b in slices:
            d.line(P([a, b]), fill=color, width=int(w * 0.7 * K))
        # kivilcimlar
        for ang, ln in ((200, 22), (232, 26), (264, 24), (296, 26), (328, 22)):
            ca, sa = np.cos(np.radians(ang)), np.sin(np.radians(ang))
            d.line(P([(262 + ca * 7, 148 + sa * 7), (262 + ca * (7 + ln), 148 + sa * (7 + ln))]),
                   fill=color, width=int(w * 0.6 * K))
        d.ellipse(P([(257, 143), (267, 153)]), fill=color)
        d.polygon(P([(340, 84), (348, 92), (340, 100), (332, 92)]), fill=color)

    # Glow (blur'lanmis kalin cizgi) -> toplamsal karisim
    glow_mask = Image.new("L", (W, W), 0)
    draw_icon(ImageDraw.Draw(glow_mask), 255, 7)
    glow_mask = glow_mask.filter(ImageFilter.GaussianBlur(9 * K))
    g = np.asarray(glow_mask, F32)[..., None] / 255.0
    bg = np.clip(bg + g * np.array(amber, F32) * 0.55, 0, 255)

    img = Image.fromarray(bg.astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img)
    draw_icon(d, amber, 3.4)
    draw_icon(d, core, 1.1)

    # Ayirici cizgi + yazi
    d.line(P([(150, 338), (232, 338)]), fill=(150, 104, 30), width=2 * K)
    d.line(P([(268, 338), (350, 338)]), fill=(150, 104, 30), width=2 * K)
    d.polygon(P([(250, 332), (256, 338), (250, 344), (244, 338)]), fill=amber)

    text = "FORGE DEPTH STUDIO"
    size = 34 * K
    while True:
        font = load_font(size)
        tw = tracked_width(d, text, font, 4.5 * K)
        if tw <= 420 * K or size <= 8 * K:
            break
        size -= K
    draw_tracked(d, W / 2, 378 * K, text, font, (246, 200, 96), 4.5 * K)

    return img.resize((500, 500), Image.LANCZOS)


# --------------------------------------------------------------------------- #
def main() -> int:
    if not INPUT_PATH.is_file():
        print(f"HATA: '{INPUT_PATH.name}' bulunamadi. Dosyayi su klasore koy: {BASE_DIR}", file=sys.stderr)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[1/4] Depth map uretiliyor (CLAHE + Bilateral + Lanczos4 -> 4000x4000)...")
    depth = build_depth_map(load_gray(INPUT_PATH))
    save_png(depth, OUT_DIR / "Viking_Wolf_3D_DepthMap_300DPI.png")

    print("[2/4] Ceviz ahsap oyma mockup...")
    save_jpg(render_wood_mockup(depth), OUT_DIR / "01_Main_Cover_Wood_Engraving_Mockup.jpg")

    print("[3/4] Antik pirinc madalyon mockup...")
    save_jpg(render_brass_mockup(depth), OUT_DIR / "02_Brass_Coin_Relief_Mockup.jpg")

    print("[4/4] Magaza logosu...")
    save_png(render_logo().convert("RGB"), OUT_DIR / "Shop_Logo_500x500.png")

    print(f"\nTamam. Dosyalar: {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
