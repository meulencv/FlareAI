import http.client
import json
import threading
import time
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from sms_demo import HappyRobotError
from telegram_demo import SIMULATION_PREFIX, TelegramClient, TelegramService, telegram_server

TOKEN = "123456789:" + "A" * 35
STATE = {"workflow_id": "workflow-telegram", "version_id": "version-1", "published": True,
         "hook_slug": "telegram-test", "token_variable_id": "variable-1"}


class TelegramTests(unittest.TestCase):
    def service(self):
        client = Mock(hook_key="test-hook")
        return TelegramService(client, STATE.copy())

    def connected(self):
        service = self.service()
        service.bot = Mock()
        service.bot_info = {"username": "FlareTestBot", "id": 123456789}
        service.chat = {"id": 123, "name": "Usuario de prueba"}
        service.workflow_verified = True
        return service

    def payload(self, **changes):
        return {"message": "Mensaje de prueba", "confirmed": True, "request_id": str(uuid4()), **changes}

    def test_workflow_verification_uses_invalid_chat_and_gates_sending(self):
        service = self.connected()
        service.workflow_verified = False
        self.assertEqual(service.send(self.payload())[0], 503)
        service.client.trigger_hook.assert_not_called()
        service.client.trigger_hook.return_value = {"run_id": "verification-run"}
        with patch("telegram_demo.prepare_workflow", return_value=STATE.copy()):
            status, result = service.verify_workflow({})
        self.assertEqual(status, 200)
        self.assertTrue(result["workflow_verified"])
        self.assertTrue(result["ready"])
        body = json.loads(service.client.trigger_hook.call_args.args[1]["telegram_body"])
        self.assertEqual(body["chat_id"], 0)
        self.assertTrue(body["text"].startswith(SIMULATION_PREFIX))

    def test_rejected_hook_stays_disabled(self):
        service = self.connected()
        service.workflow_verified = False
        service.client.trigger_hook.side_effect = HappyRobotError(401, "private details")
        with patch("telegram_demo.prepare_workflow", return_value=STATE.copy()):
            status, result = service.verify_workflow({})
        self.assertEqual(status, 502)
        self.assertFalse(service.config()["ready"])
        self.assertNotIn("private", json.dumps(result))

    def test_startup_and_config_do_not_send_messages(self):
        service = self.service()
        self.assertFalse(service.config()["ready"])
        self.assertEqual(service.config()["channel"], "telegram")
        service.client.trigger_hook.assert_not_called()
        self.assertNotIn(TOKEN, json.dumps(service.config()))

    def test_connect_checks_bot_and_saves_hidden_variable_only_after_consent(self):
        service = self.service()
        bot = Mock()
        bot.call.side_effect = [{"id": 123456789, "is_bot": True, "username": "FlareTestBot"}, {"url": ""}]
        with patch("telegram_demo.TelegramClient", return_value=bot):
            with self.assertRaises(ValueError):
                service.connect({"token": TOKEN})
            service.client.request.assert_not_called()
            status, result = service.connect({"token": TOKEN, "confirmed_store_token": True})
        self.assertEqual(status, 200)
        self.assertFalse(result["ready"])
        self.assertIn("t.me/FlareTestBot?start=", result["pair_link"])
        self.assertNotIn(TOKEN, json.dumps(result))
        path = service.client.request.call_args.args[1]
        self.assertEqual(path, "/workflows/workflow-telegram/variables/variable-1")
        self.assertEqual(service.client.request.call_args.args[2]["value_production"], TOKEN)
        service.client.trigger_hook.assert_not_called()

    def test_existing_bot_webhook_is_not_deleted_or_modified(self):
        service = self.service()
        bot = Mock()
        bot.call.side_effect = [{"id": 123456789, "is_bot": True, "username": "FlareTestBot"},
                                {"url": "https://example.com/existing-webhook"}]
        with patch("telegram_demo.TelegramClient", return_value=bot):
            status, result = service.connect({"token": TOKEN, "confirmed_store_token": True})
        self.assertEqual(status, 409)
        self.assertIn("webhook", result["error"])
        service.client.request.assert_not_called()
        self.assertEqual([call.args[0] for call in bot.call.call_args_list], ["getMe", "getWebhookInfo"])

    def test_pairing_requires_private_chat_fresh_nonce_and_matching_sender(self):
        service = self.connected()
        service.chat = None
        service.pair_started = time.time() - 1
        service.pair_expires = time.time() + 600
        service.pair_nonce = "pairing-proof"
        base = {"date": int(time.time()), "text": "/start pairing-proof", "from": {"id": 123, "is_bot": False},
                "chat": {"id": 123, "type": "private", "first_name": "Usuario"}}
        wrong = [{**base, "text": "/start someone-else"},
                 {**base, "chat": {"id": -100, "type": "group"}},
                 {**base, "from": {"id": 999, "is_bot": False}},
                 {**base, "date": int(time.time()) - 900}]
        service.bot.call.return_value = [{"update_id": i, "message": msg} for i, msg in enumerate(wrong)]
        self.assertEqual(service.pair({})[0], 202)
        self.assertIsNone(service.chat)
        service.bot.call.return_value = [{"update_id": 10, "message": base}]
        self.assertEqual(service.pair({})[0], 200)
        self.assertEqual(service.chat["id"], 123)
        self.assertTrue(service.config()["ready"])
        self.assertNotIn("pairing-proof", service.config()["pair_link"])
        service.client.trigger_hook.assert_not_called()

    def test_expired_pairing_is_rejected_without_reading_updates(self):
        service = self.connected()
        service.chat = None
        service.pair_expires = time.time() - 1
        self.assertEqual(service.pair({})[0], 409)
        service.bot.call.assert_not_called()

    def test_message_is_bound_to_paired_chat_prefixed_and_sent_once(self):
        service = self.connected()
        service.client.trigger_hook.return_value = {"run_id": "telegram-run"}
        body = self.payload(chat_id=999, token="not-used")
        result = service.send(body)
        self.assertEqual(result[0], 202)
        self.assertEqual(service.send(body), result)
        service.client.trigger_hook.assert_called_once()
        slug, payload = service.client.trigger_hook.call_args.args
        self.assertEqual(slug, "telegram-test")
        data = json.loads(payload["telegram_body"])
        self.assertEqual(data["chat_id"], 123)
        self.assertEqual(data["text"], SIMULATION_PREFIX + "Mensaje de prueba")
        self.assertNotIn("parse_mode", data)
        self.assertNotIn(TOKEN, json.dumps(payload))
        self.assertEqual(service.send(self.payload())[0], 429)

    def test_quotes_and_unicode_are_json_encoded_without_markup(self):
        service = self.connected()
        service.client.trigger_hook.return_value = {"run_id": "telegram-run"}
        message = 'Texto "entre comillas"\nEspaña <b>literal</b>'
        self.assertEqual(service.send(self.payload(message=message))[0], 202)
        payload = service.client.trigger_hook.call_args.args[1]
        self.assertEqual(json.loads(payload["telegram_body"])["text"], SIMULATION_PREFIX + message)

    def test_invalid_messages_and_missing_pair_do_not_send(self):
        service = self.connected()
        for changes in ({"message": ""}, {"message": "x" * 1501}, {"message": []},
                        {"message": "\ud800"}, {"confirmed": False}, {"request_id": "invalid"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                service.send(self.payload(**changes))
        service.chat = None
        self.assertEqual(service.send(self.payload())[0], 503)
        service.client.trigger_hook.assert_not_called()

    def test_telegram_transport_has_fixed_host_and_no_send_method(self):
        bot = TelegramClient(TOKEN)
        with self.assertRaises(ValueError):
            bot.call("sendMessage", {"chat_id": 123, "text": "not authorized here"})
        with self.assertRaises(ValueError):
            bot.call("https://example.com")


class TelegramHTTPTests(unittest.TestCase):
    def test_assets_and_private_setup_route(self):
        service = TelegramService(Mock(hook_key="test-hook"), STATE.copy())
        server = telegram_server(service, port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
        try:
            connection.request("GET", "/")
            response = connection.getresponse()
            self.assertEqual(response.status, 200)
            self.assertIn(b"Telegram", response.read())
            connection.request("POST", "/api/connect", "{}", {"Content-Type": "application/json"})
            response = connection.getresponse()
            self.assertEqual(response.status, 403)
            response.read()
            service.client.trigger_hook.assert_not_called()
        finally:
            connection.close()
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
