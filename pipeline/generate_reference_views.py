"""Generate locked reference views with automatic face-QA retries (runs in GitHub Actions).

Usage: python pipeline/generate_reference_views.py ADAM,EVE [view1,view2] [seed_offset]

Each view is made with FLUX.2 [pro] edit from two references: image 1 = the locked face,
image 2 = the approved costume image (when one exists). Views that must show the face are
checked with ArcFace against the locked face and regenerated with new seeds until they
pass (up to MAX_TRIES). Every attempt is logged in provenance.json. A 5% border is trimmed
from every image to remove painter-style signatures the model tends to put in corners.
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
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
STYLE = yaml.safe_load((ROOT / "style/style_guide.yaml").read_text())
MAX_TRIES = 4
THRESHOLD = 0.45
TRIM = 0.05
BG = "plain soft warm-grey studio background, even soft light"

# (view id, prompt, image_size, face check, costume reference view or None)
VIEWS = [
    ("face_front_garment", "Head-and-shoulders portrait, front view, looking at viewer, {top}.", "portrait_4_3", True, None),
    ("face_three_quarter", "Head-and-shoulders portrait, three-quarter view turned to the left, {top}.", "portrait_4_3", True, "HEAD"),
    ("face_profile", "Head-and-shoulders portrait, exact side profile facing left, {top}.", "portrait_4_3", True, "HEAD"),
    ("head_back", "Head-and-shoulders view from directly behind, showing the back of the head and the full length of the hair, {top}.", "portrait_4_3", False, "HEAD"),
    ("expression_afraid", "Head-and-shoulders portrait, front view, expression of fear and shame, eyes lowered, {top}.", "portrait_4_3", True, "HEAD"),
    ("expression_grief", "Head-and-shoulders portrait, front view, expression of deep grief, {top}.", "portrait_4_3", True, "HEAD"),
    ("full_garment_front", "Full-body standing figure, front view, head to bare feet visible, wearing {garment}.", "portrait_16_9", True, None),
    ("full_garment_back", "Full-body standing figure, back view, head to bare feet visible, wearing exactly the same garment as image 2, seen from behind.", "portrait_16_9", False, "full_garment_front"),
]

_face_app = None


def face_app():
    global _face_app
    if _face_app is None:
        from insightface.app import FaceAnalysis
        _face_app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
        _face_app.prepare(ctx_id=-1, det_size=(640, 640))
    return _face_app


def embed(path):
    import cv2
    faces = face_app().get(cv2.imread(str(path)))
    if not faces:
        return None
    return max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])).normed_embedding


def similarity(ref_emb, path):
    e = embed(path)
    return None if e is None else float((ref_emb * e).sum())


def fetch_trimmed(url, dest):
    data = urllib.request.urlopen(url).read()
    im = Image.open(io.BytesIO(data)).convert("RGB")
    dx, dy = int(im.width * TRIM), int(im.height * TRIM)
    im.crop((dx, dy, im.width - dx, im.height - dy)).save(dest)


def run(char_id, only, seed_offset):
    spec = yaml.safe_load((ROOT / f"characters/{char_id.lower()}.yaml").read_text())
    face = ROOT / spec["selected_face"]
    out = face.parent
    human = spec.get("human", True)
    ref_emb = embed(face) if human else None
    face_url = fal_client.upload_file(str(face))
    beard = ", and beard" if "beard" in spec["locked_traits"] else ""
    hair = spec["locked_traits"].get("hair", "")
    garment = spec["costumes"].get("after_3_21") or spec["costumes"].get("default", "")
    top = spec.get("head_costume") or ("bare shoulders only" if spec["id"] == "ADAM" else f"wearing: {garment}")
    head_ref = "face_front_garment" if "head_costume" in spec else None
    prov_path = out / "provenance.json"
    log = json.loads(prov_path.read_text()) if prov_path.exists() else []
    views = [v for v in VIEWS if "views" not in spec or v[0] in spec["views"]]
    views = [(*v, None) for v in views]
    for ev in spec.get("extra_views", []):
        views.append((ev["id"], ev["prompt"], ev["size"], ev["face_check"] and human, None, ev.get("threshold")))
    for i, (vid, tmpl, size, face_check, costume, thr) in enumerate(views):
        thr = thr or THRESHOLD
        if only and vid not in only:
            continue
        if vid == "face_front_garment" and "head_costume" not in spec:
            continue
        costume = head_ref if costume == "HEAD" else costume
        urls = [face_url]
        same = (f"The exact same person as in image 1: identical face, facial structure, skin tone, eyes{beard}. "
                f"Hair exactly as image 1: {hair}.")
        if costume and (out / f"{char_id}_{costume}.png").exists():
            urls.append(fal_client.upload_file(str(out / f"{char_id}_{costume}.png")))
            same += " Clothing exactly as in image 2."
        if not human or vid in {e["id"] for e in spec.get("extra_views", [])}:
            same = ""
        body = tmpl if thr != THRESHOLD or vid in {e["id"] for e in spec.get("extra_views", [])} else tmpl.format(top=top, garment=garment)
        prompt = " ".join(x for x in [same, body, BG + ".", STYLE["style_prompt"].strip()] if x)
        fname = f"{char_id}_{vid}.png"
        attempts, best = [], None
        for t in range(MAX_TRIES if face_check else 1):
            seed = 2000 + i * 10 + t + seed_offset
            result = fal_client.subscribe(STYLE["model"]["reference_edit"], arguments={
                "prompt": prompt, "image_urls": urls, "image_size": size, "seed": seed,
                "safety_tolerance": STYLE["model"]["safety_tolerance"],
                "output_format": STYLE["model"]["output_format"],
            })
            tmp = out / f".try_{vid}_{t}.png"
            fetch_trimmed(result["images"][0]["url"], tmp)
            sim = similarity(ref_emb, tmp) if face_check else None
            attempts.append({"seed": seed, "similarity": None if sim is None else round(sim, 3)})
            if best is None or (sim if sim is not None else -1) > (best[1] if best[1] is not None else -1):
                best = (tmp, sim, seed)
            print(f"{fname} try {t + 1}: seed {seed} similarity {sim}")
            if not face_check or (sim is not None and sim >= thr):
                break
        best[0].replace(out / fname)
        for f in out.glob(f".try_{vid}_*.png"):
            f.unlink()
        log = [e for e in log if e["file"] != fname]
        log.append({"file": fname, "view": vid, "face_check": face_check, "threshold": thr, "seed": best[2],
                    "attempts": attempts, "model": STYLE["model"]["reference_edit"],
                    "references": [spec["selected_face"]] + ([f"{char_id}_{costume}.png"] if len(urls) > 1 else []),
                    "prompt": prompt, "post": f"trimmed {int(TRIM * 100)}% border",
                    "generated_utc": dt.datetime.utcnow().isoformat() + "Z",
                    "rights": "fal.ai API output, FLUX.2 [pro]; commercial use permitted per fal.ai terms (verify at release)"})
        prov_path.write_text(json.dumps(log, indent=2))


if __name__ == "__main__":
    if not os.environ.get("FAL_KEY"):
        sys.exit("FAL_KEY is not set.")
    ids = [c.strip().upper() for c in sys.argv[1].split(",") if c.strip()]
    only = {v for v in (sys.argv[2] if len(sys.argv) > 2 else "").split(",") if v}
    offset = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] else 0
    for cid in ids:
        run(cid, only, offset)
