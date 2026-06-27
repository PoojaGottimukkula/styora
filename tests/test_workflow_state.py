import json
import os
import tempfile
import unittest

from utils.workflow_state import read_workflow_state, write_workflow_state


class WorkflowStateTests(unittest.TestCase):
    def test_write_and_read_workflow_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state = {
                "status": "discovering",
                "products": ["https://example.com/product-a"],
                "preview_emails": [{"product_id": "A1", "status": "queued"}],
            }
            written = write_workflow_state(state, base_dir=tmpdir)
            self.assertEqual(written["status"], "discovering")
            loaded = read_workflow_state(base_dir=tmpdir)
            self.assertEqual(loaded["products"], state["products"])
            self.assertEqual(loaded["preview_emails"], state["preview_emails"])


if __name__ == "__main__":
    unittest.main()
