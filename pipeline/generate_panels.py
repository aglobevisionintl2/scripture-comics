"""Generate panel art for an issue script, with automated character-consistency QA (GitHub Actions).

Usage: python pipeline/generate_panels.py scripts/issue01_in_the_beginning.json [p9.1,p9.2] [seed_offset]

- Panels without characters: FLUX.2 [pro] text-to-image.
- Panels with characters: FLUX.2 [pro] edit, with each character's locked face as a reference image.
- Every panel with visible faces is checked with ArcFace: each locked character must match one
  detected face at >= THRESHOLD. Failures are regenerated with new seeds (MAX_TRIES).
- Art never contains lettering; text is added in layout. A 5% border is trimmed (signature guard).
Writes art/<issue>/pXX_Y.png, art/<issue>/provenance.json and qa/<issue>_panel_qa.json.
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
NO_TEXT = "No text, no letters, no speech bubbles, no captions, no signature, no frame or border."
STORY_POINT = {
    "eden_before_3_21": {
        "ADAM": "bare shoulders, no clothing visible in frame",
        "EVE": "long hair falling over her shoulders and chest, no clothing of any kind, ignore any clothing shown in the reference image",
    },
}

_app = None


def face_app():
    global _app
    if _app is None:
        from insightface.app import FaceAnalysis
        _app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
        _app.prepare(ctx_id=-1, det_size=(640, 640))
    return _app


def faces(path):
    import cv2
    return [f.normed_embedding for f in face_app().get(cv2.imread(str(path)))]


def fetch_trimmed(url, dest):
    im = Image.open(io.BytesIO(urllib.request.urlopen(url).read())).convert("RGB")
    dx, dy = int(im.width * TRIM), int(im.height * TRIM)
    im.crop((dx, dy, im.width - dx, im.height - dy)).save(dest)


def char_info(cid, cache={}):
    if cid not in cache:
        spec = yaml.safe_load((ROOT / f"characters/{cid.lower()}.yaml").read_text())
        if spec.get("status") != "locked":
            sys.exit(f"{cid} is not locked; refusing to draw an unlocked character.")
        face = ROOT / spec["selected_face"]
        cache[cid] = {"spec": spec, "face": face, "emb": faces(face)[0],
                      "url": fal_client.upload_file(str(face))}
    return cache[cid]


def describe(cid, story_point):
    t = char_info(cid)["spec"]["locked_traits"]
    look = ", ".join(f"{k.replace('_', ' ')}: {v}" for k, v in t.items() if k != "distinguishing_marks")
    costume = STORY_POINT.get(story_point, {}).get(cid, char_info(cid)["spec"]["costumes"].get("after_3_21", ""))
    return f"{char_info(cid)['spec']['name']} ({look}; {costume})"


def check(path, chars):
    found = faces(path)
    result = {}
    for c in chars:
        sims = [float((char_info(c)["emb"] * f).sum()) for f in found]
        result[c] = round(max(sims), 3) if sims else None
    ok = all(v is not None and v >= THRESHOLD for v in result.values())
    return ok, result


def main(script_path, only, offset):
    sc = json.load(open(script_path, encoding="utf-8"))
    tag = f"issue{sc['issue']:02d}"
    out = ROOT / "art" / tag
    out.mkdir(parents=True, exist_ok=True)
    prov_p, qa_p = out / "provenance.json", ROOT / "qa" / f"{tag}_panel_qa.json"
    (ROOT / "qa").mkdir(exist_ok=True)
    prov = json.loads(prov_p.read_text()) if prov_p.exists() else []
    qa = json.loads(qa_p.read_text()) if qa_p.exists() else {}
    for pg in sc["pages"]:
        for pn in pg["panels"]:
            pid = f"p{pg['page']}.{pn['panel']}"
            if only and pid not in only:
                continue
            chars = pn["characters"]
            refs, lead = [], ""
            if chars:
                refs = [char_info(c)["url"] for c in chars]
                lead = " ".join(f"Image {i + 1} shows the exact face and hair of {describe(c, pn.get('story_point'))}; "
                                f"draw this same person with an identical face." for i, c in enumerate(chars))
            prompt = " ".join(x for x in [lead, f"Comic panel, {pn['camera']}.", pn["art"],
                                          STYLE["style_prompt"].strip(), NO_TEXT] if x)
            model = STYLE["model"]["reference_edit"] if refs else STYLE["model"]["generate"]
            tries, attempts, best = (MAX_TRIES if pn.get("face_visible") else 1), [], None
            for t in range(tries):
                seed = 5000 + pg["page"] * 100 + pn["panel"] * 10 + t + offset
                args = {"prompt": prompt, "image_size": pn["size"], "seed": seed,
                        "safety_tolerance": STYLE["model"]["safety_tolerance"],
                        "output_format": STYLE["model"]["output_format"]}
                if refs:
                    args["image_urls"] = refs
                try:
                    res = fal_client.subscribe(model, arguments=args)
                except Exception as e:  # e.g. safety filter; logged, never hidden
                    attempts.append({"seed": seed, "error": str(e)[:300]})
                    print(pid, "try", t + 1, "ERROR", e)
                    continue
                tmp = out / f".try_{pid}_{t}.png"
                fetch_trimmed(res["images"][0]["url"], tmp)
                ok, sims = check(tmp, chars) if pn.get("face_visible") else (True, {})
                attempts.append({"seed": seed, "similarity": sims, "pass": ok})
                score = min([v for v in sims.values() if v is not None], default=-1) if sims else 0
                if best is None or score > best[1]:
                    best = (tmp, score, seed, ok)
                print(pid, "try", t + 1, "seed", seed, sims, "PASS" if ok else "FAIL")
                if ok:
                    break
            fname = f"p{pg['page']:02d}_{pn['panel']}.png"
            if best:
                best[0].replace(out / fname)
            for f in out.glob(f".try_{pid}_*.png"):
                f.unlink()
            status = "PASS" if best and best[3] else ("FAIL" if best else "NO IMAGE")
            if not pn.get("face_visible") and best:
                status = "PASS (no faces to check)"
            qa[pid] = {"file": fname, "characters": chars, "status": status, "attempts": attempts}
            prov = [p for p in prov if p["panel"] != pid]
            prov.append({"panel": pid, "file": fname, "model": model, "prompt": prompt,
                         "references": [str(char_info(c)["face"].relative_to(ROOT)) for c in chars],
                         "seed": best[2] if best else None, "post": f"trimmed {int(TRIM * 100)}% border",
                         "generated_utc": dt.datetime.utcnow().isoformat() + "Z",
                         "rights": "fal.ai API output, FLUX.2 [pro]; commercial use permitted per fal.ai terms (verify at release)"})
            prov_p.write_text(json.dumps(prov, indent=2))
            qa_p.write_text(json.dumps(qa, indent=2))
    total = len(qa)
    passed = sum(v["status"].startswith("PASS") for v in qa.values())
    first_try = sum(1 for v in qa.values() if v["attempts"] and v["attempts"][0].get("pass", "error" not in v["attempts"][0]))
    print(f"SUMMARY panels={total} passed={passed} first_try={first_try}")


if __name__ == "__main__":
    if not os.environ.get("FAL_KEY"):
        sys.exit("FAL_KEY is not set.")
    only = {p for p in (sys.argv[2] if len(sys.argv) > 2 else "").split(",") if p}
    off = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] else 0
    main(sys.argv[1], only, off)
