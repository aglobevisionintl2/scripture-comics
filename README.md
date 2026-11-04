# Scripture Comics

Automated pipeline for Bible comics on Amazon KDP, quoting only the public-domain World English Bible (WEB).

## Layout
- `source/`: official eBible.org WEB archive (edition 30 Oct 2026, SHA-256 in `data/web.sqlite`, source table)
- `pipeline/`: scripts (verse DB, catalog, verse-selection verifier, image generation)
- `data/`: Genesis–Exodus catalog (CSV + XLSX). `web.sqlite` is rebuilt by `build_verse_db.py`.
- `selections/`: per-volume verse selections (JSON) and their verified review files
- `characters/`: Character Bible specs (locked traits, Scripture basis, palette)
- `style/`: house art style
- `designs/`: generated candidates and locked reference sheets
- `.github/workflows/`: jobs that run on GitHub (they need the `FAL_KEY` secret)

## Rebuild the verse database
```
unzip source/eng-web_html.zip -d /tmp/web_html
python3 -I pipeline/build_verse_db.py source/eng-web_html.zip /tmp/web_html data/web.sqlite
```

## Generate character candidates
GitHub → Actions → "Character design candidates" → Run workflow.
