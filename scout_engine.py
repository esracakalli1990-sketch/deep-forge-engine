"""Faz D2 (one alindi): Etsy Open API v3 ile niş talep/rekabet istihbarati. Kazima YOK; yalniz resmi API.

Her anahtar kelime icin:
  1) /listings/active?keywords=...  -> toplam ilan sayisi (rekabet) + ilk N ilan (fiyat, favori, yas)
  2) /listings/{id}/reviews         -> ilan yorum sayisi -> tahmini satis (yorum / REVIEW_RATE)
  3) /shops/{shop_id}               -> magaza toplam satisi (transaction_sold_count)
Cikti: outputs/_SCOUT/hot_trends.json, SCOUT_REPORT.md, listings.csv

Anahtar: Etsy geliştirici uygulamasi (etsy.com/developers) -> ortam degiskeni ya da .env:
  ETSY_API_KEY=<keystring>        ETSY_SHARED_SECRET=<shared secret>   (header: "keystring:secret")
Kullanim: python scout_engine.py [--keywords "coin depth map" "christmas depth map"] [--top 48] [--no-reviews]

Not: satis TAHMINDIR. Dijital urunlerde alicilarin kucuk bir kismi yorum birakir (varsayilan %8, --review-rate).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import statistics as st
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Callable

BASE_DIR = Path(__file__).resolve().parent
API = "https://openapi.etsy.com/v3/application"
SCOUT_DIR = "_SCOUT"
DEFAULT_KEYWORDS = [
    "coin depth map", "fiber laser depth map", "challenge coin depth map", "depth map bundle",
    "christmas depth map", "3d relief stl laser", "16 bit depth map", "slate coaster laser engraving",
    "3d illusion laser engraving file", "cutting board laser engraving file", "christmas ornament laser file",
    "viking laser file",
]
REVIEW_RATE = 0.08
MIN_INTERVAL = 0.2                  # saniye/istek (Etsy kotasinin cok altinda)
DESIGN_RE = re.compile(r"(\d[\d,.]*)\s*\+?\s*(designs?|files?|coins?|pcs|pieces|depth ?maps?|png|svg)", re.I)

Fetch = Callable[[str, dict], dict]


# --------------------------------------------------------------------------- #
# API istemcisi
# --------------------------------------------------------------------------- #
def load_env(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def api_key() -> str:
    key, secret = os.environ.get("ETSY_API_KEY", "").strip(), os.environ.get("ETSY_SHARED_SECRET", "").strip()
    if not key:
        raise SystemExit("HATA: ETSY_API_KEY yok (.env veya ortam degiskeni). Bkz. docs/MARKET_RESEARCH.md")
    return f"{key}:{secret}" if secret and ":" not in key else key


def make_fetch(key: str) -> Fetch:
    last = [0.0]

    def fetch(path: str, params: dict) -> dict:
        url = f"{API}{path}?{urllib.parse.urlencode(params)}" if params else f"{API}{path}"
        for attempt in range(5):
            wait = MIN_INTERVAL - (time.time() - last[0])
            if wait > 0:
                time.sleep(wait)
            last[0] = time.time()
            req = urllib.request.Request(url, headers={"x-api-key": key, "Accept": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    return json.load(r)
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503) and attempt < 4:
                    time.sleep(2 ** attempt)
                    continue
                body = e.read().decode("utf-8", "replace")[:300]
                raise RuntimeError(f"Etsy API {e.code} {path}: {body}") from None
        raise RuntimeError(f"Etsy API tekrar denemeleri tukendi: {path}")
    return fetch


# --------------------------------------------------------------------------- #
# Hesap
# --------------------------------------------------------------------------- #
def price_usd(listing: dict) -> float | None:
    p = listing.get("price") or {}
    try:
        return p["amount"] / p["divisor"]
    except (KeyError, TypeError, ZeroDivisionError):
        return None


def design_count(title: str) -> int:
    nums = []
    for m in DESIGN_RE.finditer(title or ""):
        try:
            nums.append(int(float(m.group(1).replace(",", ""))))
        except ValueError:
            pass
    return max(nums) if nums else 1


def median(xs: list[float]) -> float:
    xs = [x for x in xs if x is not None]
    return float(st.median(xs)) if xs else 0.0


def scout_keyword(fetch: Fetch, kw: str, top: int, reviews: bool, review_rate: float,
                  shop_cache: dict, now: float | None = None) -> dict:
    now = now or time.time()
    rows, count, offset = [], 0, 0
    while len(rows) < top:
        res = fetch("/listings/active", {"keywords": kw, "limit": min(100, top - len(rows)), "offset": offset,
                                         "sort_on": "score"})
        count = int(res.get("count", 0))
        batch = res.get("results", [])
        if not batch:
            break
        rows += batch
        offset += len(batch)
    out = []
    for rank, L in enumerate(rows[:top], 1):
        created = L.get("original_creation_timestamp") or L.get("creation_timestamp") or now
        age_days = max((now - created) / 86400, 1.0)
        n_rev = 0
        if reviews:
            n_rev = int(fetch(f"/listings/{L['listing_id']}/reviews", {"limit": 1}).get("count", 0))
        sid = L.get("shop_id")
        if sid not in shop_cache:
            shop_cache[sid] = fetch(f"/shops/{sid}", {}) if sid else {}
        shop = shop_cache[sid]
        est_sales = n_rev / review_rate if reviews else None
        out.append(dict(
            keyword=kw, rank=rank, listing_id=L.get("listing_id"), title=L.get("title", ""), price=price_usd(L),
            currency=(L.get("price") or {}).get("currency_code", ""),
            designs=design_count(L.get("title", "")), favorites=int(L.get("num_favorers") or 0),
            views=L.get("views"), age_days=round(age_days), reviews=n_rev,
            est_sales=round(est_sales) if est_sales is not None else None,
            est_monthly=round(est_sales / max(age_days / 30.4, 1.0), 1) if est_sales is not None else None,
            shop=shop.get("shop_name", ""), shop_sales=int(shop.get("transaction_sold_count") or 0),
            shop_reviews=int(shop.get("review_count") or 0), url=L.get("url", ""),
        ))
    monthly = [r["est_monthly"] for r in out if r["est_monthly"] is not None]
    usd = [r for r in out if r["currency"] in ("USD", "")]          # fiyat medyani yalniz USD (TRY/INR karismasin)
    demand = sum(monthly) if monthly else sum(r["favorites"] for r in out) / max(len(out), 1)
    summary = dict(
        keyword=kw, results=count, sampled=len(out),
        median_price=round(median([r["price"] for r in usd]), 2),
        median_designs=median([r["designs"] for r in out]),
        median_price_per_design=round(median([r["price"] / r["designs"] for r in usd if r["price"]]), 2),
        pct_with_reviews=round(100 * sum(r["reviews"] > 0 for r in out) / max(len(out), 1)),
        est_monthly_sales_top=round(demand, 1),
        median_shop_sales=median([r["shop_sales"] for r in out]),
        young_winners=sum(1 for r in out if r["age_days"] < 180 and (r["est_monthly"] or 0) >= 5),
        demand_basis="reviews" if monthly else "favorites",
    )
    summary["opportunity"] = round(demand / math.log10(count + 10), 2)
    return dict(summary=summary, listings=out)


# --------------------------------------------------------------------------- #
# Rapor
# --------------------------------------------------------------------------- #
def render_report(results: list[dict], review_rate: float) -> str:
    ranked = sorted(results, key=lambda r: r["summary"]["opportunity"], reverse=True)
    L = ["# SCOUT_REPORT — Etsy niş istihbaratı (resmi API)", "",
         f"Satış = TAHMİN (yorum / %{review_rate * 100:.0f}). Fırsat = ilk N ilanın tahmini aylık satışı ÷ log10(toplam ilan).",
         "", "| # | Anahtar kelime | Toplam ilan | Medyan $ | Medyan tasarım | $/tasarım | Tah. aylık satış (ilk N) | Genç kazanan | Fırsat |",
         "|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(ranked, 1):
        s = r["summary"]
        L.append(f"| {i} | {s['keyword']} | {s['results']:,} | {s['median_price']} | {s['median_designs']:.0f} | "
                 f"{s['median_price_per_design']} | {s['est_monthly_sales_top']} | {s['young_winners']} | {s['opportunity']} |")
    for r in ranked:
        s = r["summary"]
        L += ["", f"## {s['keyword']}", "", "| Sıra | Başlık | $ | Tasarım | Yorum | Tah. aylık | Yaş (gün) | Mağaza (toplam satış) |",
              "|---|---|---|---|---|---|---|---|"]
        top = sorted(r["listings"], key=lambda x: (x["est_monthly"] or 0, x["favorites"]), reverse=True)[:10]
        for x in top:
            L.append(f"| {x['rank']} | {x['title'][:70]} | {x['price']} | {x['designs']} | {x['reviews']} | "
                     f"{x['est_monthly']} | {x['age_days']} | {x['shop']} ({x['shop_sales']:,}) |")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--keywords", nargs="*", default=DEFAULT_KEYWORDS)
    ap.add_argument("--top", type=int, default=48, help="anahtar kelime basina incelenen ilan (ilk sayfalar)")
    ap.add_argument("--no-reviews", action="store_true", help="yorum sayisi cekme (hizli; talep = favori)")
    ap.add_argument("--review-rate", type=float, default=REVIEW_RATE)
    ap.add_argument("--outputs", type=Path, default=BASE_DIR / "outputs")
    args = ap.parse_args()
    load_env(BASE_DIR / ".env")
    fetch = make_fetch(api_key())
    out = args.outputs / SCOUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    results, cache = [], {}
    for kw in args.keywords:
        try:
            r = scout_keyword(fetch, kw, args.top, not args.no_reviews, args.review_rate, cache)
        except Exception as e:  # noqa: BLE001
            print(f"HATA [{kw}]: {e}", file=sys.stderr)
            continue
        results.append(r)
        s = r["summary"]
        print(f"{kw:38s} ilan={s['results']:>7,}  medyan=${s['median_price']:<6} aylik~{s['est_monthly_sales_top']:<7} firsat={s['opportunity']}")
    if not results:
        return 1
    (out / "hot_trends.json").write_text(json.dumps([r["summary"] for r in results], indent=1), encoding="utf-8")
    (out / "SCOUT_REPORT.md").write_text(render_report(results, args.review_rate), encoding="utf-8")
    with (out / "listings.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0]["listings"][0].keys()) if results[0]["listings"] else ["keyword"])
        w.writeheader()
        for r in results:
            w.writerows(r["listings"])
    print(f"-> {out / 'SCOUT_REPORT.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
