#!/usr/bin/env python3
"""Simple concurrency helper for Zoe.

Tracks running agents and blocks spawns beyond ZOE_MAX_CONCURRENT.
"""

import json
import os
import time
from pathlib import Path

REGISTRY = Path(__file__).parent.parent / "tasks_registry.json"
MAX_CONCURRENT = int(os.environ.get("ZOE_MAX_CONCURRENT", "3"))
POLL_INTERVAL = 5  # seconds


def count_running() -> int:
    if not REGISTRY.exists():
        return 0
    try:
        data = json.loads(REGISTRY.read_text())
    except (json.JSONDecodeError, OSError):
        return 0
    return sum(1 for t in data.get("tasks", []) if t.get("status") == "running")


def wait_for_slot(timeout: float = 3600) -> bool:
    """Block until fewer than MAX_CONCURRENT agents are running."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if count_running() < MAX_CONCURRENT:
            return True
        time.sleep(POLL_INTERVAL)
    return False


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "wait":
        ok = wait_for_slot()
        sys.exit(0 if ok else 1)
    print(f"Running agents: {count_running()} / {MAX_CONCURRENT}")
