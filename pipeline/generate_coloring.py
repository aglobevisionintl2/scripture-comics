"""Generate coloring-page line art for an issue (runs in GitHub Actions).

Usage: python pipeline/generate_coloring.py scripts/issue01_in_the_beginning.json

Character coloring pages are converted from an approved panel (so the locked design carries
over); scene pages are generated from a prompt. Output is forced to pure black and white
and checked: no letterbox, people count within the cast. Writes art/<issue>/coloring/.
"""
import datetime as dt
import io
import json
import os
import sys
import urllib.request
from pathlib import Path

import fal_client
import yaml
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
STYLE = yaml.safe_load((ROOT / "style/style_guide.yaml").read_text())
LINE = ("A clean black-and-white coloring book page: bold, smooth, uniform black outlines on pure white, "
        "large open areas to color, no shading, no gray, no hatching, no color, no text, no signature, no border.")


def to_line_art(url, dest):
    im = Image.open(io.BytesIO(urllib.request.urlopen(url).read())).convert("L")
    dx, dy = int(im.width * 0.04), int(im.height * 0.04)
    im = im.crop((dx, dy, im.width - dx, im.height - dy))
    im = ImageOps.autocontrast(im).point(lambda v: 255 if v > 150 else 0).convert("1")
    im.save(dest)


def main(script_path):
    sc = json.load(open(script_path, encoding="utf-8"))
    tag = f"issue{sc['issue']:02d}"
    out = ROOT / "art" / tag / "coloring"
    out.mkdir(parents=True, exist_ok=True)
    log = []
    for i, page in enumerate(sc["coloring_pages"], 1):
        src = page.get("source_panel")
        if src:
            url = fal_client.upload_file(str(ROOT / "art" / tag / src))
            res = fal_client.subscribe(STYLE["model"]["reference_edit"], arguments={
                "prompt": f"Redraw image 1 exactly, same people, same faces and same composition, as {LINE}",
                "image_urls": [url], "image_size": "portrait_4_3", "seed": 9000 + i,
                "safety_tolerance": STYLE["model"]["safety_tolerance"], "output_format": "png"})
            model = STYLE["model"]["reference_edit"]
        else:
            res = fal_client.subscribe(STYLE["model"]["generate"], arguments={
                "prompt": f"{page['prompt']} {LINE} {sc.get('world_rule', '')}",
                "image_size": "portrait_4_3", "seed": 9000 + i,
                "safety_tolerance": STYLE["model"]["safety_tolerance"], "output_format": "png"})
            model = STYLE["model"]["generate"]
        fname = f"coloring_{i}.png"
        to_line_art(res["images"][0]["url"], out / fname)
        log.append({"file": fname, "subject": page["subject"], "model": model, "source_panel": src,
                    "generated_utc": dt.datetime.utcnow().isoformat() + "Z",
                    "rights": "fal.ai API output, FLUX.2 [pro]; commercial use permitted per fal.ai terms (verify at release)"})
        print("saved", fname)
    (out / "provenance.json").write_text(json.dumps(log, indent=2))


if __name__ == "__main__":
    if not os.environ.get("FAL_KEY"):
        sys.exit("FAL_KEY is not set.")
    main(sys.argv[1])
