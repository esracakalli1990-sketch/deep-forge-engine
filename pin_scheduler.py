"""Faz C2: traffic_cannon pinlerinden Pinterest yayin takvimi (elle zamanlama icin kopyala-yapistir) + opsiyonel toplu CSV.

Bot YOK: pinleri kurucu Pinterest'in kendi zamanlayicisiyla (Pin olustur > "Publish at a later date") kurar.
Siralama: once tum Hero pinleri (+bundle), sonra Process, sonra Materials; ayni urun art arda gelmez.

Girdi : outputs/_Traffic_Cannon/pins.json  (traffic_cannon.py)
        --links links.json  {"_shop": "...", "01_Fenrir_Wolf": "https://www.etsy.com/listing/...", ...}
        (yoksa sablon yazilir; bos link -> magaza linki + uyari)
Cikti : outputs/_Traffic_Cannon/PINTEREST_SCHEDULE.md, schedule.json
        --media-base-url verilirse pinterest_bulk.csv (Pinterest toplu yukleme; gorseller herkese acik URL'de olmali)

Kullanim: python pin_scheduler.py --start 2026-10-26 [--per-day 2] [--links links.json] [--media-base-url https://...]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import traffic_cannon as tc

BASE_DIR = Path(__file__).resolve().parent
SHOP_URL = "https://forgedepthstudio.etsy.com"
LINK_RE = re.compile(r"^https://([a-z0-9-]+\.)?(etsy\.com|etsy\.me)(/|$)", re.I)
AUDIENCE_TZ, LOCAL_TZ = "America/New_York", "Europe/Istanbul"
SLOTS = ["09:00", "20:00", "13:00", "17:00", "22:00"]      # ABD Dogu saati; per-day kadar bastan alinir
CSV_HEADER = ["Title", "Media URL", "Pinterest board", "Thumbnail", "Description", "Link", "Publish date", "Keywords"]
VARIANT_ORDER = {"A": 0, "BUNDLE": 0, "B": 1, "C": 2}


def tz(name: str):
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(name)
    except Exception:  # noqa: BLE001  (Windows'ta tzdata yoksa)
        return None


def order_pins(pins: list[dict]) -> list[dict]:
    """Varyant turlarina gore sirala; tur icinde urun sirasi her turda kaydirilir (ayni urun art arda gelmesin)."""
    rounds: dict[int, list[dict]] = {}
    for p in pins:
        rounds.setdefault(VARIANT_ORDER.get(p["variant"], 3), []).append(p)
    out: list[dict] = []
    for r in sorted(rounds):
        grp = sorted(rounds[r], key=lambda p: p["product"])
        k = r % len(grp)
        grp = grp[k:] + grp[:k]
        if out and grp[0]["product"] == out[-1]["product"]:
            grp = grp[1:] + grp[:1]
        out += grp
    return out


def load_links(path: Path, pins: list[dict]) -> tuple[dict, list[str]]:
    keys = sorted({p["link_key"] for p in pins})
    if not path.is_file():
        path.write_text(json.dumps({"_shop": SHOP_URL, **{k: "" for k in keys}}, indent=1), encoding="utf-8")
        return {"_shop": SHOP_URL}, [f"{path.name} yoktu -> sablon yazildi; ilan linklerini doldurup tekrar calistirin"]
    links = json.loads(path.read_text(encoding="utf-8"))
    warns = []
    for k, v in list(links.items()):
        if v and not LINK_RE.match(v.strip()):
            raise ValueError(f"{k}: gecersiz link (yalniz https etsy.com / etsy.me): {v}")
        links[k] = v.strip()
    links["_shop"] = links.get("_shop") or SHOP_URL
    warns += [f"{k}: link bos -> magaza linki kullanildi" for k in keys if not links.get(k)]
    return links, warns


def build_schedule(pins: list[dict], links: dict, start: date, per_day: int) -> list[dict]:
    if not 1 <= per_day <= len(SLOTS):
        raise ValueError(f"--per-day 1..{len(SLOTS)} olmali")
    a_tz, l_tz = tz(AUDIENCE_TZ), tz(LOCAL_TZ)
    slots = sorted(SLOTS[:per_day])
    rows = []
    for i, p in enumerate(order_pins(pins)):
        day = start + timedelta(days=i // per_day)
        hh, mm = map(int, slots[i % per_day].split(":"))
        when = datetime(day.year, day.month, day.day, hh, mm, tzinfo=a_tz)
        local = when.astimezone(l_tz).strftime("%Y-%m-%d %H:%M") if a_tz and l_tz else ""
        utc = when.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") if a_tz else ""
        rows.append({**p, "link": links.get(p["link_key"]) or links["_shop"], "day": i // per_day + 1,
                     "date": day.isoformat(), "time_et": slots[i % per_day], "time_local": local, "publish_utc": utc})
    return rows


def render_md(rows: list[dict], warns: list[str]) -> str:
    L = ["# Pinterest yayin takvimi (elle zamanlama)", "",
         "Pinterest > Olustur > Pin: gorseli yukle, alanlari asagidan kopyala, panoyu sec, "
         "**Publish at a later date** ile tarih/saati kur. Saatler ABD Dogu (ET); parantezde Turkiye saati.", ""]
    L += [f"> UYARI: {w}" for w in warns] + ([""] if warns else [])
    day = None
    for r in rows:
        if r["day"] != day:
            day = r["day"]
            L += [f"## Gun {day} — {r['date']}", ""]
        tr = f" ({r['time_local']} TR)" if r["time_local"] else ""
        L += [f"### {r['time_et']} ET{tr} — `{r['file']}`", f"- **Pano:** {r['board']}",
              "- **Baslik:**", "```", r["title"], "```", "- **Aciklama:**", "```", r["description"], "```",
              "- **Alt metin:**", "```", r["alt_text"], "```", "- **Link:**", "```", r["link"], "```", ""]
    return "\n".join(L)


def write_csv(rows: list[dict], path: Path, base_url: str) -> None:
    if not base_url.startswith("https://"):
        raise ValueError("--media-base-url https:// ile baslamali")
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(CSV_HEADER)
        for r in rows[:200]:                                    # Pinterest toplu yukleme ust siniri
            w.writerow([r["title"], base_url.rstrip("/") + "/" + r["file"], r["board"], "", r["description"],
                        r["link"], r["publish_utc"], r["keywords"]])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--outputs", type=Path, default=BASE_DIR / "outputs")
    ap.add_argument("--start", default=(date.today() + timedelta(days=1)).isoformat(), help="YYYY-MM-DD (ilk gun)")
    ap.add_argument("--per-day", type=int, default=2, help="gunluk pin (yeni hesap: 2-3)")
    ap.add_argument("--links", type=Path, default=BASE_DIR / "links.json")
    ap.add_argument("--media-base-url", default=None, help="gorsellerin herkese acik klasor URL'si (CSV icin)")
    args = ap.parse_args()
    try:
        tdir = args.outputs / tc.TC_DIR
        pins = json.loads((tdir / "pins.json").read_text(encoding="utf-8"))
        links, warns = load_links(args.links, pins)
        rows = build_schedule(pins, links, date.fromisoformat(args.start), args.per_day)
        (tdir / "PINTEREST_SCHEDULE.md").write_text(render_md(rows, warns), encoding="utf-8")
        (tdir / "schedule.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
        if args.media_base_url:
            write_csv(rows, tdir / "pinterest_bulk.csv", args.media_base_url)
    except FileNotFoundError as e:
        print(f"HATA: {e} (once traffic_cannon.py)", file=sys.stderr)
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"HATA: {e}", file=sys.stderr)
        return 1
    for w in warns:
        print(f"UYARI: {w}")
    print(f"{len(rows)} pin, {rows[-1]['day']} gun ({rows[0]['date']} -> {rows[-1]['date']}) -> {tdir / 'PINTEREST_SCHEDULE.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
