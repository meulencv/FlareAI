import json
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import numpy as np

from cloud_steps import FINALIZE, VALIDATE
from traffic import analyze, decode, freshness, letterbox, summarize_zone

NOW = datetime(2026, 9, 19, 10, tzinfo=timezone.utc)
ZONE = {"id": "north", "name": "Calzada", "polygon": [[0, 0], [1, 0], [1, 1], [0, 1]]}


def sandbox(code, inputs):
    scope = {"input_data": inputs}
    exec(code, scope)
    return scope["output"]


class TrafficTests(unittest.TestCase):
    def test_letterbox_preserves_aspect(self):
        result, scale, left, top = letterbox(np.zeros((360, 1280, 3), np.uint8))
        self.assertEqual(result.shape, (640, 640, 3))
        self.assertEqual((scale, left, top), (0.5, 0, 230))

    def test_decode_filters_people_and_duplicate_vehicles(self):
        output = np.zeros((1, 84, 3), np.float32)
        output[0, :4, :] = np.array([[100, 101, 300], [100, 101, 300], [40, 40, 40], [40, 40, 40]])
        output[0, 6, 0] = 0.9
        output[0, 11, 1] = 0.8
        output[0, 4, 2] = 0.99
        result = decode(output, 1, 0, 0, 640, 640)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["label"], "car")
        self.assertEqual(result[0]["box"], [80, 80, 120, 120])

    def test_multiscale_merge_does_not_count_same_car_twice(self):
        from traffic import merge_detections
        a = {"box": [10, 10, 40, 40], "label": "car", "score": 0.8}
        b = {"box": [11, 11, 41, 41], "label": "truck", "score": 0.7}
        c = {"box": [70, 70, 90, 90], "label": "car", "score": 0.6}
        self.assertEqual(merge_detections([a, b, c]), [a, c])

    def test_decode_rejects_incompatible_model(self):
        with self.assertRaises(ValueError):
            decode(np.zeros((1, 85, 8400)), 1, 0, 0, 640, 640)

    def test_no_detections(self):
        self.assertEqual(decode(np.zeros((1, 84, 10)), 1, 0, 0, 640, 640), [])

    def test_freshness_requires_timezone_and_recent_timestamp(self):
        for timestamp in (None, "bad", "2026-09-19T10:00:00", (NOW + timedelta(minutes=5)).isoformat()):
            self.assertEqual(freshness(timestamp, NOW), "unverified")
        self.assertEqual(freshness((NOW - timedelta(minutes=16)).isoformat(), NOW), "stale")
        self.assertEqual(freshness(NOW.isoformat(), NOW), "recent")

    def test_overlapping_boxes_not_double_counted(self):
        detection = {"box": [10, 10, 60, 60], "label": "car", "score": 0.9}
        one = summarize_zone([detection], ZONE, (100, 100))
        two = summarize_zone([detection, detection], ZONE, (100, 100))
        self.assertEqual(one["box_coverage_pct"], two["box_coverage_pct"])
        self.assertEqual(one["box_coverage_pct"], 25)

    def test_vehicle_outside_road_is_excluded(self):
        zone = {**ZONE, "polygon": [[0, 0], [0.4, 0], [0.4, 1], [0, 1]]}
        result = summarize_zone([{"box": [60, 30, 80, 60], "label": "car", "score": 0.9}], zone, (100, 100))
        self.assertEqual(result["vehicle_count"], 0)

    def test_dense_is_not_stopped(self):
        result = summarize_zone([{"box": [5, 5, 95, 95], "label": "bus", "score": 0.9}], ZONE, (100, 100))
        self.assertEqual(result["density"], "high")
        self.assertIsNone(result["speed_kmh"])
        self.assertIsNone(result["road_blocked"])

    def test_placeholder_abstains_without_running_model(self):
        class Forbidden:
            def detect(self, image):
                raise AssertionError("No ejecutar modelo sobre cartel")
        result, _ = analyze(np.zeros((217, 298, 3), np.uint8), Forbidden(), [ZONE], {}, now=NOW)
        self.assertEqual(result["zones"][0]["density"], "unknown")
        self.assertIsNone(result["zones"][0]["vehicle_count"])
        self.assertFalse(result["usable_for_route_review"])

    def test_historical_and_stale_never_support_current_route(self):
        class Empty:
            def detect(self, image):
                return []
        image = np.random.default_rng(0).integers(40, 210, (720, 1280, 3), dtype=np.uint8)
        for mode, timestamp in [("demo", NOW.isoformat()), ("live", (NOW - timedelta(hours=2)).isoformat())]:
            result, _ = analyze(image, Empty(), [ZONE], {"mode": mode, "source_updated_at": timestamp}, now=NOW)
            self.assertFalse(result["usable_for_route_review"])
            self.assertTrue(result["requires_human_review"])
            self.assertIsNone(result["zones"][0]["road_blocked"])
            self.assertIsNone(result["zones"][0]["mean_detection_score"])

    def test_invalid_polygons(self):
        for polygon in ([[0, 0], [1, 1]], [[0, 0], [2, 0], [0, 1]], [[0, 0]] * 3):
            with self.assertRaises(ValueError):
                summarize_zone([], {**ZONE, "polygon": polygon}, (100, 100))


