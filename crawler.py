"""
Web crawler sederhana untuk:
  1. https://quotes.toscrape.com  -> output/quotes.csv
  2. https://books.toscrape.com   -> output/books.csv

Crawler mulai dari halaman utama, mengambil data di setiap halaman,
lalu mengikuti tombol "next" sampai halaman terakhir.

Cara pakai:
  python crawler.py                    # crawl kedua situs
  python crawler.py quotes             # hanya quotes.toscrape.com
  python crawler.py books              # hanya books.toscrape.com
  python crawler.py --max-pages 2      # batasi jumlah halaman per situs
  python crawler.py --output hasil     # simpan CSV ke folder "hasil"
"""
import argparse
import csv
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "SimpleCrawler/1.0 (latihan web crawling)"}
RATING = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def fetch(session, url, retries=3):
    """Ambil halaman dan kembalikan objek BeautifulSoup. Coba ulang jika gagal."""
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
            return BeautifulSoup(resp.content, "html.parser")
        except requests.RequestException as e:
            if attempt == retries:
                raise
            print(f"    ! gagal ({e}), mencoba lagi ({attempt}/{retries})...")
            time.sleep(2 * attempt)


def parse_quotes(soup, page_url):
    """Ambil semua kutipan dari satu halaman quotes.toscrape.com."""
    for q in soup.select("div.quote"):
        yield {
            "quote": q.select_one("span.text").get_text(strip=True).strip("“”"),
            "author": q.select_one("small.author").get_text(strip=True),
            "tags": ", ".join(t.get_text(strip=True) for t in q.select("a.tag")),
            "author_url": urljoin(page_url, q.select_one("a[href^='/author/']")["href"]),
        }


def parse_books(soup, page_url):
    """Ambil semua buku dari satu halaman katalog books.toscrape.com."""
    for b in soup.select("article.product_pod"):
        link = b.select_one("h3 a")
        price = b.select_one("p.price_color").get_text(strip=True)
        rating_classes = b.select_one("p.star-rating")["class"]
        yield {
            "title": link["title"],
            "price_gbp": float(re.sub(r"[^\d.]", "", price)),
            "rating": next((RATING[c] for c in rating_classes if c in RATING), None),
            "availability": b.select_one("p.availability").get_text(strip=True),
            "book_url": urljoin(page_url, link["href"]),
            "image_url": urljoin(page_url, b.select_one("img")["src"]),
        }


SITES = {
    "quotes": ("https://quotes.toscrape.com/", parse_quotes, "quotes.csv"),
    "books": ("https://books.toscrape.com/", parse_books, "books.csv"),
}


def crawl(session, start_url, parse_page, max_pages=None, delay=0.5):
    """Crawl dari start_url, ikuti link 'next' sampai habis atau max_pages tercapai."""
    url, page, rows = start_url, 0, []
    while url and (max_pages is None or page < max_pages):
        page += 1
        soup = fetch(session, url)
        found = list(parse_page(soup, url))
        rows.extend(found)
        print(f"  [hal. {page}] {url} -> {len(found)} data")

        next_link = soup.select_one("li.next a")
        url = urljoin(url, next_link["href"]) if next_link else None
        if url:
            time.sleep(delay)  # beri jeda agar tidak membebani server
    return rows


def save_csv(rows, path):
    """Simpan list of dict ke file CSV (UTF-8 dengan BOM agar rapi dibuka di Excel)."""
    if not rows:
        print(f"  Tidak ada data untuk disimpan ke {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Tersimpan: {path} ({len(rows)} baris)")


def main():
    parser = argparse.ArgumentParser(description="Web crawler quotes.toscrape.com & books.toscrape.com")
    parser.add_argument("site", nargs="?", default="all", choices=["all", *SITES],
                        help="situs yang di-crawl (default: all)")
    parser.add_argument("--max-pages", type=int, default=None,
                        help="batas jumlah halaman per situs (default: semua halaman)")
    parser.add_argument("--delay", type=float, default=0.5,
                        help="jeda antar request dalam detik (default: 0.5)")
    parser.add_argument("--output", default="output",
                        help="folder tujuan file CSV (default: output)")
    args = parser.parse_args()

    targets = SITES if args.site == "all" else {args.site: SITES[args.site]}
    with requests.Session() as session:
        session.headers.update(HEADERS)
        for name, (start_url, parse_page, filename) in targets.items():
            print(f"\n=== Crawling {start_url} ===")
            start = time.time()
            rows = crawl(session, start_url, parse_page, args.max_pages, args.delay)
            save_csv(rows, Path(args.output) / filename)
            print(f"  Selesai dalam {time.time() - start:.1f} detik")


if __name__ == "__main__":
    main()
