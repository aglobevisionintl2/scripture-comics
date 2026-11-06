"""Lay out an issue as a KDP print interior PDF (HTML/CSS rendered by Chromium via Playwright).

Usage: python3 pipeline/layout_issue.py scripts/issue01_in_the_beginning.json out_dir [--proof]

Trim 7 x 10 in, bleed 0.125 in on top, bottom and outside edge (page 7.125 x 10.25 in).
Pages alternate recto/verso so the bleed is always on the outside edge. Every lettered line
is re-verified against the WEB database before layout; the job stops on any mismatch.
Writes <out>/issueNN_interior.pdf, page previews, and layout_report.json (effective image DPI).
"""
import html
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
TRIM_W, TRIM_H, BLEED = 7.0, 10.0, 0.125
PAGE_W, PAGE_H = TRIM_W + BLEED, TRIM_H + 2 * BLEED
M_IN, M_OUT, M_TOP, M_BOT = 0.5, 0.45, 0.5, 0.7   # from trim edge; KDP minimum 0.375 (24-150 pages)
GUTTER = 0.14
BOOK = {"GEN": "Genesis", "EXO": "Exodus"}

GRIDS = {  # layout keyword -> (grid-template-rows, grid-template-columns, areas)
    "three tall vertical": ("1fr", "1fr 1fr 1fr", ['"a b c"']),
    "large top panel, two bottom": ("1.35fr 1fr", "1fr 1fr", ['"a a"', '"b c"']),
    "two wide horizontal": ("1fr 1fr", "1fr", ['"a"', '"b"']),
    "four panels, grid": ("1fr 1fr", "1fr 1fr", ['"a b"', '"c d"']),
    "tall left panel, two stacked right": ("1fr 1fr", "1fr 1fr", ['"a b"', '"a c"']),
    "large panel split sea/sky, small bottom": ("2.2fr 1fr", "1fr", ['"a"', '"b"']),
    "wide top panel, large bottom": ("1fr 1.5fr", "1fr", ['"a"', '"b"']),
    "three panels, final panel largest": ("1fr 1fr 1.6fr", "1fr", ['"a"', '"b"', '"c"']),
}


def grid_for(layout):
    for k, v in GRIDS.items():
        if layout.startswith(k):
            return v
    raise SystemExit(f"No grid template for layout: {layout}")


def esc(s):
    return html.escape(s, quote=False)


def verify_text(sc, db):
    for pg in sc["pages"]:
        for pn in pg["panels"]:
            for t in pn["text"]:
                c, v = map(int, t["ref"].split(":"))
                row = db.execute("SELECT text FROM verses WHERE book=? AND chapter=? AND verse=?",
                                 (sc["book"], c, v)).fetchone()
                if not row or t["text"] not in row[0]:
                    raise SystemExit(f"STOP: lettering mismatch p{pg['page']}.{pn['panel']} {t['ref']}")


