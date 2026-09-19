from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np

from prepare import MODEL_PATH, MODEL_SHA256

VEHICLES = {1: "bicycle", 2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}


def letterbox(image):
    height, width = image.shape[:2]
    scale = min(640 / width, 640 / height)
    resized = cv2.resize(image, (round(width * scale), round(height * scale)))
    left, top = (640 - resized.shape[1]) // 2, (640 - resized.shape[0]) // 2
    result = np.full((640, 640, 3), 114, np.uint8)
    result[top:top + resized.shape[0], left:left + resized.shape[1]] = resized
    return result, scale, left, top


def decode(output, scale, left, top, width, height, threshold=0.3):
    if output.ndim != 3 or output.shape[0] != 1 or output.shape[1] != 84:
        raise ValueError(f"Salida ONNX no compatible: {output.shape}")
    rows = output[0].T
    classes = rows[:, 4:].argmax(axis=1)
    scores = rows[np.arange(len(rows)), classes + 4]
    keep = np.isin(classes, list(VEHICLES)) & (scores >= threshold) & np.isfinite(rows).all(axis=1)
    boxes, confidences, labels = [], [], []
    for row, cls, score in zip(rows[keep], classes[keep], scores[keep]):
        cx, cy, w, h = row[:4]
        x1 = int(np.clip((cx - w / 2 - left) / scale, 0, width - 1))
        y1 = int(np.clip((cy - h / 2 - top) / scale, 0, height - 1))
        x2 = int(np.clip((cx + w / 2 - left) / scale, 0, width))
        y2 = int(np.clip((cy + h / 2 - top) / scale, 0, height))
        if x2 <= x1 or y2 <= y1:
            continue
        boxes.append([x1, y1, x2 - x1, y2 - y1])
        confidences.append(float(score))
        labels.append(VEHICLES[int(cls)])
    indexes = np.asarray(cv2.dnn.NMSBoxes(boxes, confidences, threshold, 0.45)).reshape(-1)
    return [{"box": [boxes[i][0], boxes[i][1], boxes[i][0] + boxes[i][2], boxes[i][1] + boxes[i][3]],
             "label": labels[i], "score": round(confidences[i], 3)} for i in indexes]


class Detector:
    def __init__(self, path: Path = MODEL_PATH):
        if not path.exists():
            raise FileNotFoundError("Falta el modelo. Ejecuta python prepare.py")
        if hashlib.sha256(path.read_bytes()).hexdigest() != MODEL_SHA256:
            raise ValueError("SHA-256 del modelo incorrecto")
        cv2.setNumThreads(4)
        self.net = cv2.dnn.readNetFromONNX(str(path))
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    def detect(self, image):
        padded, scale, left, top = letterbox(image)
        self.net.setInput(cv2.dnn.blobFromImage(padded, 1 / 255, (640, 640), swapRB=True))
        return decode(self.net.forward(), scale, left, top, image.shape[1], image.shape[0])


def freshness(timestamp, now=None):
    try:
        value = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if value.tzinfo is None:
            return "unverified"
        age = ((now or datetime.now(timezone.utc)) - value).total_seconds()
        return "unverified" if age < -60 else "stale" if age > 900 else "recent"
    except (ValueError, AttributeError, TypeError):
        return "unverified"


def polygon_pixels(zone, shape):
    points = np.asarray(zone["polygon"], dtype=float)
    if points.ndim != 2 or points.shape[1] != 2 or len(points) < 3 or not np.isfinite(points).all() or (points < 0).any() or (points > 1).any():
        raise ValueError("La zona requiere al menos tres puntos normalizados entre 0 y 1")
    height, width = shape[:2]
    points = np.rint(points * [width - 1, height - 1]).astype(np.int32)
    if cv2.contourArea(points) < 4:
        raise ValueError("Zona vacía o degenerada")
    return points


