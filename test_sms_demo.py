import http.client
import json
import threading
import unittest
from unittest.mock import Mock
from uuid import uuid4

from sms_demo import HappyRobotClient, HappyRobotError, SMSService, make_server, validate_sms


class SMSTests(unittest.TestCase):
    def payload(self, **changes):
        return {"to": "+34600000000", "message": "Prueba", "confirmed": True,
                "request_id": str(uuid4()), **changes}

    def test_validation(self):
        self.assertEqual(validate_sms(self.payload(to=" +34 600 000 000 "))[0], "+34600000000")
        for changes in ({"to": "112"}, {"to": "+15304471317"}, {"to": None},
                        {"message": " "}, {"message": "x" * 481}, {"message": {}},
                        {"confirmed": False}, {"confirmed": "true"}, {"request_id": "x"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_sms(self.payload(**changes))
        with self.assertRaises(ValueError):
            validate_sms([])

    def test_one_click_starts_one_run_and_duplicates_are_cached(self):
        client = Mock()
        client.request.return_value = {"run_id": "run-1"}
        service = SMSService(client, "workflow-1")
        body = self.payload()
        first = service.send(body)
        self.assertEqual(first, service.send(body))
        self.assertEqual(first[0], 202)
        self.assertEqual(first[1]["run_id"], "run-1")
        client.request.assert_called_once_with("POST", "/workflows/workflow-1/runs", {
            "environment": "production", "payload": {"to": "+34600000000", "message": "Prueba"},
        })
        self.assertEqual(service.send({**body, "message": "Otro"})[0], 409)
        self.assertEqual(service.send(self.payload())[0], 429)

    def test_unknown_result_is_not_retried_or_reported_as_sent(self):
        for error in (TimeoutError(), HappyRobotError(403, "private upstream detail")):
            with self.subTest(error=error):
                client = Mock()
                client.request.side_effect = error
                service = SMSService(client, "workflow-1")
                body = self.payload()
                result = service.send(body)
                self.assertEqual(result[0], 502)
                self.assertNotIn("private", json.dumps(result))
                self.assertEqual(service.send(body), result)
                client.request.assert_called_once()

    def test_missing_configuration_never_calls_provider(self):
        client = Mock()
        service = SMSService(client, "")
        self.assertFalse(service.config()["ready"])
        self.assertEqual(service.send(self.payload())[0], 503)
        client.request.assert_not_called()

    def test_hook_key_required_and_no_fallback_after_failure(self):
        client = Mock(hook_key="")
        service = SMSService(client, "workflow-1", "test-slug")
        self.assertFalse(service.config()["ready"])
        self.assertEqual(service.send(self.payload())[0], 503)
        client.trigger_hook.assert_not_called()
        client.hook_key = "test-only-hook-key"
        client.trigger_hook.side_effect = TimeoutError()
        self.assertTrue(service.config()["ready"])
        body = self.payload()
        self.assertEqual(service.send(body)[0], 502)
        service.send(body)
        client.trigger_hook.assert_called_once_with("test-slug", {"to": "+34600000000", "message": "Prueba"})
        client.request.assert_not_called()

    def test_hook_transport_keeps_account_key_out_of_request(self):
        client = HappyRobotClient(api_key="test-only-api-key", hook_key="test-only-hook-key")
        client.exchange = Mock(return_value={"run_id": "test-run"})
        response = client.trigger_hook("test-slug", {"to": "", "message": ""})
        self.assertEqual(response["run_id"], "test-run")
        request = client.exchange.call_args.args[0]
        self.assertEqual(request.full_url, "https://workflows.platform.eu.happyrobot.ai/hooks/test-slug")
        self.assertEqual(request.get_header("X-api-key"), "test-only-hook-key")
        self.assertIsNone(request.get_header("Authorization"))
        self.assertNotIn(client.api_key, str(request.headers))
        with self.assertRaises(ValueError):
            client.trigger_hook("//example.com", {})
        self.assertNotIn(client.hook_key, json.dumps(SMSService(client, "workflow-1", "test-slug").config()))

    def test_missing_run_id_is_not_success(self):
        client = Mock()
        client.request.return_value = {"status": "ok"}
        service = SMSService(client, "workflow-1")
        self.assertEqual(service.send(self.payload())[0], 502)

    def test_failed_run_explains_provider_error_without_leaking_raw_details(self):
        client = Mock()
        service = SMSService(client, "workflow-1")
        service.runs.add("run-1")
        for code, hint in (("40305", "perfil de mensajería"), ("40013", "remitente")):
            with self.subTest(code=code):
                client.request.side_effect = [
                    {"id": "run-1", "workflow_id": "workflow-1", "status": "failed"},
                    {"data": [{"status": "failed", "error": "Telnyx returned 400: " + json.dumps({
                        "errors": [{"code": code, "detail": "private upstream details"}],
                    })}]},
                ]
                status, result = service.run_status("run-1")
                self.assertEqual(status, 200)
                self.assertEqual(result["status"], "failed")
                self.assertEqual(result["provider_error_code"], code)
                self.assertIn(hint, result["error"])
                self.assertNotIn("private", json.dumps(result))

    def test_failed_run_keeps_status_if_diagnostics_are_unavailable(self):
        client = Mock()
        service = SMSService(client, "workflow-1")
        service.runs.add("run-1")
        client.request.side_effect = [
            {"id": "run-1", "workflow_id": "workflow-1", "status": "failed"},
            HappyRobotError(500, "private error"),
        ]
        status, result = service.run_status("run-1")
        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "failed")
        self.assertIn("HappyRobot", result["error"])
        self.assertNotIn("private", json.dumps(result))

    def test_status_is_scoped_to_runs_created_here(self):
        client = Mock()
        service = SMSService(client, "workflow-1")
        self.assertEqual(service.run_status("other")[0], 404)
        client.request.assert_not_called()
        client.request.return_value = {"run_id": "run-1"}
        service.send(self.payload())
        client.request.return_value = {"id": "run-1", "workflow_id": "workflow-1", "status": "completed"}
        result = service.run_status("run-1")
        self.assertEqual(result[1]["status"], "completed")
        self.assertNotIn("delivered", result[1])


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = Mock()
        cls.service = SMSService(cls.client, "workflow-1")
        cls.server = make_server(cls.service, port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        connection.request(method, path, body, headers or {})
        response = connection.getresponse()
        status, data, output_headers = response.status, response.read(), dict(response.getheaders())
        connection.close()
        return status, data, output_headers

    def test_page_and_config_do_not_send_anything(self):
        self.client.reset_mock()
        for path in ("/", "/sms.js", "/sms.css", "/api/config"):
            result = self.request("GET", path)
            self.assertEqual(result[0], 200)
            self.assertEqual(result[2]["Cache-Control"], "no-store")
        self.client.request.assert_not_called()

    def test_secrets_and_arbitrary_paths_are_not_served(self):
        for path in ("/.env", "/sms-workflow.json", "/../sms_demo.py", "/api/send"):
            self.assertEqual(self.request("GET", path)[0], 404)

    def test_cross_origin_bad_host_and_missing_token_are_blocked(self):
        body = json.dumps(SMSTests().payload())
        headers = {"Content-Type": "application/json", "X-CSRF-Token": self.service.csrf_token}
        self.assertEqual(self.request("POST", "/api/send", body, {
            **headers, "Origin": "https://example.com"})[0], 403)
        self.assertEqual(self.request("POST", "/api/send", body, {
            "Content-Type": "application/json"})[0], 403)
        self.assertEqual(self.request("GET", "/", headers={"Host": "example.com"})[0], 403)

    def test_bad_json_and_large_bodies(self):
        headers = {"Content-Type": "application/json", "X-CSRF-Token": self.service.csrf_token}
        self.assertEqual(self.request("POST", "/api/send", "{", headers)[0], 400)
        self.assertEqual(self.request("POST", "/api/send", "x" * 9000, headers)[0], 413)
        self.assertEqual(self.request("POST", "/api/send", "{}", {
            **headers, "Content-Type": "text/plain"})[0], 415)

    def test_valid_submission(self):
        self.client.request.return_value = {"run_id": "run-http"}
        headers = {"Content-Type": "application/json", "X-CSRF-Token": self.service.csrf_token,
                   "Origin": f"http://127.0.0.1:{self.port}"}
        result = self.request("POST", "/api/send", json.dumps(SMSTests().payload()), headers)
        self.assertEqual(result[0], 202)
        self.assertEqual(json.loads(result[1])["run_id"], "run-http")


if __name__ == "__main__":
    unittest.main()
