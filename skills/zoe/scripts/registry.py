#!/usr/bin/env python3
"""Minimal task registry helper for Zoe."""

import json
from pathlib import Path
from datetime import datetime

REGISTRY = Path(__file__).parent.parent / "tasks_registry.json"


def load() -> dict:
    if not REGISTRY.exists():
        return {"version": 1, "tasks": []}
    return json.loads(REGISTRY.read_text())


def save(data: dict) -> None:
    REGISTRY.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def add_task(task_id: str, role: str, worktree: str, instruction: str) -> None:
    data = load()
    data["tasks"].append({
        "id": task_id,
        "role": role,
        "worktree": worktree,
        "instruction": instruction,
        "status": "running",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    })
    save(data)


def update_status(task_id: str, status: str, output: str = "") -> None:
    data = load()
    for t in data["tasks"]:
        if t["id"] == task_id:
            t["status"] = status
            t["updated_at"] = datetime.now().isoformat()
            if output:
                t["output"] = output
            break
    save(data)


def list_tasks() -> None:
    data = load()
    for t in data["tasks"]:
        print(f"{t['id']}: {t['status']} ({t['role']})")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: registry.py add|update|list ...")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "add" and len(sys.argv) >= 6:
        add_task(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif cmd == "update" and len(sys.argv) >= 4:
        update_status(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
    elif cmd == "list":
        list_tasks()
    else:
        print("Unknown command or missing args")
        sys.exit(1)
