"""Upscale panel and coloring art to print resolution (runs in GitHub Actions).

Usage: python pipeline/upscale_panels.py scripts/issue01_in_the_beginning.json qa/issue01_layout_report.json

For each panel, the needed factor comes from its measured box on the page (layout report):
Real-ESRGAN x2 or x4 on fal.ai, then a small Lanczos top-up if still below TARGET_DPI.
Coloring pages are upscaled and re-thresholded to pure black and white.
Writes art/<issue>/print/*.jpg (not committed; used by the print build in the same job).
"""
import io
import json
import math
import os
import sys
import urllib.request
from pathlib import Path

import fal_client
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TARGET_DPI = 320
COLORING_PX_W = 2000  # about 330 DPI across a 6 in live area


def esrgan(path, scale):
    url = fal_client.upload_file(str(path))
    res = fal_client.subscribe("fal-ai/esrgan", arguments={"image_url": url, "scale": scale, "output_format": "png"})
    return Image.open(io.BytesIO(urllib.request.urlopen(res["images"][0]["url"]).read())).convert("RGB")


def main(script_path, report_path):
    sc = json.load(open(script_path, encoding="utf-8"))
    tag = f"issue{sc['issue']:02d}"
    art = ROOT / "art" / tag
    out = art / "print"
    out.mkdir(exist_ok=True)
    rep = json.load(open(report_path))
    log = []
    for p in rep["panels"]:
        pg, pn = p["panel"][1:].split(".")
        src = art / f"p{int(pg):02d}_{pn}.png"
        need = TARGET_DPI / p["effective_dpi"]
        scale = 2 if need <= 2 else 4
        im = esrgan(src, scale)
        w_in, h_in = p["box_in"]
        min_w = math.ceil(w_in * TARGET_DPI)
        min_h = math.ceil(h_in * TARGET_DPI)
        k = max(min_w / im.width, min_h / im.height, 1.0)
        if k > 1.0:
            im = im.resize((math.ceil(im.width * k), math.ceil(im.height * k)), Image.LANCZOS)
        dest = out / f"p{int(pg):02d}_{pn}.jpg"
        im.save(dest, quality=93, dpi=(TARGET_DPI, TARGET_DPI))
        eff = round(min(im.width / w_in, im.height / h_in)) if k == 1.0 else TARGET_DPI
        log.append({"panel": p["panel"], "esrgan_scale": scale, "lanczos_topup": round(k, 3), "px": im.size,
                    "effective_dpi_after": eff})
        print(p["panel"], "x", scale, "topup", round(k, 3), im.size)
    for c in sorted((art / "coloring").glob("coloring_*.png")):
        im = esrgan(c, 4).convert("L")
        if im.width < COLORING_PX_W:
            im = im.resize((COLORING_PX_W, round(im.height * COLORING_PX_W / im.width)), Image.LANCZOS)
        im.point(lambda v: 255 if v > 140 else 0).convert("1").save(out / f"{c.stem}.png", dpi=(330, 330))
        log.append({"coloring": c.name, "px": im.size})
        print(c.name, im.size)
    (ROOT / "qa" / f"{tag}_upscale_log.json").write_text(json.dumps(log, indent=2))


if __name__ == "__main__":
    if not os.environ.get("FAL_KEY"):
        sys.exit("FAL_KEY is not set.")
    main(sys.argv[1], sys.argv[2])
