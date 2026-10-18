#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_listing_video.py  -  Etsy listing videosu (10 sn, 1080x1080, 30 FPS, sessiz)

Girdi  : etsy_launch_pack/Viking_Wolf_3D_DepthMap_300DPI.png
         etsy_launch_pack/01_Main_Cover_Wood_Engraving_Mockup.jpg
         etsy_launch_pack/02_Brass_Coin_Relief_Mockup.jpg
Cikti  : etsy_launch_pack/03_Etsy_Listing_Video.mp4

Zaman cizelgesi
  0.0 - 3.5 sn : ham depth map; yukaridan asagi lazer cizgisi gecer, gectigi yer ahsap oymaya donusur
  3.5 - 7.0 sn : ahsap mockup uzerinde yumusak Ken Burns zoom-in (rozet kadrajda kalir)
  7.0 - 10  sn : crossfade ile antik pirinc madalyon + hafif zoom

Kullanim:
    python make_listing_video.py
    python make_listing_video.py --pack-dir yol/etsy_launch_pack

Kodlama: ffmpeg (PATH'te veya `pip install imageio-ffmpeg`) varsa H.264 / yuv420p / faststart.
Yoksa OpenCV VideoWriter'a duser (avc1 -> mp4v) ve uyari verir.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_PACK = BASE_DIR / "etsy_launch_pack"

DEPTH_NAME = "Viking_Wolf_3D_DepthMap_300DPI.png"
WOOD_NAME = "01_Main_Cover_Wood_Engraving_Mockup.jpg"
BRASS_NAME = "02_Brass_Coin_Relief_Mockup.jpg"
VIDEO_NAME = "03_Etsy_Listing_Video.mp4"

SIZE = 1080
FPS = 30
DURATION = 10.0
N_FRAMES = int(round(FPS * DURATION))
SRC = 1620                     # kaynaklar 1.5x supersample; warp ile 1080'e iner

T_WIPE_END = 3.5
T_WOOD_END = 7.0
T_FADE = 1.2                   # crossfade suresi (7.0'de baslar)

# first_launch_builder.render_wood_mockup duzeni (2000 px uzerinde)
MOCK_S, MOCK_D, MOCK_CY_OFF = 2000, 1400, -40

F32 = np.float32


# --------------------------------------------------------------------------- #
# Yardimcilar
# --------------------------------------------------------------------------- #
def smoothstep(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    return x * x * (3.0 - 2.0 * x)


def read_image(path: Path, flags: int = cv2.IMREAD_COLOR) -> np.ndarray:
    img = cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), flags)
    if img is None:
        raise FileNotFoundError(f"Gorsel okunamadi: {path}")
    return img


def to_src(img_bgr: np.ndarray) -> np.ndarray:
    return cv2.resize(img_bgr, (SRC, SRC), interpolation=cv2.INTER_AREA).astype(F32)


def build_depth_layer(depth_gray: np.ndarray) -> np.ndarray:
    """Depth map'i, ahsap mockup'taki daire ile ayni konum/olcekte siyah zemine koy."""
    k = SRC / MOCK_S
    d = int(round(MOCK_D * k))
    cy = SRC / 2 + MOCK_CY_OFF * k
    small = cv2.resize(depth_gray, (d, d), interpolation=cv2.INTER_AREA)
    canvas = np.zeros((SRC, SRC), np.uint8)
    x0, y0 = int(round(SRC / 2 - d / 2)), int(round(cy - d / 2))
    canvas[y0:y0 + d, x0:x0 + d] = small
    return cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR).astype(F32)


def view(src: np.ndarray, zoom: float, focus: tuple[float, float] = (0.5, 0.5)) -> np.ndarray:
    """`focus` (0..1) noktasi sabit kalacak sekilde yakinlastirilmis 1080x1080 gorunum (float32 BGR)."""
    k = SIZE * zoom / SRC
    fx, fy = focus[0] * SRC, focus[1] * SRC
    m = np.float32([[k, 0, fx * SIZE / SRC - k * fx], [0, k, fy * SIZE / SRC - k * fy]])
    return cv2.warpAffine(src, m, (SIZE, SIZE), flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_REPLICATE)


