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
    def __init__(self, path: Path = MODEL_PATH, threshold=0.25):
        self.threshold = threshold
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
        return decode(self.net.forward(), scale, left, top, image.shape[1], image.shape[0], self.threshold)


def freshness(timestamp, now=None):
    try:
        value = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if value.tzinfo is None:
            return "unverified"
        age = ((now or datetime.now(timezone.utc)) - value).total_seconds()
        return "unverified" if age < -60 else "stale" if age > 600 else "recent"
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
            "density": "unknown" if not selected else "high" if coverage >= 0.28 else "moderate" if coverage >= 0.12 else "low",
            "mean_detection_score": round(float(np.mean([d["score"] for d in selected])), 3) if selected else None,
            "speed_kmh": None, "road_blocked": None, "motion": "not_measured", "detections": selected}


def merge_detections(detections):
    boxes = [[d["box"][0], d["box"][1], d["box"][2] - d["box"][0], d["box"][3] - d["box"][1]] for d in detections]
    indexes = np.asarray(cv2.dnn.NMSBoxes(boxes, [d["score"] for d in detections], 0.0, 0.45)).reshape(-1)
    return [detections[i] for i in indexes]


def tile_windows(width, height, size=512, overlap=0.25):
    step = max(1, round(size * (1 - overlap)))

    def starts(length):
        return sorted(set([*range(0, max(1, length - size + 1), step), max(0, length - size)]))

    return [(x, y, min(size, width - x), min(size, height - y)) for y in starts(height) for x in starts(width)]


def detect_multiscale(detector, image):
    height, width = image.shape[:2]
    detections = detector.detect(image)
    tile_size = max(512, (max(width, height) + 4) // 5)
    for x, y, w, h in tile_windows(width, height, size=tile_size):
        if w == width and h == height:
            continue
        for item in detector.detect(image[y:y + h, x:x + w]):
            a, b, c, d = item["box"]
            if (x > 0 and a <= 2) or (y > 0 and b <= 2) or (x + w < width and c >= w - 2) or (y + h < height and d >= h - 2):
                continue
            detections.append({**item, "box": [a + x, b + y, c + x, d + y]})
    return merge_detections(detections)


def scene_alignment(reference, image):
    result = {"status": "unverified", "matches": 0, "inliers": 0, "max_corner_shift_fraction": None}
    if reference is None or abs(reference.shape[1] / reference.shape[0] - image.shape[1] / image.shape[0]) > 0.02:
        return result
    if reference.shape == image.shape and np.array_equal(reference, image):
        return {**result, "status": "aligned", "method": "identical_reference", "max_corner_shift_fraction": 0.0}
    width, height = 640, round(640 * reference.shape[0] / reference.shape[1])
    a = cv2.cvtColor(cv2.resize(reference, (width, height)), cv2.COLOR_BGR2GRAY)
    b = cv2.cvtColor(cv2.resize(image, (width, height)), cv2.COLOR_BGR2GRAY)
    mask = np.zeros((height, width), np.uint8)
    mask[round(height * 0.16):round(height * 0.85), :] = 255
    orb = cv2.ORB_create(nfeatures=2500, fastThreshold=12)
    ka, da = orb.detectAndCompute(a, mask)
    kb, db = orb.detectAndCompute(b, mask)
    if da is None or db is None or len(da) < 25 or len(db) < 25:
        return result
    pairs = cv2.BFMatcher(cv2.NORM_HAMMING).knnMatch(da, db, k=2)
    good = [pair[0] for pair in pairs if len(pair) == 2 and pair[0].distance < 0.7 * pair[1].distance]
    result["matches"] = len(good)
    if len(good) < 25:
        return result
    source = np.float32([ka[m.queryIdx].pt for m in good])
    target = np.float32([kb[m.trainIdx].pt for m in good])
    transform, inliers = cv2.findHomography(source, target, cv2.RANSAC, 3.0)
    if transform is None or inliers is None or not np.isfinite(transform).all():
        return result
    selected = inliers.ravel().astype(bool)
    result["inliers"] = int(selected.sum())
    if selected.sum() < 20 or selected.mean() < 0.65 or cv2.contourArea(cv2.convexHull(source[selected])) < width * height * 0.04:
        return result
    corners = np.float32([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]]).reshape(1, 4, 2)
    moved = cv2.perspectiveTransform(corners, transform)
    shift = float(np.linalg.norm(moved - corners, axis=2).max() / max(width, height))
    if not np.isfinite(shift):
        return result
    return {**result, "status": "aligned" if shift <= 0.015 else "changed", "method": "orb_homography",
            "max_corner_shift_fraction": round(shift, 5)}


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