def summarize_zone(detections, zone, shape):
    points = polygon_pixels(zone, shape)
    road = np.zeros(shape[:2], np.uint8)
    occupied = np.zeros_like(road)
    cv2.fillPoly(road, [points], 1)
    selected = []
    for item in detections:
        x1, y1, x2, y2 = item["box"]
        if cv2.pointPolygonTest(points, ((x1 + x2) / 2, float(y2 - 1)), False) < 0:
            continue
        selected.append(item)
        occupied[max(0, y1):y2, max(0, x1):x2] = 1
    coverage = float(np.count_nonzero(occupied & road) / np.count_nonzero(road))
    return {"id": zone["id"], "name": zone["name"], "polygon": zone["polygon"],
            "vehicle_count": len(selected), "box_coverage_pct": round(100 * coverage, 2),
            "density": "high" if coverage >= 0.28 else "moderate" if coverage >= 0.12 else "low",
            "mean_detection_score": round(float(np.mean([d["score"] for d in selected])), 3) if selected else None,
            "speed_kmh": None, "road_blocked": None, "motion": "not_measured", "detections": selected}


def merge_detections(detections):
    boxes = [[d["box"][0], d["box"][1], d["box"][2] - d["box"][0], d["box"][3] - d["box"][1]] for d in detections]
    indexes = np.asarray(cv2.dnn.NMSBoxes(boxes, [d["score"] for d in detections], 0.0, 0.45)).reshape(-1)
    return [detections[i] for i in indexes]


def image_quality(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape
    brightness, contrast = float(gray.mean()), float(gray.std())
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    issues = []
    if width < 640 or height < 360:
        issues.append("Resolución insuficiente o posible cartel de sustitución")
    if brightness < 25 or brightness > 235:
        issues.append("Exposición extrema: no se puede valorar la vía")
    if contrast < 12 or sharpness < 20:
        issues.append("Imagen plana o borrosa: posible indisponibilidad")
    return {"status": "unusable" if issues else "basic_checks_passed", "issues": issues,
            "brightness": round(brightness, 1), "contrast": round(contrast, 1),
            "sharpness": round(sharpness, 1), "width": width, "height": height}


def analyze(image, detector, zones, metadata, now=None):
    started = time.perf_counter()
    now = now or datetime.now(timezone.utc)
    quality = image_quality(image)
    results, annotated = [], image.copy()
    colors = [(244, 211, 56), (112, 210, 180)]
    full_frame = detector.detect(image) if zones and quality["status"] != "unusable" else []
    for index, zone in enumerate(zones):
        points = polygon_pixels(zone, image.shape)
        x, y, w, h = cv2.boundingRect(points)
        detections = []
        if quality["status"] != "unusable":
            for item in detector.detect(image[y:y + h, x:x + w]):
                a, b, c, d = item["box"]
                detections.append({**item, "box": [a + x, b + y, c + x, d + y]})
        result = summarize_zone(merge_detections(full_frame + detections), zone, image.shape)
        if quality["status"] == "unusable":
            result.update(density="unknown", vehicle_count=None, box_coverage_pct=None)
        results.append(result)
        color = colors[index % len(colors)]
        cv2.polylines(annotated, [points], True, color, 2, cv2.LINE_AA)
        for item in result["detections"]:
            x1, y1, x2, y2 = item["box"]
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            cv2.putText(annotated, f'{item["label"]} {item["score"]:.2f}', (x1, max(15, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1, cv2.LINE_AA)
    mode = metadata.get("mode", "local")
    age_status = freshness(metadata.get("source_updated_at"), now)
    warnings = list(quality["issues"])
    if not zones:
        warnings.append("Sin zona de carretera configurada: no se clasifica tráfico")
    if age_status != "recent":
        warnings.append("Fecha de actualización ausente, inválida o antigua")
    if mode != "live":
        warnings.append("Muestra histórica/local, no describe el tráfico actual")
    warnings.extend(["Una foto no mide velocidad, retenciones ni confirma que la vía esté abierta.",
                     "ROI manual y umbrales sin calibración estadística; revisar encuadre, oclusiones y detecciones."])
    result = {"schema_version": "1.0", "analyzed_at": now.isoformat(), "source": metadata,
              "freshness": age_status, "quality": quality, "zones": results,
              "usable_for_route_review": False, "requires_human_review": True,
              "reason": "Solo evidencia visual; sin validación de encuadre, aforo, cierres y cobertura del tramo.",
              "model": {"name": "YOLOv8n COCO / ONNX", "sha256": MODEL_SHA256, "license": "AGPL-3.0",
                        "detection_threshold": 0.3, "nms_iou": 0.45, "density_thresholds": [0.12, 0.28],
                        "score_is_calibrated_probability": False},
              "warnings": warnings, "elapsed_ms": round((time.perf_counter() - started) * 1000)}
    return result, annotated
