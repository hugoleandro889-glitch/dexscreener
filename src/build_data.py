"""
build_data.py
Entry point utama. Menjalankan:
1. fetch_prices  -> harga & fundamental tiap saham
2. fetch_news    -> berita terbaru tiap saham
3. sentiment     -> nilai nada pemberitaan tiap saham
4. Gabungkan semua jadi docs/data/stocks.json, dibaca langsung oleh dashboard (docs/index.html)

Jalankan: python src/build_data.py
"""

import os
import sys
import json
import yaml
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))

from fetch_prices import fetch_all_stocks
from fetch_news import fetch_news_for_all
from sentiment import score_sentiment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "config", "tickers.yaml")
OUTPUT_PATH = os.path.join(ROOT, "docs", "data", "stocks.json")


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    print("=== IDX Stock Screener: build_data ===")
    config = load_config()
    tickers = config.get("tickers", [])

    print(f"[1/4] Mengambil harga & fundamental untuk {len(tickers)} saham...")
    price_data = fetch_all_stocks(tickers)
    ok_count = sum(1 for d in price_data if d.get("price") is not None)
    print(f"      -> {ok_count}/{len(tickers)} berhasil ambil harga")

    print("[2/4] Mengambil berita per saham...")
    news_data = fetch_news_for_all(tickers)
    total_news = sum(len(v) for v in news_data.values())
    print(f"      -> {total_news} berita ditemukan total")

    print("[3/4] Menilai sentimen berita...")
    sentiment_data = score_sentiment(news_data)

    print("[4/4] Menggabungkan & menyimpan data...")
    combined = []
    for stock in price_data:
        sym = stock["symbol"]
        combined.append({
            **stock,
            "news": news_data.get(sym, []),
            "sentiment": sentiment_data.get(sym, {"label": "tidak dinilai", "reason": ""}),
        })

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_at_wib": datetime.now(timezone.utc).astimezone(
            __import__("datetime").timezone(__import__("datetime").timedelta(hours=7))
        ).strftime("%Y-%m-%d %H:%M WIB"),
        "stocks": combined,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Selesai. Data tersimpan di: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
