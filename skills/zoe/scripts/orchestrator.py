#!/usr/bin/env python3
"""Zoe orchestrator: task lifecycle state machine.

States: pending -> running -> finished|failed
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

REGISTRY = Path(__file__).parent.parent / "tasks_registry.json"
VALID_STATES = {"pending", "running", "failed", "finished"}


def _max_concurrent() -> int:
    return int(os.environ.get("ZOE_MAX_CONCURRENT", "3"))


def _load() -> dict:
    if not REGISTRY.exists():
        return {"version": 1, "tasks": []}
    try:
        return json.loads(REGISTRY.read_text())
    except (json.JSONDecodeError, OSError):
        return {"version": 1, "tasks": []}


def _save(data: dict) -> None:
    REGISTRY.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def enqueue(task_id: str, role: str, worktree: str, instruction: str) -> None:
    """Add a new task in pending state."""
    data = _load()
    data["tasks"].append({
        "id": task_id,
        "role": role,
        "worktree": worktree,
        "instruction": instruction,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    })
    _save(data)


def start_next() -> None:
    """Promote pending tasks to running up to MAX_CONCURRENT limit."""
    data = _load()
    running = sum(1 for t in data["tasks"] if t.get("status") == "running")
    slots = _max_concurrent() - running
    if slots <= 0:
        _save(data)
        return
    for t in data["tasks"]:
        if t.get("status") == "pending" and slots > 0:
            t["status"] = "running"
            t["updated_at"] = datetime.now().isoformat()
            slots -= 1
    _save(data)


def mark(task_id: str, status: str, output: str = "") -> None:
    """Update task status and optional output."""
    if status not in VALID_STATES:
        raise ValueError(f"Invalid status {status!r}; must be one of {VALID_STATES}")
    data = _load()
    for t in data["tasks"]:
        if t["id"] == task_id:
            t["status"] = status
            t["updated_at"] = datetime.now().isoformat()
            if output:
                t["output"] = output
            break
    _save(data)


def can_spawn() -> bool:
    """Return True if running count is below MAX_CONCURRENT."""
    data = _load()
    running = sum(1 for t in data["tasks"] if t.get("status") == "running")
    return running < _max_concurrent()


def _summary_counts() -> dict:
    """Return counts per status."""
    data = _load()
    counts = {"running": 0, "finished": 0, "failed": 0, "pending": 0}
    for t in data["tasks"]:
        counts[t.get("status", "pending")] += 1
    return counts


def summary() -> None:
    """Print running/finished/failed counts."""
    counts = _summary_counts()
    print(f"running={counts['running']} finished={counts['finished']} failed={counts['failed']} pending={counts['pending']}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: orchestrator.py enqueue|start|mark|summary|can-spawn ...")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "enqueue" and len(sys.argv) >= 6:
        enqueue(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif cmd == "start" and len(sys.argv) == 2:
        start_next()
    elif cmd == "mark" and len(sys.argv) >= 4:
        mark(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
    elif cmd == "summary" and len(sys.argv) == 2:
        summary()
    elif cmd == "can-spawn" and len(sys.argv) == 2:
        sys.exit(0 if can_spawn() else 1)
    else:
        print("Unknown command or missing args")
        sys.exit(1)


if __name__ == "__main__":
    main()