def analyze(image, detector, zones, metadata, now=None, references=None):
    started = time.perf_counter()
    now = now or datetime.now(timezone.utc)
    quality = image_quality(image)
    results, annotated = [], image.copy()
    calibration = {"status": "unverified", "reference_id": None}
    colors = [(244, 211, 56), (112, 210, 180)]
    if quality["status"] != "unusable":
        candidates = [(view, scene_alignment(view["image"], image)) for view in references or []]
        aligned = [(view, check) for view, check in candidates if check["status"] == "aligned"]
        if aligned:
            view, check = max(aligned, key=lambda pair: pair[1].get("inliers", 0))
            calibration = {**check, "reference_id": view["id"], "reference_sha256": view.get("sha256")}
            zones = view["zones"]
        elif any(check["status"] == "changed" for _, check in candidates):
            calibration["status"] = "changed"
    detections = detect_multiscale(detector, image) if quality["status"] != "unusable" else []
    box_colors = {}
    for index, zone in enumerate(zones):
        valid = calibration["status"] == "aligned" and quality["status"] != "unusable"
        result = summarize_zone(detections if valid else [], zone, image.shape)
        if not valid:
            result.update(density="unknown", vehicle_count=None, box_coverage_pct=None, mean_detection_score=None)
        results.append(result)
        if valid:
            color = colors[index % len(colors)]
            cv2.polylines(annotated, [polygon_pixels(zone, image.shape)], True, color, 2, cv2.LINE_AA)
            box_colors.update({tuple(item["box"]): color for item in result["detections"]})
    for index, item in enumerate(detections, 1):
        x1, y1, x2, y2 = item["box"]
        color = box_colors.get(tuple(item["box"]), (110, 175, 255))
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        cv2.putText(annotated, str(index), (x1, max(12, y1 - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA)
    mode = metadata.get("mode", "local")
    age_status = freshness(metadata.get("source_updated_at"), now)
    warnings = list(quality["issues"])
    if calibration["status"] != "aligned":
        warnings.append("Encuadre diferente o no verificable: zonas desactivadas; hace falta una referencia calibrada.")
    if not zones:
        warnings.append("Sin zona de carretera configurada: no se clasifica tráfico")
    if age_status != "recent":
        warnings.append("Fecha de actualización del proveedor ausente, inválida o de más de 10 minutos")
    if mode != "live":
        warnings.append("Muestra histórica/local, no describe el tráfico actual")
    warnings.extend(["La fecha HTTP del proveedor no verifica la hora real de captura.",
                     "Una foto no mide velocidad, retenciones ni confirma que la vía esté abierta.",
                     "Cajas naranjas: fuera de zonas validadas; pueden incluir aparcados. No son aforo de la carretera.",
                     "Los conteos son detecciones, no el número real certificado; pueden faltar vehículos pequeños u ocultos."])
    result = {"schema_version": "1.0", "analyzed_at": now.isoformat(), "source": metadata,
              "freshness": age_status, "capture_time_verified": False, "captured_at": None,
              "quality": quality, "calibration": calibration, "zones": results,
              "scene": {"vehicle_count": len(detections) if quality["status"] != "unusable" else None,
                        "detections": detections, "includes_parked_vehicles": True, "density": "unknown"},
              "usable_for_route_review": False, "requires_human_review": True,
              "reason": "Detecciones parciales; encuadre, aforo, antigüedad real y cobertura vial requieren validación.",
              "model": {"name": "YOLOv8s COCO / ONNX · imagen completa + teselas", "sha256": MODEL_SHA256, "license": "AGPL-3.0",
                        "detection_threshold": getattr(detector, "threshold", 0.25), "nms_iou": 0.45, "tile_size": max(512, (max(image.shape[:2]) + 4) // 5), "tile_overlap": 0.25,
                        "density_thresholds": [0.12, 0.28], "score_is_calibrated_probability": False},
              "warnings": warnings, "elapsed_ms": round((time.perf_counter() - started) * 1000)}
    return result, annotated