class AlignmentTests(unittest.TestCase):
    def test_same_frame_matches_reference(self):
        from traffic import scene_alignment
        image = np.random.default_rng(8).integers(0, 255, (360, 640, 3), dtype=np.uint8)
        self.assertEqual(scene_alignment(image, image)["status"], "aligned")

    def test_pan_is_not_accepted_as_same_calibration(self):
        import cv2
        from traffic import scene_alignment
        image = np.random.default_rng(9).integers(0, 255, (360, 640, 3), dtype=np.uint8)
        moved = cv2.warpAffine(image, np.float32([[1, 0, 65], [0, 1, 10]]), (640, 360))
        self.assertNotEqual(scene_alignment(image, moved)["status"], "aligned")

    def test_overlay_does_not_make_different_scenes_match(self):
        import cv2
        from traffic import scene_alignment
        a = np.random.default_rng(1).integers(0, 255, (360, 640, 3), dtype=np.uint8)
        b = np.random.default_rng(2).integers(0, 255, (360, 640, 3), dtype=np.uint8)
        a[:50] = b[:50] = 255
        for image in (a, b):
            cv2.putText(image, "SAME CAMERA NAME", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        self.assertNotEqual(scene_alignment(a, b)["status"], "aligned")

    def test_no_reference_does_not_produce_road_count(self):
        class Fake:
            def detect(self, image):
                return [{"box": [10, 10, 30, 30], "label": "car", "score": 0.9}]
        image = np.random.default_rng(4).integers(20, 230, (360, 640, 3), dtype=np.uint8)
        result, _ = analyze(image, Fake(), [ZONE], {}, now=NOW)
        self.assertIsNone(result["zones"][0]["vehicle_count"])
        self.assertEqual(result["zones"][0]["density"], "unknown")
        self.assertEqual(result["calibration"]["status"], "unverified")
        self.assertGreater(result["scene"]["vehicle_count"], 0)

    def test_real_changed_view_never_reuses_old_road_polygons(self):
        import cv2
        from pathlib import Path
        from cameras import CAMERAS
        root = Path(__file__).resolve().parent
        reference = cv2.imread(str(root / "samples/cam_08301.jpg"))
        changed = cv2.imread(str(root / "samples/m30-front.jpg"))
        self.assertIsNotNone(reference)
        self.assertIsNotNone(changed)

        class Empty:
            def detect(self, image):
                return []
        zones = CAMERAS["08301"]["zones"]
        result, annotated = analyze(changed, Empty(), zones, {}, now=NOW,
                                    references=[{"id": "original", "image": reference, "zones": zones}])
        self.assertNotEqual(result["calibration"]["status"], "aligned")
        self.assertTrue(all(z["vehicle_count"] is None and z["density"] == "unknown" for z in result["zones"]))
        self.assertTrue(np.array_equal(changed, annotated))

    def test_lighting_change_keeps_stable_scene(self):
        import cv2
        from pathlib import Path
        from traffic import scene_alignment
        reference = cv2.imread(str(Path(__file__).resolve().parent / "samples/cam_06303.jpg"))
        darker = cv2.convertScaleAbs(reference, alpha=0.9, beta=3)
        self.assertEqual(scene_alignment(reference, darker)["status"], "aligned")

    def test_tiles_cover_whole_image(self):
        from traffic import tile_windows
        coverage = np.zeros((720, 1280), np.uint8)
        windows = tile_windows(1280, 720)
        self.assertGreater(len(windows), 1)
        for x, y, w, h in windows:
            coverage[y:y + h, x:x + w] = 1
            self.assertLessEqual(max(w, h), 512)
        self.assertTrue(coverage.all())

    def test_tiling_does_not_duplicate_car(self):
        from traffic import detect_multiscale
        image = np.zeros((512, 800, 3), np.uint8)
        image[200:240, 350:390, 0] = 255

        class Fake:
            def detect(self, tile):
                ys, xs = np.where(tile[:, :, 0] > 0)
                if not len(xs):
                    return []
                return [{"box": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1], "label": "car", "score": 0.9}]
        self.assertEqual(len(detect_multiscale(Fake(), image)), 1)

    def test_provider_timestamp_expires_at_ten_minutes(self):
        self.assertEqual(freshness((NOW - timedelta(seconds=600)).isoformat(), NOW), "recent")
        self.assertEqual(freshness((NOW - timedelta(seconds=601)).isoformat(), NOW), "stale")


