"""Build a verse-level SQLite database from the official eBible.org WEB HTML edition.

Usage:
    python3 -I build_verse_db.py <path/to/eng-web_html.zip> <path/to/extracted_dir> <out.sqlite>
"""
import hashlib
import re
import sqlite3
import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString

SKIP_CLASSES = {"tnav", "footnote", "copyright", "chapterlabel", "mt", "mt2", "mt3",
                "notemark", "popup", "verse"}
FILE_RE = re.compile(r"^([0-9A-Z]{3})(\d+)\.htm$")


def skipped(node, main):
    p = node.parent
    while p is not None and p is not main:
        if SKIP_CLASSES.intersection(p.get("class") or []):
            return True
        p = p.parent
    return False


def parse_chapter(path):
    soup = BeautifulSoup(path.read_text(encoding="utf-8-sig"), "html.parser")
    main = soup.find("div", class_="main")
    verses, footnotes = {}, []
    current = None
    for node in main.descendants:
        if getattr(node, "name", None) == "span" and "verse" in (node.get("class") or []):
            current = int(node["id"][1:])
            verses.setdefault(current, [])
        elif getattr(node, "name", None) == "div" and current is not None:
            verses[current].append(" ")  # paragraph / poetry line boundary
        elif isinstance(node, NavigableString) and current is not None and not skipped(node, main):
            verses[current].append(str(node))
    for f in soup.select("p.f"):
        back = f.select_one("a.notebackref")
        if back is None:
            continue
        ref = back.get_text(strip=True)
        back.extract()
        for mark in f.select("span.notemark"):
            mark.extract()
        footnotes.append((ref, f.get_text(" ", strip=True)))
    clean = {v: re.sub(r"\s+", " ", "".join(parts).replace(" ", " ")).strip()
             for v, parts in verses.items()}
    return clean, footnotes


def main(zip_path, src_dir, out_path):
    src = Path(src_dir)
    sha = hashlib.sha256(Path(zip_path).read_bytes()).hexdigest()
    cr = (src / "copyright.htm").read_text(encoding="utf-8-sig")
    dated = re.search(r"dated (\d+ \w+ \d{4})", cr)
    db = sqlite3.connect(out_path)
    db.executescript("""
        DROP TABLE IF EXISTS verses; DROP TABLE IF EXISTS footnotes; DROP TABLE IF EXISTS source;
        CREATE TABLE verses(book TEXT, chapter INT, verse INT, text TEXT, PRIMARY KEY(book, chapter, verse));
        CREATE TABLE footnotes(book TEXT, chapter INT, ref TEXT, text TEXT);
        CREATE TABLE source(key TEXT PRIMARY KEY, value TEXT);
    """)
    books = []
    for f in sorted(src.iterdir()):
        m = FILE_RE.match(f.name)
        if not m:
            continue
        book, ch = m.group(1), int(m.group(2))
        verses, notes = parse_chapter(f)
        if not verses:
            continue
        if book not in books:
            books.append(book)
        db.executemany("INSERT INTO verses VALUES (?,?,?,?)",
                       [(book, ch, v, t) for v, t in verses.items()])
        db.executemany("INSERT INTO footnotes VALUES (?,?,?,?)",
                       [(book, ch, r, t) for r, t in notes])
    meta = {
        "translation": "World English Bible (Classic, eBible.org eng-web)",
        "source_url": "https://ebible.org/eng-web/",
        "archive": Path(zip_path).name,
        "archive_sha256": sha,
        "edition_dated": dated.group(1) if dated else "unknown",
        "license": "Public Domain; 'World English Bible' is a trademark of eBible.org",
    }
    db.executemany("INSERT INTO source VALUES (?,?)", meta.items())
    db.commit()
    total = db.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
    print(f"books={len(books)} verses={total} sha256={sha} edition={meta['edition_dated']}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
