"""Automated face-consistency QA: compare every face-check view to the locked front face.

Usage: python pipeline/qa_faces.py ADAM,EVE [threshold]
Uses InsightFace (ArcFace embeddings, cosine similarity). Writes qa/<ID>_face_qa.json and
exits 1 if any required view fails, so failures are never hidden.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import yaml
from insightface.app import FaceAnalysis

ROOT = Path(__file__).resolve().parent.parent
app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
app.prepare(ctx_id=-1, det_size=(640, 640))


def embed(path):
    faces = app.get(cv2.imread(str(path)))
    if not faces:
        return None
    f = max(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
    return f.normed_embedding


def main(ids, threshold):
    failed = 0
    (ROOT / "qa").mkdir(exist_ok=True)
    for cid in ids:
        spec = yaml.safe_load((ROOT / f"characters/{cid.lower()}.yaml").read_text())
        if not spec.get("human", True):
            print(cid, "non-human: face QA not applicable")
            continue
        ref = embed(ROOT / spec["selected_face"])
        prov = json.loads((ROOT / f"designs/locked/{cid}/provenance.json").read_text())
        rows = []
        for p in prov:
            if p.get("result") == "NO IMAGE":
                rows.append({"file": p["file"], "result": "FAIL (no image: content filter or error)"})
                failed += 1
                continue
            if not p["face_check"]:
                rows.append({"file": p["file"], "result": "exempt (no face visible)"})
                continue
            e = embed(ROOT / f"designs/locked/{cid}/{p['file']}")
            if e is None:
                rows.append({"file": p["file"], "similarity": None, "result": "FAIL (no face detected)"})
                failed += 1
                continue
            sim = float(np.dot(ref, e))
            ok = sim >= p.get("threshold", threshold)
            failed += 0 if ok else 1
            rows.append({"file": p["file"], "similarity": round(sim, 3), "result": "PASS" if ok else "FAIL"})
        checked = [r for r in rows if "similarity" in r]
        report = {"character": cid, "threshold": threshold, "views": rows,
                  "pass_rate": f"{sum(r['result'] == 'PASS' for r in checked)}/{len(checked)}"}
        (ROOT / f"qa/{cid}_face_qa.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    ids = [c.strip().upper() for c in sys.argv[1].split(",") if c.strip()]
    main(ids, float(sys.argv[2]) if len(sys.argv) > 2 else 0.45)
