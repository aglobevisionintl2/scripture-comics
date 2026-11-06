"""KDP preflight for an interior PDF. Usage: python3 preflight.py file.pdf out.json

Checks: every page is trim + bleed (7.125 x 10.25 in), all fonts embedded, even page count,
24+ pages (KDP paperback minimum; a single issue may fall short and must be bundled),
file size under 650 MB. Exit 1 on any hard failure.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

PAGE = (7.125 * 72, 10.25 * 72)


def run(*a):
    return subprocess.run(a, capture_output=True, text=True, check=True).stdout


def main(pdf, out):
    info = run("pdfinfo", "-l", "9999", pdf)
    sizes = [tuple(map(float, m)) for m in re.findall(r"Page\s+\d+ size:\s+([\d.]+) x ([\d.]+)", info)]
    pages = len(sizes)
    bad_size = [i + 1 for i, s in enumerate(sizes) if abs(s[0] - PAGE[0]) > 0.5 or abs(s[1] - PAGE[1]) > 0.5]
    fonts = run("pdffonts", pdf).splitlines()[2:]
    not_emb = [l for l in fonts if l.split()[-5] != "yes"] if fonts else []
    mb = Path(pdf).stat().st_size / 1e6
    rep = {"pdf": Path(pdf).name, "pages": pages, "page_size_pt": sizes[0] if sizes else None,
           "pages_wrong_size": bad_size, "fonts": [l.split()[0] for l in fonts], "fonts_not_embedded": not_emb,
           "even_page_count": pages % 2 == 0, "meets_24_page_minimum": pages >= 24, "size_mb": round(mb, 1)}
    hard = bad_size or not_emb or pages % 2 or mb > 650
    rep["result"] = "FAIL" if hard else ("PASS" if pages >= 24 else "PASS (bundle needed: under 24 pages)")
    Path(out).write_text(json.dumps(rep, indent=2))
    print(json.dumps(rep, indent=2))
    sys.exit(1 if hard else 0)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
