"""Assemble a Character Bible reference sheet image. Usage: python3 build_reference_sheet.py ADAM"""
import json, sys, textwrap
from pathlib import Path
import yaml
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parent.parent
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def font(p, s): return ImageFont.truetype(p, s)
cid = sys.argv[1].upper(); d = ROOT / f"designs/locked/{cid}"
spec = yaml.safe_load((ROOT / f"characters/{cid.lower()}.yaml").read_text())
qa = {v["file"]: v for v in json.loads((ROOT / f"qa/{cid}_face_qa.json").read_text())["views"]}
W, H = 2400, 1750; BG = (244, 239, 230); INK = (55, 38, 25)
sheet = Image.new("RGB", (W, H), BG); g = ImageDraw.Draw(sheet)
g.text((50, 30), f"{spec['name'].upper()}: CHARACTER BIBLE REFERENCE  ·  ID {cid}", fill=INK, font=font(FB, 44))
g.text((50, 90), f"Scripture Comics · first appears {spec['first_appears']} · status: {spec['status']}", fill=INK, font=font(FR, 26))
def tile(fname, label, x, y, w, h):
    im = Image.open(d / fname).convert("RGB"); im.thumbnail((w, h)); sheet.paste(im, (x + (w - im.width) // 2, y))
    q = qa.get(fname, {}); s = q.get("similarity")
    sub = f"face match {s:.2f} · {q['result']}" if s is not None else ("identity reference" if not q else "no face · exempt")
    g.text((x, y + h + 8), label, fill=INK, font=font(FB, 20)); g.text((x, y + h + 34), sub, fill=INK, font=font(FR, 19))
front = f"{cid}_face_front_garment.png" if (d / f"{cid}_face_front_garment.png").exists() else f"{cid}_face_front.png"
heads = [(front, "Front"), (f"{cid}_face_three_quarter.png", "Three-quarter"),
         (f"{cid}_face_profile.png", "Profile"), (f"{cid}_head_back.png", "Back")]
for i, (f, l) in enumerate(heads): tile(f, l, 50 + i * 330, 150, 310, 413)
exprs = [(f"{cid}_expression_afraid.png", "Afraid / ashamed"), (f"{cid}_expression_grief.png", "Grief")]
for i, (f, l) in enumerate(exprs): tile(f, l, 50 + i * 330, 660, 310, 413)
bodies = [(f"{cid}_full_garment_front.png", "Gen 3:21 garment · front"), (f"{cid}_full_garment_back.png", "Gen 3:21 garment · back")]
for i, (f, l) in enumerate(bodies): tile(f, l, 1390 + i * 500, 150, 470, 836)
# palette
x0, y0 = 720, 660; g.text((x0, y0), "Palette (locked)", fill=INK, font=font(FB, 26))
for i, (k, hx) in enumerate(spec["palette"].items()):
    yy = y0 + 45 + i * 62; g.rectangle([x0, yy, x0 + 80, yy + 50], fill=hx, outline=INK)
    g.text((x0 + 95, yy + 10), f"{k}  {hx}", fill=INK, font=font(FR, 22))
# traits and scripture
y = 1160; g.text((50, y), "Locked traits", fill=INK, font=font(FB, 26)); y += 40
for k, v in spec["locked_traits"].items():
    g.text((50, y), f"{k.replace('_', ' ')}: {v}", fill=INK, font=font(FR, 21)); y += 30
y2 = 1160; g.text((1240, y2), "Scripture basis", fill=INK, font=font(FB, 26)); y2 += 40
for s in spec["scripture_basis"]:
    for line in textwrap.wrap(f"{s['ref']}: {s['note']}", 80):
        g.text((1240, y2), line, fill=INK, font=font(FR, 21)); y2 += 28
    y2 += 6
for line in textwrap.wrap("Costume rule (Eden): " + spec["costumes"]["eden"], 80):
    g.text((1240, y2), line, fill=INK, font=font(FR, 21)); y2 += 28
g.text((50, H - 45), "Face QA: ArcFace cosine similarity vs. locked front face, pass ≥ 0.45. Generated with FLUX.2 [pro] via fal.ai; provenance in designs/locked/" + cid + "/provenance.json", fill=INK, font=font(FR, 18))
out = d / f"{cid}_reference_sheet.jpg"; sheet.save(out, quality=90); print(out)