# Ahsap zoom'u sag alt kosedeki rozeti kadrajda tutacak sekilde oraya sabitlenir.
WOOD_FOCUS = (0.97, 0.97)


def wood_zoom(t: float) -> float:
    return 1.0 + 0.12 * smoothstep((t - T_WIPE_END) / 4.5)


def brass_zoom(t: float) -> float:
    return 1.0 + 0.07 * smoothstep((t - T_WOOD_END) / 3.0)


# --------------------------------------------------------------------------- #
# Lazer tarama efekti
# --------------------------------------------------------------------------- #
ROWS = np.arange(SIZE, dtype=F32)
CORE_C = np.array([225, 245, 255], F32)     # BGR - beyaza yakin cekirdek
HALO_C = np.array([30, 150, 255], F32)      # BGR - turuncu
WIDE_C = np.array([10, 105, 255], F32)      # BGR - koyu turuncu/altin


def laser_y(t: float) -> float:
    p = min(max(t / T_WIPE_END, 0.0), 1.0)
    p = 0.85 * p + 0.15 * smoothstep(p)      # neredeyse dogrusal tarama
    return -30.0 + p * (SIZE + 70.0)


def laser_gain(yl: float) -> float:
    return smoothstep((yl + 30.0) / 50.0) * (1.0 - smoothstep((yl - (SIZE - 20.0)) / 60.0))


def render_scan_frame(t: float, idx: int, depth: np.ndarray, wood: np.ndarray) -> np.ndarray:
    yl = laser_y(t)
    gain = laser_gain(yl)
    out = depth.copy()

    edge = int(np.floor(yl))
    if edge > 0:
        out[:min(edge, SIZE)] = wood[:min(edge, SIZE)]
    if 0 <= edge < SIZE:
        frac = yl - edge
        out[edge] = wood[edge] * (1.0 - frac) + depth[edge] * frac

    if gain > 1e-3:
        rng = np.random.default_rng(idx)
        flick = 0.93 + 0.07 * rng.random()
        dy = ROWS - F32(yl)
        core = np.exp(-(dy / 2.3) ** 2)
        halo = np.exp(-(dy / 13.0) ** 2) * 0.85
        wide = np.exp(-(dy / 55.0) ** 2) * 0.35
        trail = np.where(dy < 0, np.exp(dy / 48.0), 0.0) * 0.30      # yeni yanmis ahsabin isisi
        add = (core[:, None] * CORE_C * 1.0 + halo[:, None] * HALO_C
               + (wide + trail)[:, None] * WIDE_C)
        out += add[:, None, :] * F32(gain * flick)

        # kivilcimlar
        layer = np.zeros_like(out)
        for _ in range(46):
            x = int(rng.integers(0, SIZE))
            y = int(yl - abs(rng.normal(0, 11.0)) + rng.normal(0, 1.5))
            r = int(rng.integers(1, 3))
            if 0 <= y < SIZE:
                cv2.circle(layer, (x, y), r, (90, 190, 255), -1, cv2.LINE_AA)
        layer = cv2.GaussianBlur(layer, (0, 0), 1.2) * 2.2
        out += layer * F32(gain)
    return out


# --------------------------------------------------------------------------- #
# Kare uretimi
# --------------------------------------------------------------------------- #
def render_frame(i: int, depth: np.ndarray, wood: np.ndarray, brass: np.ndarray) -> np.ndarray:
    t = i / FPS
    if t < T_WIPE_END:
        f = render_scan_frame(t, i, view(depth, 1.0), view(wood, 1.0))
    else:
        f = view(wood, wood_zoom(t), WOOD_FOCUS)
        a = smoothstep((t - T_WOOD_END) / T_FADE)
        if a > 0.0:
            f = f * F32(1.0 - a) + view(brass, brass_zoom(t)) * F32(a)
    return np.clip(f + 0.5, 0, 255).astype(np.uint8)