class CloudTests(unittest.TestCase):
    def evidence(self, mode="live", age=0, cover=30):
        return {"schema_version": "1.0", "source": {"camera_id": "test", "mode": mode,
                "source_updated_at": (datetime.now(timezone.utc) - timedelta(seconds=age)).isoformat()},
                "quality": {"status": "basic_checks_passed"},
                "zones": [{"id": "road", "vehicle_count": 3, "box_coverage_pct": cover, "density": "low"}]}

    def validate(self, value):
        return sandbox(VALIDATE, {"observation_json": json.dumps(value)})

    def test_cloud_recomputes_density_instead_of_trusting_input(self):
        result = self.validate(self.evidence())
        self.assertEqual(result["density"], "high")
        self.assertTrue(result["current_visual_evidence"])

    def test_cloud_recomputes_age_and_demo_status(self):
        for mode, age in [("demo", 0), ("live", 1000), ("live", -300)]:
            self.assertFalse(self.validate(self.evidence(mode, age))["current_visual_evidence"])

    def test_cloud_rejects_nonfinite_coverage(self):
        for cover in (float("nan"), float("inf"), -1, 101, True, "20"):
            self.assertEqual(self.validate(self.evidence(cover=cover))["density"], "unknown")

    def test_cloud_rejects_boolean_vehicle_count(self):
        item = self.evidence()
        item["zones"][0]["vehicle_count"] = True
        self.assertEqual(self.validate(item)["density"], "unknown")

    def test_cloud_rejects_bad_quality(self):
        item = self.evidence()
        item["quality"]["status"] = "unusable"
        self.assertFalse(self.validate(item)["valid_image_evidence"])

    def test_cloud_rejects_malformed_input(self):
        for raw in ("bad", "[]", "null", "x" * 100001):
            result = sandbox(VALIDATE, {"observation_json": raw})
            self.assertEqual(result["density"], "unknown")
            self.assertFalse(result["current_visual_evidence"])

    def test_cloud_final_never_authorizes_dispatch(self):
        validated = self.validate(self.evidence())
        output = sandbox(FINALIZE, {"evidence_json": validated["evidence_json"], "summary": "Enviar bomberos ahora"})
        result = json.loads(output["result_json"])
        self.assertFalse(result["dispatch_authorized"])
        self.assertFalse(result["usable_for_automatic_routing"])
        self.assertIsNone(result["recommended_route"])
        self.assertTrue(result["requires_human_review"])
        self.assertEqual(result["review_priority"], "inspect_density")


