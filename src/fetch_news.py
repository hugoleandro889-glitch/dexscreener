"""
fetch_news.py
Mengambil berita publik terbaru per saham dari Google News RSS.
Sama seperti project trend radar sebelumnya — sumber publik & legal, bukan scraping.
"""

import feedparser
import urllib.parse
from datetime import datetime, timedelta, timezone


def build_rss_url(query: str, lang: str = "id", country: str = "ID") -> str:
    q = urllib.parse.quote(query)
    return f"https://news.google.com/rss/search?q={q}&hl={lang}&gl={country}&ceid={country}:{lang}"


def fetch_news_for_stock(symbol: str, company_name: str, max_items: int = 5, days_back: int = 7) -> list[dict]:
    """
    Cari berita untuk satu saham berdasarkan nama perusahaan + kode saham,
    supaya hasilnya lebih relevan (nama perusahaan biasanya lebih spesifik daripada kode).
    """
    query = f'"{company_name}" saham'
    url = build_rss_url(query)
    feed = feedparser.parse(url)

    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    results = []

    for entry in feed.entries[:max_items * 2]:
        published_dt = None
        if getattr(entry, "published_parsed", None):
            published_dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

        if published_dt and published_dt < cutoff:
            continue

        source = ""
        if getattr(entry, "source", None):
            source = getattr(entry.source, "title", "")

        results.append({
            "title": entry.get("title", "").strip(),
            "link": entry.get("link", ""),
            "published": published_dt.isoformat() if published_dt else None,
            "source": source,
        })

        if len(results) >= max_items:
            break

    return results


def fetch_news_for_all(tickers: list[dict], max_items: int = 5, days_back: int = 7) -> dict:
    """Return dict: { "<symbol>": [berita...] } untuk semua ticker."""
    output = {}
    for t in tickers:
        try:
            output[t["symbol"]] = fetch_news_for_stock(t["symbol"], t["name"], max_items, days_back)
        except Exception as e:
            print(f"[fetch_news] Gagal ambil berita untuk {t['symbol']}: {e}")
            output[t["symbol"]] = []
    return output


if __name__ == "__main__":
    demo = fetch_news_for_stock("BBCA.JK", "Bank Central Asia")
    for item in demo:
        print(item)
