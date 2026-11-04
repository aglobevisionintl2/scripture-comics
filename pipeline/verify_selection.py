"""Verify a verse selection against the WEB database and write a kept/skipped review.

Usage: python3 -I verify_selection.py data/web.sqlite selections/vol1_genesis_1-5.json out.md
Exit code 1 if any kept text is not an exact piece of its cited verse.
"""
import json
import sqlite3
import sys

BOOK = {"GEN": "Genesis", "EXO": "Exodus"}


def cv(s):
    c, v = s.split(":")
    return int(c), int(v)


def main(db_path, sel_path, out_path):
    db = sqlite3.connect(db_path)
    sel = json.load(open(sel_path, encoding="utf-8"))
    out, failures, grand_full, grand_kept = [f"# {sel['volume']}: Verse Selection Review", ""], 0, 0, 0
    out += ["Every kept line below was checked character for character against the World English Bible source file. "
            "Struck-through verses are skipped. ✂ marks a verse quoted in part.", ""]
    for iss in sel["issues"]:
        b = iss["book"]
        s, e = (cv(x) for x in iss["range"].split("-"))
        verses = db.execute("SELECT chapter, verse, text FROM verses WHERE book=? AND chapter*1000+verse BETWEEN ? AND ? "
                            "ORDER BY chapter, verse", (b, s[0] * 1000 + s[1], e[0] * 1000 + e[1])).fetchall()
        keep = {}
        for k in iss["keep"]:
            ref, text = (k, None) if isinstance(k, str) else (k["ref"], k["text"])
            keep[cv(ref)] = text
        full = sum(len(t.split()) for _, _, t in verses)
        kept_words = 0
        lines = []
        for c, v, t in verses:
            if (c, v) in keep:
                piece = keep[(c, v)] or t
                if piece not in t:
                    failures += 1
                    lines.append(f"- **{c}:{v} MISMATCH:** {piece}")
                    continue
                kept_words += len(piece.split())
                lines.append(f"- **{c}:{v}**{' ✂' if piece != t else ''} {piece}")
            else:
                lines.append(f"- ~~{c}:{v}~~ _skipped_")
        unknown = set(keep) - {(c, v) for c, v, _ in verses}
        for u in unknown:
            failures += 1
            lines.append(f"- **{u[0]}:{u[1]} NOT IN RANGE**")
        grand_full += full
        grand_kept += kept_words
        out += [f"## Issue {iss['issue']}: {iss['title']} ({BOOK[b]} {iss['range'].replace('-', '–')}, selected verses)",
                f"Kept {kept_words} of {full} words ({kept_words * 100 // full}%), "
                f"about {max(6, -(-kept_words // 50))} story pages.", ""] + lines
        if iss.get("scroll_page_names"):
            out += ["", "Family-tree page names: " + " → ".join(iss["scroll_page_names"])]
        out.append("")
    out.insert(2, f"**Volume total:** {grand_kept} of {grand_full} words kept ({grand_kept * 100 // grand_full}%). "
                  f"**Verification mismatches:** {failures}.\n")
    open(out_path, "w", encoding="utf-8").write("\n".join(out))
    print(f"kept={grand_kept}/{grand_full} mismatches={failures}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main(*sys.argv[1:4])
