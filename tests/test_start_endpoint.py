import os
import unittest
from unittest.mock import patch

from api import start as start_module


class StartEndpointTests(unittest.TestCase):
    def test_falls_back_to_local_worker_when_worker_url_missing(self):
        class DummyProcess:
            pid = 1234

            def poll(self):
                return None

        with patch.dict(os.environ, {}, clear=True), patch.object(
            start_module.subprocess,
            "Popen",
            return_value=DummyProcess(),
        ) as popen_mock:
            result = start_module.dispatch_start_request(b"")

        self.assertTrue(result["ok"])
        self.assertIn("fallback", result["message"].lower())
        popen_mock.assert_called_once()

    def test_uses_selected_recipient_email_for_preview_emails(self):
        class DummyProcess:
            pid = 4321

            def poll(self):
                return None

        def fake_popen(*args, **kwargs):
            self.assertEqual(kwargs["env"]["PREVIEW_EMAIL"], "review@example.com")
            return DummyProcess()

        with patch.dict(os.environ, {}, clear=True), patch.object(
            start_module.subprocess,
            "Popen",
            side_effect=fake_popen,
        ) as popen_mock:
            result = start_module.dispatch_start_request(b'{"recipient_email": "review@example.com"}')

        self.assertTrue(result["ok"])
        self.assertEqual(popen_mock.call_count, 1)


if __name__ == "__main__":
    unittest.main()
