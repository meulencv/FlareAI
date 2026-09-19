import argparse
import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import cv2

from cameras import CAMERAS
from server import Lab, SameHostRedirect, decode_image
from traffic import analyze

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="Regresión visual reproducible sobre un fotograma congelado")
    parser.add_argument("--capture", action="store_true")
    parser.add_argument("--stage", choices=["before", "after", "candidate"], required=True)
    parser.add_argument("--threshold", type=float)
    args = parser.parse_args()
    if args.threshold is not None and not 0.05 <= args.threshold <= 0.9:
        parser.error("El umbral de diagnóstico debe estar entre 0.05 y 0.9")
    image_path = ROOT / "samples/m30-front.jpg"
    meta_path = ROOT / "samples/m30-front.http.json"
    camera = CAMERAS["08301"]
    if args.capture and not image_path.exists():
        request = urllib.request.Request(camera["url"], headers={"User-Agent": "FlareAI-TrafficLab/1.0", "Accept": "image/jpeg"})
        with urllib.request.build_opener(SameHostRedirect()).open(request, timeout=20) as response:
            body = response.read(4_000_001)
            decode_image(body)
            meta = {"url": camera["url"], "last_modified": response.headers.get("Last-Modified"),
                    "downloaded_at": datetime.now(timezone.utc).isoformat(), "sha256": hashlib.sha256(body).hexdigest()}
        image_path.write_bytes(body)
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    body = image_path.read_bytes()
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if hashlib.sha256(body).hexdigest() != meta["sha256"]:
        raise ValueError("La imagen de regresión no coincide con su hash")
    image = decode_image(body)
    lab = Lab()
    if args.threshold is not None:
        lab.detector.threshold = args.threshold
    baseline = lab.detector.detect(image)
    kwargs = {"references": lab.reference_views("08301")} if hasattr(lab, "reference_views") else {}
    result, annotated = analyze(image, lab.detector, camera["zones"], {
        "camera_id": "08301", "mode": "regression", "sha256": meta["sha256"],
        "downloaded_at": meta["downloaded_at"], "source_updated_at": None}, **kwargs)
    result["single_pass_scene_count"] = len(baseline)
    (ROOT / f"vision-{args.stage}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    cv2.imwrite(str(ROOT / f"vision-{args.stage}.jpg"), annotated)
    print(json.dumps({"stage": args.stage, "source": meta, "single_pass_scene_count": len(baseline),
                      "calibration": result.get("calibration"), "scene_count": result.get("scene", {}).get("vehicle_count"),
                      "zones": [{k: z[k] for k in ("id", "vehicle_count", "density")} for z in result["zones"]]}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