CSS = f"""
@font-face {{ font-family: 'EBG'; src: url('{(ROOT / 'fonts/EBGaramond-wght.ttf').as_uri()}'); font-weight: 400 800; }}
@font-face {{ font-family: 'Cinzel'; src: url('{(ROOT / 'fonts/Cinzel-wght.ttf').as_uri()}'); font-weight: 400 900; }}
@page {{ size: {PAGE_W}in {PAGE_H}in; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: #fff; }}
.page {{ position: relative; width: {PAGE_W}in; height: {PAGE_H}in; overflow: hidden; page-break-after: always;
        background: #f4ede0; font-family: 'EBG', serif; color: #2b1d12; }}
.live {{ position: absolute; display: grid; gap: {GUTTER}in; }}
.panel {{ position: relative; overflow: hidden; border: 1.4pt solid #1d140c; background: #111; }}
.panel img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
.letters {{ position: absolute; left: 0.09in; top: 0.09in; right: 0.09in; display: flex; flex-direction: column;
           align-items: flex-start; gap: 0.06in; }}
.cap {{ background: #f3e6c8; border: 0.8pt solid #3a2410; padding: 0.045in 0.08in; font-size: 9.6pt; line-height: 1.22;
        max-width: 88%; color: #24170c; }}
.divine {{ font-family: 'Cinzel', serif; font-weight: 600; font-size: 11pt; line-height: 1.28; color: #fff6dc; max-width: 92%;
          letter-spacing: 0.02em; padding: 0.02in 0.04in;
          text-shadow: 0 0 0 #3a2410, 0.6pt 0 0 #3a2410, -0.6pt 0 0 #3a2410, 0 0.6pt 0 #3a2410, 0 -0.6pt 0 #3a2410,
                       0.6pt 0.6pt 0 #3a2410, -0.6pt -0.6pt 0 #3a2410, 0.6pt -0.6pt 0 #3a2410, -0.6pt 0.6pt 0 #3a2410; }}
.tag {{ font-family: 'EBG', serif; font-style: italic; font-size: 7.5pt; color: #6b4a2a; white-space: nowrap; margin-left: 0.04in; }}
.divine .tag {{ color: #fff6dc; font-family: 'EBG'; font-weight: 500; }}
.footer {{ position: absolute; font-size: 8.5pt; color: #4a3220; display: flex; gap: 0.18in; }}
.full {{ position: absolute; inset: 0; }}
.full img {{ width: 100%; height: 100%; object-fit: cover; }}
.center {{ position: absolute; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }}
h1 {{ font-family: 'Cinzel'; font-weight: 700; }}
.moral {{ border: 2pt double #6b4a2a; background: #fbf6ea; padding: 0.4in 0.45in; }}
.moral h2 {{ font-family: 'Cinzel'; font-weight: 700; font-size: 17pt; margin-bottom: 0.18in; text-align: center; }}
.moral p {{ font-size: 12.5pt; line-height: 1.5; text-align: left; }}
.note {{ font-size: 8pt; color: #6b4a2a; font-style: italic; margin-top: 0.25in; text-align: center; }}
.proof {{ position: absolute; font-size: 7pt; color: #b0563a; letter-spacing: 0.08em; }}
"""


class Book:
    def __init__(self, proof):
        self.pages, self.proof = [], proof

    def frame(self):
        """Return (recto, trim_left_x) for the next page."""
        recto = len(self.pages) % 2 == 0  # page 1 is a right-hand page
        return recto, (0.0 if recto else BLEED)

    def live_box(self):
        recto, tx = self.frame()
        left = tx + (M_IN if recto else M_OUT)
        right_margin = (M_OUT if recto else M_IN)
        width = TRIM_W - M_IN - M_OUT
        top = BLEED + M_TOP
        return recto, tx, left, top, width, TRIM_H - M_TOP - M_BOT, right_margin

    def footer(self, text):
        recto, tx, left, top, width, height, _ = self.live_box()
        num = len(self.pages) + 1
        side = f"right:{BLEED + M_OUT}in" if recto else f"left:{BLEED + M_OUT}in"
        parts = [esc(text), str(num)] if recto else [str(num), esc(text)]
        return (f'<div class="footer" style="{side};bottom:{BLEED + 0.38}in">'
                + "".join(f"<span>{p}</span>" for p in parts if p) + "</div>")

    def stamp(self):
        if not self.proof:
            return ""
        recto, tx, left, *_ = self.live_box()
        return f'<div class="proof" style="left:{left}in;top:{BLEED + 0.2}in">PROOF · NOT FOR SALE</div>'

    def add(self, inner, footer_text=""):
        body = inner + (self.footer(footer_text) if footer_text is not None else "") + self.stamp()
        self.pages.append(f'<div class="page">{body}</div>')


def letters(pn, book_code):
    last = {}
    for i, t in enumerate(pn["text"]):
        last[t["ref"]] = i
    out = []
    for i, t in enumerate(pn["text"]):
        tag = (f'<span class="tag">{BOOK[book_code]} {t["ref"]}</span>' if last[t["ref"]] == i else "")
        cls = "divine" if t["type"] == "divine" else "cap"
        out.append(f'<div class="{cls}">{esc(t["text"])}{tag}</div>')
    return '<div class="letters">' + "".join(out) + "</div>"


