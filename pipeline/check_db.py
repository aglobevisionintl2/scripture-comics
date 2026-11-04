"""Spot-check the verse database. Usage: python3 -I check_db.py data/web.sqlite"""
import sqlite3
import sys

db = sqlite3.connect(sys.argv[1])
print(dict(db.execute("SELECT key, value FROM source")))
for book, n, ch in db.execute(
        "SELECT book, COUNT(*), MAX(chapter) FROM verses WHERE book IN ('GEN','EXO') GROUP BY book"):
    print(book, "verses", n, "chapters", ch)
for ref in [("GEN", 1, 1), ("GEN", 1, 2), ("GEN", 2, 23), ("GEN", 49, 3), ("EXO", 15, 1), ("EXO", 40, 38)]:
    row = db.execute("SELECT text FROM verses WHERE book=? AND chapter=? AND verse=?", ref).fetchone()
    print(ref, "->", row[0] if row else "MISSING")
# gaps: verse numbers per chapter must be 1..max with no holes
for book in ("GEN", "EXO"):
    for ch, mx, cnt in db.execute(
            "SELECT chapter, MAX(verse), COUNT(*) FROM verses WHERE book=? GROUP BY chapter", (book,)):
        if mx != cnt:
            print("GAP", book, ch, mx, cnt)
bad = db.execute("SELECT book, chapter, verse, text FROM verses WHERE book IN ('GEN','EXO') "
                 "AND (text='' OR text LIKE '%†%' OR text LIKE '%‡%' OR text LIKE '%<%')").fetchall()
print("suspicious verses:", len(bad), bad[:5])