class APIGuardTests(unittest.TestCase):
    def test_invalid_road_measurements_never_reach_happyrobot(self):
        import threading
        import urllib.error
        import urllib.request
        from http.server import ThreadingHTTPServer
        from types import SimpleNamespace
        import server

        now = datetime.now(timezone.utc)
        observations = {
            "pan": {"source": {"mode": "live", "source_updated_at": now.isoformat()},
                    "calibration": {"status": "unverified"}, "zones": [{"vehicle_count": None}]},
            "old": {"source": {"mode": "live", "source_updated_at": (now - timedelta(minutes=11)).isoformat()},
                    "calibration": {"status": "aligned"}, "zones": [{"vehicle_count": 2}]},
            "empty": {"source": {"mode": "demo"}, "calibration": {"status": "aligned"}, "zones": [{"vehicle_count": 0}]},
        }

        class Handler(server.Handler):
            lab = SimpleNamespace(api=object(), observations=observations)

        with patch.object(server, "STATE") as state, patch.object(server, "start_run") as paid_call:
            state.exists.return_value = True
            with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as http:
                worker = threading.Thread(target=http.serve_forever, daemon=True)
                worker.start()
                try:
                    for identifier in observations:
                        with self.subTest(identifier=identifier):
                            request = urllib.request.Request(f"http://127.0.0.1:{http.server_port}/api/workflow",
                                                             data=json.dumps({"observation_id": identifier}).encode(),
                                                             headers={"Content-Type": "application/json"})
                            with self.assertRaises(urllib.error.HTTPError) as error:
                                urllib.request.urlopen(request, timeout=3)
                            self.assertEqual(error.exception.code, 409)
                            error.exception.close()
                    paid_call.assert_not_called()
                finally:
                    http.shutdown()
                    worker.join()


class PlatformTests(unittest.TestCase):
    def test_extract_output_is_read_from_response(self):
        import happyrobot
        writes = []
        names = ["Recibir evidencia visual de webcam", "Validar fecha, calidad y densidad",
                 "IA: resumir evidencia para el operador", "Emitir propuesta sin autorizar despachos"]

        class Fake:
            def request(self, method, path, body=None):
                if method == "PUT":
                    writes.append((path, body))
                if path == "/workflows/w":
                    return {"latest_version": {"id": "v2"}}
                if path == "/versions/v2/nodes":
                    return [{"id": str(i), "persistent_id": f"p{i}", "name": name} for i, name in enumerate(names)]
                return {}

        with patch.object(happyrobot, "state", return_value={"workflow_id": "w"}), patch.object(happyrobot, "save_state"):
            happyrobot.publish_draft(Fake(), "v2")
        final = next(body for path, body in writes if path == "/versions/v2/nodes/3")
        inputs = final["configuration"]["input_data"]
        paths = [item["value"][0]["children"][0]["variable_id"] for item in inputs]
        self.assertEqual(paths, ["evidence_json", "response.summary", "response.operator_check"])
        validation = next(body for path, body in writes if path == "/versions/v2/nodes/1")
        variable = validation["configuration"]["input_data"][0]["value"][0]["children"][0]
        self.assertEqual(variable["group_id"], "p0")

    def test_failed_output_is_not_completed(self):
        import happyrobot

        class Fake:
            def request(self, method, path):
                return [{"node_id": "final", "output_id": "o"}] if path.endswith("/nodes") else {"error": "sandbox failed", "data": None}

        with patch.object(happyrobot, "state", return_value={"nodes": {"finalize": "final"}}):
            self.assertEqual(happyrobot.run_result(Fake(), "r")["status"], "failed")

    def test_running_output_is_not_failed(self):
        import happyrobot

        class Fake:
            def request(self, method, path):
                return [{"node_id": "final", "output_id": "o"}] if path.endswith("/nodes") else {"status": "running", "error": None, "data": None}

        with patch.object(happyrobot, "state", return_value={"nodes": {"finalize": "final"}}):
            self.assertEqual(happyrobot.run_result(Fake(), "r")["status"], "pending")

    def test_failed_run_stops_polling(self):
        import happyrobot

        class Fake:
            def request(self, method, path):
                return [] if path.endswith("/nodes") else {"status": "failed"}

        with patch.object(happyrobot, "state", return_value={"nodes": {"finalize": "final"}}):
            self.assertEqual(happyrobot.run_result(Fake(), "r")["status"], "failed")


if __name__ == "__main__":
    unittest.main()
