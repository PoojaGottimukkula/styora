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
            result = start_module.dispatch_start_request()

        self.assertTrue(result["ok"])
        self.assertIn("fallback", result["message"].lower())
        popen_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
