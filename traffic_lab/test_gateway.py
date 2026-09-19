import json
import unittest

from gateway_vision import request_body, validate_response
from traffic_catalog import Catalog, allowed_snapshot, candidate


class CatalogTests(unittest.TestCase):
    def camera(self):
        return {"id": "madrid-08301", "name": "Test", "source": "madrid", "category": "traffic", "kind": "snapshot",
                "lat": 40.4, "lon": -3.7, "imageUrl": "https://informo.madrid.es/cameras/Camara08301.jpg"}

    def test_known_https_camera_is_candidate_not_verified(self):
        record = self.camera()
        self.assertTrue(candidate(record))
        catalog = Catalog({"cameras": [record]})
        self.assertFalse(catalog.summary()["live_availability_verified"])
        self.assertEqual(catalog.get(record["id"])["availability"], "not_verified")

    def test_does_not_accept_video_external_links_or_weather(self):
        for update in ({"kind": "player"}, {"kind": "link"}, {"category": "weather"}, {"lat": float("nan")}):
            self.assertFalse(candidate({**self.camera(), **update}))

    def test_duplicate_ids_are_rejected(self):
        with self.assertRaises(ValueError):
            Catalog({"cameras": [self.camera(), self.camera()]})

    def test_blocks_local_urls_credentials_and_arbitrary_query(self):
        for url in ("http://127.0.0.1/image.jpg", "https://informo.madrid.es.evil.test/cameras/Camara1.jpg",
                    "https://user:password@informo.madrid.es/cameras/Camara1.jpg",
                    "https://informo.madrid.es/cameras/Camara1.jpg?url=secret", "file:///camera.jpg", None):
            self.assertFalse(allowed_snapshot(url))


class GatewayTests(unittest.TestCase):
    def result(self, **changes):
        return {"image_status": "road_visible", "density": "low", "vehicle_count_estimate": 3,
                "reason": "Vehículos separados", "limitations": ["No mide velocidad"], **changes}

    def test_actual_image_attachment_not_plain_url_prompt(self):
        body = request_body({"image_url": "https://informo.madrid.es/cameras/Camara08301.jpg"})
        self.assertEqual(body["messages"][1]["content"][1]["type"], "image_url")
        self.assertEqual(body["max_tokens"], 700)
        self.assertTrue(body["response_format"]["json_schema"]["strict"])

    def test_gateway_request_rejects_untrusted_url(self):
        with self.assertRaises(ValueError):
            request_body({"image_url": "https://localhost/image.jpg"})

    def test_model_cannot_authorize_dispatch_or_verify_time(self):
        result = validate_response(json.dumps(self.result()), "camera")
        self.assertEqual(result["density"], "low")
        self.assertFalse(result["current_visual_evidence"])
        self.assertFalse(result["dispatch_authorized"])
        self.assertIsNone(result["speed_kmh"])

    def test_unavailable_or_null_count_abstains(self):
        for changes in ({"image_status": "unavailable"}, {"vehicle_count_estimate": None}, {"density": "unknown"}):
            result = validate_response(json.dumps(self.result(**changes)), "camera")
            self.assertEqual(result["density"], "unknown")
            self.assertIsNone(result["vehicle_count_estimate"])

    def test_invalid_responses_abstain(self):
        for raw in ("not json", "null", "[]", json.dumps(self.result(vehicle_count_estimate=True)),
                    json.dumps(self.result(dispatch_authorized=True)), json.dumps(self.result(density="free"))):
            self.assertEqual(validate_response(raw, "camera")["density"], "unknown")


class RemoteCodeTests(unittest.TestCase):
    def test_preparation_executes_without_project_imports(self):
        from remote_setup import prepare_code
        scope = {"input_data": {"camera_id": "madrid-08301", "image_url": "https://informo.madrid.es/cameras/Camara08301.jpg"}}
        exec(prepare_code(), scope)
        body = json.loads(scope["output"]["body_json"])
        self.assertEqual(body["messages"][1]["content"][1]["type"], "image_url")
        self.assertEqual(scope["output"]["camera_id"], "madrid-08301")

    def test_preparation_stops_untrusted_url_before_paid_node(self):
        from remote_setup import prepare_code
        with self.assertRaises(ValueError):
            exec(prepare_code(), {"input_data": {"camera_id": "x", "image_url": "http://localhost/"}})

    def test_cloud_final_abstains_on_truncation(self):
        from remote_setup import finalize_code
        from datetime import datetime
        from zoneinfo import ZoneInfo
        raw = json.dumps({"image_status": "road_visible", "density": "low", "vehicle_count_estimate": 1,
                          "reason": "Test", "limitations": [], "timestamp_legible": True,
                          "timestamp_text": datetime.now(ZoneInfo("Europe/Madrid")).strftime("%d-%m-%Y %H:%M:%S")})
        for finish, density in (("stop", "low"), ("length", "unknown"), ("content_filter", "unknown")):
            scope = {"input_data": {"camera_id": "x", "content": raw, "finish_reason": finish}}
            exec(finalize_code(), scope)
            result = json.loads(scope["output"]["result_json"])
            self.assertEqual(result["density"], density)
            self.assertFalse(result["capture_time_verified"])
            self.assertFalse(result["dispatch_authorized"])

    def test_native_bearer_auth_uses_variable_reference(self):
        from remote_setup import inference_config
        config = inference_config("prepare")
        self.assertEqual(config["authType"], "bearer")
        self.assertEqual(config["token"][0]["children"][0]["variable_id"], "AI_GATEWAY_API_KEY")
        self.assertNotIn("Authorization", [header["key"] for header in config["headers"]])


if __name__ == "__main__":
    unittest.main()
