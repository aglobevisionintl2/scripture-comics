"""Verify an issue script against the WEB source and the approved verse selection.

Usage: python3 -I verify_script.py data/web.sqlite scripts/issue01_in_the_beginning.json
Checks, and exits 1 on any failure:
  1. Every lettered line is an exact piece of the verse it is tagged with.
  2. Every tagged verse is in the approved selection for this issue.
  3. Every approved verse appears in the script (nothing selected is dropped).
  4. Lettered lines from the same verse appear in verse order without overlap.
  5. Every quotation in the Moral paragraph is exact WEB text and appears in the paragraph.
  6. Only locked characters appear in panels.
  7. The Moral paragraph is 80-150 words.
"""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(db_path, script_path):
    db = sqlite3.connect(db_path)
    sc = json.load(open(script_path, encoding="utf-8"))
    sel = json.load(open(ROOT / sc["selection_file"], encoding="utf-8"))
    issue = next(i for i in sel["issues"] if i["issue"] == sc["issue"])
    approved = {(k if isinstance(k, str) else k["ref"]) for k in issue["keep"]}
    verse = lambda b, r: db.execute("SELECT text FROM verses WHERE book=? AND chapter=? AND verse=?",
                                    (b, *map(int, r.split(":")))).fetchone()
    errors, used, lines = [], set(), 0
    cursor = {}
    for pg in sc["pages"]:
        for pn in pg["panels"]:
            for c in pn["characters"]:
                spec = ROOT / f"characters/{c.lower()}.yaml"
                if not spec.exists() or "status: locked" not in spec.read_text():
                    errors.append(f"p{pg['page']}.{pn['panel']}: character {c} is not locked")
            for t in pn["text"]:
                lines += 1
                row = verse(sc["book"], t["ref"])
                where = f"p{pg['page']}.{pn['panel']} {t['ref']}"
                if row is None:
                    errors.append(f"{where}: verse not found")
                    continue
                if t["ref"] not in approved:
                    errors.append(f"{where}: verse not in approved selection")
                pos = row[0].find(t["text"], cursor.get(t["ref"], 0))
                if pos < 0:
                    errors.append(f"{where}: TEXT MISMATCH or out of order: {t['text']}")
                    continue
                cursor[t["ref"]] = pos + len(t["text"])
                used.add(t["ref"])
    for missing in sorted(approved - used):
        errors.append(f"approved verse {missing} is not used in the script")
    tree = sc.get("family_tree", [])
    if tree:
        chap_text = " ".join(t for (t,) in db.execute(
            "SELECT text FROM verses WHERE book=? AND chapter IN (4, 5)", (sc["book"],)))
        for name in [n for x in tree for n in (x if isinstance(x, list) else [x])]:
            if name not in chap_text:
                errors.append(f"family tree name not found in Genesis 4-5: {name}")
    m = sc["moral"]
    words = len(m["paragraph"].split())
    if not 80 <= words <= 150:
        errors.append(f"moral paragraph is {words} words (must be 80-150)")
    for q in m["quotes"]:
        b, r = q["ref"].split()
        row = verse(b, r)
        if row is None or q["text"] not in row[0]:
            errors.append(f"moral quote {q['ref']} does not match WEB: {q['text']}")
        if q["text"] not in m["paragraph"]:
            errors.append(f"moral quote {q['ref']} not found in paragraph text")
    print(f"pages={len(sc['pages'])} lettered_lines={lines} verses_used={len(used)}/{len(approved)} "
          f"moral_words={words} moral_quotes={len(m['quotes'])} errors={len(errors)}")
    for e in errors:
        print("  ERROR", e)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main(*sys.argv[1:3])
