import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from cameras import CAMERAS

ROOT = Path(__file__).resolve().parent
MODEL_SHA256 = "65158dad735be799c2466fa15e260c09558080bd530b42a8d0c3d1b419afd8b5"
MODEL_URL = "https://huggingface.co/inference4j/yolov8n/resolve/66295110f9dd507498735446f4f9f05da3007073/model.onnx"
MODEL_PATH = ROOT / "models/yolov8n.onnx"


def prepare():
    MODEL_PATH.parent.mkdir(exist_ok=True)
    if not MODEL_PATH.exists() or hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest() != MODEL_SHA256:
        print("Descargando YOLOv8n ONNX (12.8 MB), revision fija y SHA-256 verificado...")
        with urllib.request.urlopen(MODEL_URL, timeout=90) as response:
            body = response.read(20_000_001)
        if hashlib.sha256(body).hexdigest() != MODEL_SHA256:
            raise ValueError("El modelo no coincide con el SHA-256 esperado")
        MODEL_PATH.write_bytes(body)
    samples = ROOT / "samples"
    samples.mkdir(exist_ok=True)
    for identifier, camera in CAMERAS.items():
        image = samples / f"cam_{identifier}.jpg"
        evidence = samples / f"cam_{identifier}.http.json"
        if not image.exists() or not evidence.exists():
            request = urllib.request.Request(camera["url"], headers={"User-Agent": "FlareAI-TrafficLab/1.0", "Accept": "image/jpeg"})
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read(4_000_001)
                if not body.startswith(b"\xff\xd8") or len(body) > 4_000_000:
                    raise ValueError("El proveedor no ha devuelto un JPEG valido")
                meta = {"camera_id": identifier, "url": camera["url"], "http_status": response.status,
                        "content_type": response.headers.get("Content-Type"), "last_modified": response.headers.get("Last-Modified"),
                        "descargada_utc": datetime.now(timezone.utc).isoformat(),
                        "sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body)}
            image.write_bytes(body)
            evidence.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        meta = json.loads(evidence.read_text(encoding="utf-8"))
        if hashlib.sha256(image.read_bytes()).hexdigest() != meta["sha256"]:
            raise ValueError(f"La evidencia {identifier} no coincide con su hash")
    print("Modelo y tres muestras listos. Ejecuta: python server.py")


if __name__ == "__main__":
    prepare()