# --------------------------------------------------------------------------- #
# Kodlayici
# --------------------------------------------------------------------------- #
def find_ffmpeg() -> str | None:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg  # type: ignore
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


class FfmpegWriter:
    def __init__(self, exe: str, path: Path):
        cmd = [exe, "-y", "-loglevel", "error",
               "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{SIZE}x{SIZE}", "-r", str(FPS), "-i", "-",
               "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
               "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart",
               "-r", str(FPS), str(path)]
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        self.codec = "H.264 (ffmpeg libx264, yuv420p)"

    def write(self, frame: np.ndarray) -> None:
        self.proc.stdin.write(frame.tobytes())

    def close(self) -> None:
        self.proc.stdin.close()
        err = self.proc.stderr.read().decode(errors="replace")
        if self.proc.wait() != 0:
            raise RuntimeError(f"ffmpeg hata verdi:\n{err}")


class CvWriter:
    def __init__(self, path: Path):
        self.vw, self.codec = None, ""
        for tag in ("avc1", "mp4v"):
            vw = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*tag), FPS, (SIZE, SIZE))
            if vw.isOpened():
                self.vw, self.codec = vw, tag
                break
        if self.vw is None:
            raise RuntimeError("OpenCV VideoWriter acilamadi; ffmpeg kur: pip install imageio-ffmpeg")
        if self.codec != "avc1":
            print("UYARI: H.264 kodlayici yok, 'mp4v' kullaniliyor. Etsy'de sorun olursa "
                  "`pip install imageio-ffmpeg` ile tekrar calistir.", file=sys.stderr)

    def write(self, frame: np.ndarray) -> None:
        self.vw.write(frame)

    def close(self) -> None:
        self.vw.release()


def open_writer(path: Path):
    exe = find_ffmpeg()
    if exe:
        try:
            return FfmpegWriter(exe, path)
        except OSError as e:
            print(f"UYARI: ffmpeg baslatilamadi ({e}); OpenCV'ye geciliyor.", file=sys.stderr)
    return CvWriter(path)


def verify(path: Path) -> str:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError("Uretilen video acilamadi.")
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ok, _ = cap.read()
    cap.release()
    if not ok or (w, h) != (SIZE, SIZE) or n != N_FRAMES:
        raise RuntimeError(f"Dogrulama basarisiz: {w}x{h}, {n} kare, ilk kare okundu={ok}")
    return f"{w}x{h}, {fps:.0f} FPS, {n} kare, {n / fps:.2f} sn, {path.stat().st_size / 1e6:.2f} MB"


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description="Etsy listing videosu uretir (10 sn, 1080x1080, 30 FPS).")
    ap.add_argument("--pack-dir", type=Path, default=DEFAULT_PACK, help="etsy_launch_pack klasoru")
    args = ap.parse_args()
    pack: Path = args.pack_dir

    try:
        depth_gray = read_image(pack / DEPTH_NAME, cv2.IMREAD_GRAYSCALE)
        wood = to_src(read_image(pack / WOOD_NAME))
        brass = to_src(read_image(pack / BRASS_NAME))
    except FileNotFoundError as e:
        print(f"HATA: {e}\nOnce `python first_launch_builder.py` calistir (klasor: {pack}).", file=sys.stderr)
        return 1
    depth = build_depth_layer(depth_gray)

    out_path = pack / VIDEO_NAME
    writer = open_writer(out_path)
    print(f"Kodlayici: {writer.codec}")
    try:
        for i in range(N_FRAMES):
            writer.write(render_frame(i, depth, wood, brass))
            if i % 60 == 0:
                print(f"  kare {i}/{N_FRAMES}")
        writer.close()
    except Exception:
        try:
            writer.close()
        except Exception:
            pass
        raise

    print(f"Dogrulama: {verify(out_path)}")
    print(f"Tamam: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
