"""Generate locked reference views from a character's selected face (runs in GitHub Actions).

Usage: python pipeline/generate_reference_views.py ADAM,EVE
Uses FLUX.2 [pro] edit with the selected face as reference image 1. Writes views and
provenance to designs/locked/<ID>/.
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

import fal_client
import yaml

ROOT = Path(__file__).resolve().parent.parent
STYLE = yaml.safe_load((ROOT / "style/style_guide.yaml").read_text())
BG = "plain soft warm-grey studio background, even soft light"
SAME = ("The exact same person as in image 1: identical face, facial structure, skin tone, eyes, "
        "hair color, hair length and hair texture{beard}.")

# (view id, prompt, image_size, face-check required)
VIEWS = [
    ("face_three_quarter", "Head-and-shoulders portrait, three-quarter view turned to the left, {top}.", "portrait_4_3", True),
    ("face_profile", "Head-and-shoulders portrait, exact side profile facing left, {top}.", "portrait_4_3", True),
    ("head_back", "Head-and-shoulders view from directly behind, showing the back of the head and the full length of the hair, {top}.", "portrait_4_3", False),
    ("expression_afraid", "Head-and-shoulders portrait, front view, expression of fear and shame, eyes lowered, {top}.", "portrait_4_3", True),
    ("expression_grief", "Head-and-shoulders portrait, front view, expression of deep grief, {top}.", "portrait_4_3", True),
    ("full_garment_front", "Full-body standing figure, front view, head to bare feet visible, wearing {garment}.", "portrait_16_9", True),
    ("full_garment_back", "Full-body standing figure, back view, head to bare feet visible, wearing {garment}.", "portrait_16_9", False),
]


def upload(path):
    return fal_client.upload_file(str(path))


def run(char_id):
    spec = yaml.safe_load((ROOT / f"characters/{char_id.lower()}.yaml").read_text())
    face = ROOT / spec["selected_face"]
    out = face.parent
    ref_url = upload(face)
    beard = ", and beard" if "beard" in spec["locked_traits"] else ""
    top = "bare shoulders only" if char_id == "ADAM" else "shoulders covered by the long hair"
    garment = spec["costumes"]["after_3_21"]
    log = []
    for i, (vid, tmpl, size, face_check) in enumerate(VIEWS):
        prompt = " ".join([SAME.format(beard=beard), tmpl.format(top=top, garment=garment), BG + ".",
                           STYLE["style_prompt"].strip()])
        seed = 2000 + i
        result = fal_client.subscribe(STYLE["model"]["reference_edit"], arguments={
            "prompt": prompt, "image_urls": [ref_url], "image_size": size, "seed": seed,
            "safety_tolerance": STYLE["model"]["safety_tolerance"],
            "output_format": STYLE["model"]["output_format"],
        })
        fname = f"{char_id}_{vid}.png"
        urllib.request.urlretrieve(result["images"][0]["url"], out / fname)
        log.append({"file": fname, "view": vid, "face_check": face_check, "seed": result.get("seed", seed),
                    "model": STYLE["model"]["reference_edit"], "reference": spec["selected_face"],
                    "prompt": prompt, "generated_utc": dt.datetime.utcnow().isoformat() + "Z",
                    "rights": "fal.ai API output, FLUX.2 [pro]; commercial use permitted per fal.ai terms (verify at release)"})
        print("saved", fname)
    (out / "provenance.json").write_text(json.dumps(log, indent=2))


if __name__ == "__main__":
    if not os.environ.get("FAL_KEY"):
        sys.exit("FAL_KEY is not set.")
    for cid in [c.strip().upper() for c in sys.argv[1].split(",") if c.strip()]:
        run(cid)