def main(script_path, out_dir, proof):
    sc = json.load(open(script_path, encoding="utf-8"))
    db = sqlite3.connect(ROOT / "data/web.sqlite")
    verify_text(sc, db)
    tag = f"issue{sc['issue']:02d}"
    art = ROOT / "art" / tag
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    book_name = BOOK[sc["book"]]
    b = Book(proof)

    # 1 Title page (recto)
    recto, tx, left, top, width, height, _ = b.live_box()
    b.add(f'<div class="center" style="left:{left}in;top:{top}in;width:{width}in;height:{height}in">'
          f'<div style="font-family:Cinzel;font-size:14pt;letter-spacing:0.25em">SCRIPTURE COMICS</div>'
          f'<h1 style="font-size:34pt;margin:0.5in 0 0.15in">{esc(sc["title"])}</h1>'
          f'<div style="font-size:14pt">Issue {sc["issue"]}</div>'
          f'<div style="font-size:13pt;margin-top:0.35in;font-style:italic">{esc(sc["opening_reference"])}</div>'
          f'<div style="font-size:10pt;margin-top:2.2in;letter-spacing:0.1em">[IMPRINT] · GLOBE VISION INTERNATIONAL</div></div>', None)
    # 2 Copyright page (verso)
    recto, tx, left, top, width, height, _ = b.live_box()
    src = dict(db.execute("SELECT key, value FROM source"))
    lines = [
        "Scripture Comics, Issue " + str(sc["issue"]) + ": " + sc["title"],
        "Copyright © 2026 [Publisher]. All rights reserved for the artwork, layout and design.",
        "Scripture quotations are taken from the World English Bible (WEB), which is in the public domain.",
        f"Source text: eBible.org, edition dated {src['edition_dated']}. Every quotation is reproduced word for word.",
        "This book presents selected verses. The full passage named on each story's opening page can be read in any Bible.",
        "The page “What This Story Teaches” is a reflection by the publisher and is not part of the Scripture text.",
        "Illustrations were created with the assistance of AI image generation (FLUX.2 [pro]).",
        "Fonts: EB Garamond and Cinzel, SIL Open Font License 1.1.",
    ]
    b.add(f'<div style="position:absolute;left:{left}in;top:{top + height - 3.2}in;width:{width}in;font-size:8.8pt;line-height:1.45">'
          + "".join(f"<p style='margin-bottom:0.08in'>{esc(l)}</p>" for l in lines) + "</div>", None)

    report = []
    # Story pages
    for pg in sc["pages"]:
        recto, tx, left, top, width, height, _ = b.live_box()
        foot = f"{pg['verses']}"
        if pg["layout"].startswith("full-page splash"):
            pn = pg["panels"][0]
            img = art / f"p{pg['page']:02d}_{pn['panel']}.png"
            title = (f'<div style="position:absolute;left:{left}in;top:{top}in;width:{width}in;text-align:center;color:#fff6dc;'
                     f'text-shadow:0 0 6pt #000">'
                     f'<div style="font-family:Cinzel;font-size:11pt;letter-spacing:0.25em">SCRIPTURE COMICS · ISSUE {sc["issue"]}</div>'
                     f'<h1 style="font-size:30pt;margin-top:0.1in">{esc(sc["title"])}</h1>'
                     f'<div style="font-size:12.5pt;font-style:italic;margin-top:0.05in">{esc(sc["opening_reference"])}</div></div>')
            cap = (f'<div style="position:absolute;left:{left}in;bottom:{BLEED + M_BOT + 0.1}in;width:{width}in">'
                   f'<div class="letters" style="position:static">{letters(pn, sc["book"])[21:-6]}</div></div>')
            b.add(f'<div class="full"><img data-panel="p{pg["page"]}.1" src="{img.as_uri()}"></div>{title}{cap}', foot)
            continue
        rows, cols, areas = grid_for(pg["layout"])
        names = "abcd"
        cells = []
        for i, pn in enumerate(pg["panels"]):
            img = art / f"p{pg['page']:02d}_{pn['panel']}.png"
            cells.append(f'<div class="panel" style="grid-area:{names[i]}">'
                         f'<img data-panel="p{pg["page"]}.{pn["panel"]}" src="{img.as_uri()}">{letters(pn, sc["book"])}</div>')
        b.add(f'<div class="live" style="left:{left}in;top:{top}in;width:{width}in;height:{height}in;'
              f'grid-template-rows:{rows};grid-template-columns:{cols};grid-template-areas:{" ".join(areas)}">'
              + "".join(cells) + "</div>", foot)

    # Moral page
    m = sc["moral"]
    recto, tx, left, top, width, height, _ = b.live_box()
    b.add(f'<div class="center" style="left:{left}in;top:{top}in;width:{width}in;height:{height}in">'
          f'<div class="moral"><h2>{esc(m["heading"])}</h2><p>{esc(m["paragraph"])}</p>'
          f'<div class="note">A reflection on {esc(sc["opening_reference"].split(",")[0])}. Quotations are from the World English Bible.</div>'
          f'</div></div>', "")
    # Coloring pages: each on a right-hand page, blank reverse (single-sided)
    for i, cp in enumerate(sc["coloring_pages"], 1):
        if len(b.pages) % 2 == 1:  # next page would be verso: insert blank so coloring lands on recto
            b.add("", None)
        recto, tx, left, top, width, height, _ = b.live_box()
        img = art / "coloring" / f"coloring_{i}.png"
        if img.exists():
            body = (f'<div style="position:absolute;left:{left}in;top:{top}in;width:{width}in;height:{height - 0.3}in;'
                    f'background:#fff;border:1pt solid #2b1d12"><img src="{img.as_uri()}" '
                    f'style="width:100%;height:100%;object-fit:contain"></div>')
        else:
            body = (f'<div class="center" style="left:{left}in;top:{top}in;width:{width}in;height:{height}in;'
                    f'border:1pt dashed #b0563a">Coloring page {i} pending: {esc(cp["subject"])}</div>')
        b.add(f'<div class="page-white" style="position:absolute;inset:0;background:#fff"></div>{body}',
              f"Coloring page · {cp['subject'].split('(')[0].strip()}")
        b.add('<div style="position:absolute;inset:0;background:#fff"></div>', None)  # blank reverse
    # Next issue page
    recto, tx, left, top, width, height, _ = b.live_box()
    b.add(f'<div class="center" style="left:{left}in;top:{top}in;width:{width}in;height:{height}in">'
          f'<div style="font-family:Cinzel;letter-spacing:0.25em;font-size:11pt">NEXT IN SCRIPTURE COMICS</div>'
          f'<h1 style="font-size:26pt;margin:0.2in 0">Issue 2: The Garden</h1>'
          f'<div style="font-style:italic;font-size:13pt">Genesis 2:4–25, selected verses</div></div>', None)
    if len(b.pages) % 2 == 1:
        b.add("", None)

    doc = f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{''.join(b.pages)}</body></html>"
    html_path = out / f"{tag}_interior.html"
    html_path.write_text(doc, encoding="utf-8")
    pdf_path = out / f"{tag}_interior{'_PROOF' if proof else ''}.pdf"
    with sync_playwright() as p:
        br = p.chromium.launch()
        page = br.new_page()
        page.goto(html_path.as_uri())
        page.wait_for_load_state("networkidle")
        page.evaluate("document.fonts.ready")
        dpi = page.evaluate("""() => [...document.querySelectorAll('img[data-panel]')].map(i => {
            const r = i.getBoundingClientRect(); const wIn = r.width/96, hIn = r.height/96;
            const scale = Math.max(wIn/i.naturalWidth, hIn/i.naturalHeight);
            return {panel: i.dataset.panel, box_in: [+wIn.toFixed(2), +hIn.toFixed(2)],
                    px: [i.naturalWidth, i.naturalHeight], effective_dpi: Math.round(1/scale)}; })""")
        page.pdf(path=str(pdf_path), width=f"{PAGE_W}in", height=f"{PAGE_H}in", print_background=True,
                 prefer_css_page_size=True)
        br.close()
    low = [d for d in dpi if d["effective_dpi"] < 300]
    rep = {"pdf": pdf_path.name, "pages": len(b.pages), "page_size_in": [PAGE_W, PAGE_H], "trim_in": [TRIM_W, TRIM_H],
           "panels": dpi, "panels_below_300dpi": len(low)}
    (out / "layout_report.json").write_text(json.dumps(rep, indent=2))
    prev = out / "preview"
    prev.mkdir(exist_ok=True)
    subprocess.run(["pdftoppm", "-r", "60", "-jpeg", str(pdf_path), str(prev / "page")], check=True)
    print(f"pages={len(b.pages)} pdf={pdf_path} panels_below_300dpi={len(low)}/{len(dpi)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], "--proof" in sys.argv)
