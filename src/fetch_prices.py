"""
fetch_prices.py
Mengambil data harga & fundamental saham IDX menggunakan yfinance (data publik Yahoo Finance).

CATATAN:
- yfinance kadang tidak punya semua field fundamental untuk saham IDX (lebih lengkap
  untuk saham AS). Field yang kosong akan diisi None dan ditangani di frontend.
- Kode ini sengaja per-ticker try/except supaya satu ticker gagal tidak menggagalkan semua.
"""

import time
import yfinance as yf


def _safe_get(info: dict, key: str, default=None):
    val = info.get(key, default)
    return val if val not in ("", "None") else default


def fetch_stock_data(symbol: str, name: str, sector: str) -> dict:
    """Ambil satu saham: harga terkini, perubahan harian, dan metrik fundamental utama."""
    result = {
        "symbol": symbol,
        "name": name,
        "sector": sector,
        "price": None,
        "change_pct": None,
        "volume": None,
        "market_cap": None,
        "pe_ratio": None,
        "dividend_yield": None,
        "eps": None,
        "week52_high": None,
        "week52_low": None,
        "error": None,
    }

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}

        price = _safe_get(info, "currentPrice") or _safe_get(info, "regularMarketPrice")
        prev_close = _safe_get(info, "previousClose")

        result["price"] = price
        if price is not None and prev_close:
            result["change_pct"] = round((price - prev_close) / prev_close * 100, 2)

        result["volume"] = _safe_get(info, "volume") or _safe_get(info, "regularMarketVolume")
        result["market_cap"] = _safe_get(info, "marketCap")
        result["pe_ratio"] = _safe_get(info, "trailingPE")
        dy = _safe_get(info, "dividendYield")
        result["dividend_yield"] = round(dy * 100, 2) if dy else None
        result["eps"] = _safe_get(info, "trailingEps")
        result["week52_high"] = _safe_get(info, "fiftyTwoWeekHigh")
        result["week52_low"] = _safe_get(info, "fiftyTwoWeekLow")

    except Exception as e:
        result["error"] = str(e)
        print(f"[fetch_prices] Gagal ambil data untuk {symbol}: {e}")

    return result


def fetch_all_stocks(tickers: list[dict], delay_sec: float = 0.5) -> list[dict]:
    """Ambil data untuk seluruh daftar ticker, dengan jeda kecil antar request."""
    results = []
    for t in tickers:
        data = fetch_stock_data(t["symbol"], t["name"], t["sector"])
        results.append(data)
        time.sleep(delay_sec)
    return results


if __name__ == "__main__":
    # Uji cepat manual (jalankan: python src/fetch_prices.py)
    demo = fetch_all_stocks([
        {"symbol": "BBCA.JK", "name": "Bank Central Asia", "sector": "Perbankan"},
    ])
    for d in demo:
        print(d)
