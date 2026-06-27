import json
import os
from pathlib import Path


STATE_FILE = "workflow_state.json"


def get_state_path(base_dir=None):
    if base_dir is None:
        base_dir = os.getcwd()
    return os.path.join(base_dir, STATE_FILE)


def read_workflow_state(base_dir=None):
    path = get_state_path(base_dir)
    if not os.path.exists(path):
        return {"status": "idle", "products": [], "preview_emails": []}

    with open(path, "r", encoding="utf-8") as handle:
        try:
            return json.load(handle)
        except json.JSONDecodeError:
            return {"status": "idle", "products": [], "preview_emails": []}


def write_workflow_state(state, base_dir=None):
    path = get_state_path(base_dir)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2)
    return state
