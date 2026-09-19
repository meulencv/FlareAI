import argparse
import base64
import json
import urllib.request
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Exporta una imagen anotada desde Traffic Lab ya arrancado")
    parser.add_argument("--camera", choices=["08301", "06303", "04301"], default="06303")
    parser.add_argument("--mode", choices=["live", "demo"], default="live")
    args = parser.parse_args()
    request = urllib.request.Request("http://127.0.0.1:8790/api/analyze",
                                     data=json.dumps({"camera_id": args.camera, "mode": args.mode}).encode(),
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.load(response)
    destination = Path(__file__).resolve().parent / f"preview-{args.camera}.jpg"
    destination.write_bytes(base64.b64decode(payload["image"].split(",", 1)[1], validate=True))
    evidence = payload["evidence"]
    print(json.dumps({"image": str(destination), "source": evidence["source"],
                      "freshness": evidence["freshness"], "quality": evidence["quality"]["status"],
                      "zones": [{k: zone[k] for k in ("name", "vehicle_count", "density")} for zone in evidence["zones"]]}, ensure_ascii=True))


if __name__ == "__main__":
    main()
