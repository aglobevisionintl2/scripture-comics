"""Assemble a Character Bible reference sheet image from whatever views a character has.

Usage: python3 pipeline/build_reference_sheet.py ADAM
"""
import json
import sys
import textwrap
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
INK, BG = (55, 38, 25), (244, 239, 230)


def font(p, s):
    return ImageFont.truetype(p, s)


def main(cid):
    cid = cid.upper()
    d = ROOT / f"designs/locked/{cid}"
    spec = yaml.safe_load((ROOT / f"characters/{cid.lower()}.yaml").read_text())
    qa_path = ROOT / f"qa/{cid}_face_qa.json"
    qa = {v["file"]: v for v in json.loads(qa_path.read_text())["views"]} if qa_path.exists() else {}
    prov = json.loads((d / "provenance.json").read_text()) if (d / "provenance.json").exists() else []
    files = [f"{cid}_face_front.png"] + [p["file"] for p in prov if (d / p["file"]).exists()]
    files = list(dict.fromkeys(files))
    W, H = 2400, 1850
    sheet = Image.new("RGB", (W, H), BG)
    g = ImageDraw.Draw(sheet)
    g.text((50, 30), f"{spec['name'].upper()}: CHARACTER BIBLE REFERENCE  ·  ID {cid}", fill=INK, font=font(FB, 44))
    g.text((50, 90), f"Scripture Comics · first appears {spec['first_appears']} · status: {spec['status']}", fill=INK, font=font(FR, 26))
    cols, tw, th = 5, 440, 470
    for i, f in enumerate(files[:10]):
        x, y = 50 + (i % cols) * (tw + 20), 150 + (i // cols) * (th + 80)
        im = Image.open(d / f).convert("RGB")
        im.thumbnail((tw, th))
        sheet.paste(im, (x + (tw - im.width) // 2, y))
        label = f.replace(f"{cid}_", "").replace(".png", "").replace("_", " ")
        label = "front (locked identity)" if label == "face front" else label
        q = qa.get(f, {})
        sub = (f"face match {q['similarity']:.2f} · {q['result']}" if q.get("similarity") is not None
               else ("no face / not applicable" if q or not spec.get("human", True) else "identity reference"))
        g.text((x, y + th + 6), label, fill=INK, font=font(FB, 20))
        g.text((x, y + th + 32), sub, fill=INK, font=font(FR, 18))
    y0 = 150 + 2 * (th + 80) + 10
    g.text((50, y0), "Palette (locked)", fill=INK, font=font(FB, 24))
    for i, (k, hx) in enumerate(spec.get("palette", {}).items()):
        yy = y0 + 40 + i * 52
        g.rectangle([50, yy, 120, yy + 42], fill=hx, outline=INK)
        g.text((135, yy + 8), f"{k}  {hx}", fill=INK, font=font(FR, 20))
    g.text((560, y0), "Locked traits", fill=INK, font=font(FB, 24))
    yy = y0 + 40
    for k, v in spec.get("locked_traits", {}).items():
        for line in textwrap.wrap(f"{k.replace('_', ' ')}: {v}", 52):
            g.text((560, yy), line, fill=INK, font=font(FR, 19))
            yy += 26
    g.text((1300, y0), "Scripture basis", fill=INK, font=font(FB, 24))
    yy = y0 + 40
    for sb in spec.get("scripture_basis", []):
        for line in textwrap.wrap(f"{sb['ref']}: {sb['note']}", 80):
            g.text((1300, yy), line, fill=INK, font=font(FR, 19))
            yy += 26
        yy += 4
    for extra in ("design_choice", "ambiguity", "views_note", "age_qa_note"):
        if spec.get(extra):
            for line in textwrap.wrap(f"{extra.replace('_', ' ').capitalize()}: {spec[extra]}", 80):
                g.text((1300, yy), line, fill=INK, font=font(FR, 19))
                yy += 26
    g.text((50, H - 40), f"Generated with FLUX.2 [pro] via fal.ai; provenance in designs/locked/{cid}/provenance.json. "
           "Face QA: ArcFace vs locked front face.", fill=INK, font=font(FR, 17))
    out = d / f"{cid}_reference_sheet.jpg"
    sheet.save(out, quality=88)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1])
