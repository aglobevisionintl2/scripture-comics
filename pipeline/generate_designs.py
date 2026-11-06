"""Generate character design candidates with fal.ai (runs in GitHub Actions).

Usage: python pipeline/generate_designs.py ADAM,EVE 4
Needs the FAL_KEY environment variable (a GitHub Actions secret). Writes images and a
rights/provenance log to designs/candidates/<ID>/.
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


def generate(char_id, count, base_seed=1000):
    spec = yaml.safe_load((ROOT / f"characters/{char_id.lower()}.yaml").read_text())
    out = ROOT / "designs/candidates" / char_id
    out.mkdir(parents=True, exist_ok=True)
    prompt = f"{spec['portrait_prompt'].strip()} {STYLE['style_prompt'].strip()}"
    refs = []
    for parent in spec.get("derive_from", []):
        pspec = yaml.safe_load((ROOT / f"characters/{parent.lower()}.yaml").read_text())
        refs.append(fal_client.upload_file(str(ROOT / pspec["selected_face"])))
    log = []
    for i in range(count):
        seed = base_seed + i
        args = {"prompt": prompt, "image_size": "portrait_4_3", "seed": seed,
                "safety_tolerance": STYLE["model"]["safety_tolerance"],
                "output_format": STYLE["model"]["output_format"]}
        model = STYLE["model"]["generate"]
        if refs:
            args["image_urls"] = refs
            model = STYLE["model"]["reference_edit"]
        result = fal_client.subscribe(model, arguments=args)
        url = result["images"][0]["url"]
        fname = f"{char_id}_portrait_seed{seed}.png"
        urllib.request.urlretrieve(url, out / fname)
        log.append({"file": fname, "seed": result.get("seed", seed), "model": model, "derived_from": spec.get("derive_from", []),
                    "prompt": prompt, "generated_utc": dt.datetime.utcnow().isoformat() + "Z",
                    "rights": "fal.ai API output, FLUX.2 [pro]; commercial use permitted per fal.ai terms (verify at release)"})
        print("saved", fname)
    (out / "provenance.json").write_text(json.dumps(log, indent=2))


if __name__ == "__main__":
    if not os.environ.get("FAL_KEY"):
        sys.exit("FAL_KEY is not set. Add it under Settings > Secrets and variables > Actions.")
    ids = [c.strip().upper() for c in sys.argv[1].split(",") if c.strip()]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    for cid in ids:
        generate(cid, n)
