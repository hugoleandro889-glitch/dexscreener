# 📊 IDX Stock Screener

Dashboard riset saham Bursa Efek Indonesia (IDX) — mirip Bloomberg Terminal versi
sederhana. Jalan otomatis lewat GitHub Actions, dashboard-nya statis (GitHub Pages)
jadi bisa kamu buka dari HP atau laptop kapan saja tanpa server nyala terus.

**⚠️ Disclaimer penting:** Ini alat riset, BUKAN penasihat investasi. Semua data
(harga, sentimen berita) murni informasional. Keputusan beli/jual sepenuhnya
tanggung jawab kamu sendiri — selalu riset lebih lanjut sebelum berinvestasi.

## Fitur

- **Ticker tape** di atas: semua saham + perubahan harga, scroll otomatis
- **Filter/screener**: cari berdasarkan nama/ticker, sektor, rentang PER (P/E ratio),
  minimum dividend yield
- **Sort**: klik header kolom apa saja buat urutkan (harga, market cap, volume, dst)
- **Watchlist**: klik bintang ☆ di tiap baris buat nandain saham favorit, tersimpan
  di browser kamu (localStorage), tombol "Watchlist" buat filter cuma yang ditandai
- **Berita & sentimen**: klik baris saham buat expand, lihat berita terbaru + label
  sentimen (positif/netral/negatif) hasil analisis Claude AI berdasarkan judul berita

## Cara kerja

1. **`src/fetch_prices.py`** — ambil harga & data fundamental (PER, dividend yield,
   market cap, dll) via `yfinance` (data publik Yahoo Finance, gratis).
2. **`src/fetch_news.py`** — ambil berita terbaru per saham dari Google News RSS.
3. **`src/sentiment.py`** — kirim judul-judul berita ke Claude API, dapat label
   sentimen per saham (kalau `ANTHROPIC_API_KEY` tidak diset, label jadi "tidak dinilai").
4. **`src/build_data.py`** — gabungkan semua jadi `docs/data/stocks.json`.
5. **`docs/index.html`** — dashboard yang baca file JSON itu dan render tabel
   interaktif. Ini yang jalan di GitHub Pages.
6. **GitHub Actions** (`.github/workflows/update-data.yml`) — jalankan langkah 1-4
   otomatis tiap hari kerja jam 16:30 WIB (habis bursa tutup), commit data baru.

## Setup (sekali saja)

1. **Push ke GitHub**:
   ```bash
   cd idx-stock-screener
   git init
   git add .
   git commit -m "Initial commit: IDX Stock Screener"
   git branch -M main
   git remote add origin https://github.com/USERNAME/idx-stock-screener.git
   git push -u origin main
   ```

2. **Aktifkan GitHub Pages**:
   - Buka repo di GitHub → **Settings → Pages**
   - Source: **Deploy from a branch**
   - Branch: **main**, folder: **/docs**
   - Save. Setelah beberapa menit, dashboard bisa diakses di
     `https://USERNAME.github.io/idx-stock-screener/`

3. **(Sangat disarankan) Tambahkan API key Claude** biar dapat sentimen berita:
   - Repo → **Settings → Secrets and variables → Actions → New repository secret**
   - Name: `ANTHROPIC_API_KEY`
   - Value: API key dari [console.anthropic.com](https://console.anthropic.com)
   - Kalau dilewati, dashboard tetap jalan penuh, cuma kolom sentimen jadi
     "tidak dinilai" semua.

4. **Jalankan pertama kali secara manual**: tab **Actions** di repo → pilih
   workflow **"Update Stock Data"** → **Run workflow**. Tunggu ~2-5 menit
   (tergantung jumlah saham), lalu buka dashboard-nya.

Setelah ini, data ter-update otomatis tiap hari kerja jam 16:30 WIB. Kamu tinggal
buka link dashboard-nya kapan saja.

## Menambah/mengubah saham yang dipantau

Edit `config/tickers.yaml`. Format:
```yaml
tickers:
  - { symbol: "BBCA.JK", name: "Bank Central Asia", sector: "Perbankan" }
```
Ticker IDX di yfinance selalu pakai suffix `.JK`. Daftar awal di file ini berisi
~40 saham blue-chip dari berbagai sektor — **bukan** salinan resmi indeks LQ45
(BEI me-rebalance indeks itu tiap 3 bulan). Cek komposisi resmi terbaru di
[idx.co.id](https://www.idx.co.id/id/data-pasar/data-saham/indeks-saham) kalau
mau menyesuaikan persis.

## Menjalankan di komputer sendiri (buat tes lokal)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."   # opsional
python src/build_data.py
# lalu buka docs/index.html langsung di browser, atau:
cd docs && python -m http.server 8000
# buka http://localhost:8000
```

## Batasan yang perlu kamu tahu

- **yfinance** adalah wrapper tidak resmi ke Yahoo Finance. Beberapa field
  fundamental (terutama untuk saham IDX) kadang kosong karena Yahoo Finance
  tidak selalu punya data lengkap untuk emiten Indonesia. Kode sudah dibuat
  toleran (field kosong ditampilkan sebagai "–", bukan bikin sistem gagal).
- **Sentimen berita** itu analisis nada judul berita oleh AI, BUKAN sinyal
  fundamental atau rekomendasi trading. Anggap sebagai indikator kasar saja.
- Update data cuma sekali sehari (habis bursa tutup) — ini bukan real-time
  streaming kayak Bloomberg Terminal beneran, cocoknya buat riset harian/mingguan,
  bukan day-trading.

## Ide pengembangan lanjutan

- Tambah kolom chart mini (sparkline) pergerakan harga 30 hari
- Notifikasi Telegram kalau saham di watchlist naik/turun lebih dari X%
- Bandingkan valuasi antar saham dalam sektor yang sama (relative valuation)
- Export hasil screening ke CSV/Excel
