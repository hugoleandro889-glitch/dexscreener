"""
sentiment.py
Menilai sentimen berita per saham (positif/netral/negatif) pakai Claude API,
berdasarkan judul-judul berita yang sudah diambil fetch_news.py.

Kalau ANTHROPIC_API_KEY tidak diset, semua saham diberi sentimen "tidak dinilai"
(fallback), supaya sistem tetap jalan tanpa AI.

PENTING: Ini BUKAN rekomendasi beli/jual. Ini cuma indikator nada pemberitaan
(apakah judul berita cenderung positif/negatif/netral), murni untuk riset pribadi.
"""

import os
import json


def _fallback_sentiment(news_by_symbol: dict) -> dict:
    return {symbol: {"label": "tidak dinilai", "reason": "ANTHROPIC_API_KEY tidak diset"}
            for symbol in news_by_symbol}


def score_sentiment(news_by_symbol: dict) -> dict:
    """
    Return dict: { "<symbol>": {"label": "positif|netral|negatif|tidak dinilai", "reason": str} }
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return _fallback_sentiment(news_by_symbol)

    import anthropic
    client = anthropic.Anthropic()

    # Cuma kirim saham yang punya berita, biar hemat token
    payload = {sym: [n["title"] for n in items] for sym, items in news_by_symbol.items() if items}

    if not payload:
        return _fallback_sentiment(news_by_symbol)

    system_prompt = (
        "Kamu menilai NADA PEMBERITAAN (bukan memberi rekomendasi investasi) untuk tiap saham "
        "berdasarkan daftar judul berita yang diberikan. Untuk tiap kode saham, tentukan label "
        "'positif', 'netral', atau 'negatif' berdasarkan apakah judul-judul beritanya secara umum "
        "membawa kabar baik, netral, atau buruk buat perusahaan tersebut. Sertakan alasan singkat "
        "(maks 15 kata) dalam Bahasa Indonesia.\n\n"
        "PENTING: Jawab HANYA dalam format JSON valid, tanpa teks lain, tanpa markdown code fence. "
        "Format: {\"KODE_SAHAM\": {\"label\": \"positif|netral|negatif\", \"reason\": \"...\"}, ...}"
    )

    try:
        message = client.messages.create(
            model=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5"),
            max_tokens=2000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}
            ],
        )
        text = "".join(block.text for block in message.content if block.type == "text")
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(text)
    except Exception as e:
        print(f"[sentiment] Gagal menilai sentimen via AI, fallback: {e}")
        return _fallback_sentiment(news_by_symbol)

    # Lengkapi saham yang tidak ada beritanya dengan label "tidak dinilai"
    final = {}
    for symbol in news_by_symbol:
        final[symbol] = parsed.get(symbol, {"label": "tidak dinilai", "reason": "tidak ada berita relevan"})
    return final


if __name__ == "__main__":
    demo_news = {
        "BBCA.JK": [{"title": "Laba BCA naik 15% di kuartal II 2026"}],
        "GOTO.JK": [{"title": "GoTo catat kerugian membengkak, saham anjlok"}],
    }
    print(score_sentiment(demo_news))
