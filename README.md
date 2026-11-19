# Web Crawler Sederhana

Program Python untuk melakukan web crawl pada:

1. https://quotes.toscrape.com → `output/quotes.csv`
2. https://books.toscrape.com → `output/books.csv`

Crawler mulai dari halaman utama, mengambil data di setiap halaman, lalu mengikuti tombol "next" sampai halaman terakhir. Hasil crawl disimpan dalam bentuk file CSV.

## Instalasi

```bash
pip install -r requirements.txt
```

## Cara Menjalankan

```bash
python crawler.py                    # crawl kedua situs
python crawler.py quotes             # hanya quotes.toscrape.com
python crawler.py books              # hanya books.toscrape.com
python crawler.py --max-pages 2      # batasi jumlah halaman per situs
python crawler.py --output hasil     # simpan CSV ke folder "hasil"
```

## Hasil

| File | Jumlah data | Kolom |
|---|---|---|
| `output/quotes.csv` | 100 kutipan (10 halaman) | quote, author, tags, author_url |
| `output/books.csv` | 1000 buku (50 halaman) | title, price_gbp, rating, availability, book_url, image_url |
