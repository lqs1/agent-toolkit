#!/usr/bin/env python3
"""Test suite for zoe orchestrator lifecycle state machine."""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

# Ensure orchestrator module is importable
sys.path.insert(0, str(Path(__file__).parent))

import orchestrator as orch


def setup_module():
    """Reset registry to a known empty state before tests."""
    orch.REGISTRY.write_text(json.dumps({"version": 1, "tasks": []}, indent=2))


def teardown_module():
    """Clean up registry after tests."""
    if orch.REGISTRY.exists():
        orch.REGISTRY.unlink()


def reset_registry():
    """Helper to reset registry between tests."""
    orch.REGISTRY.write_text(json.dumps({"version": 1, "tasks": []}, indent=2))


def test_enqueue_adds_pending_task():
    reset_registry()
    orch.enqueue("task-1", "backend_dev", "/wt/1", "build auth API")
    data = orch._load()
    assert len(data["tasks"]) == 1
    t = data["tasks"][0]
    assert t["id"] == "task-1"
    assert t["role"] == "backend_dev"
    assert t["worktree"] == "/wt/1"
    assert t["instruction"] == "build auth API"
    assert t["status"] == "pending"
    assert "created_at" in t
    assert "updated_at" in t


def test_start_next_promotes_pending_to_running():
    reset_registry()
    orch.enqueue("task-1", "backend_dev", "/wt/1", "build auth API")
    orch.start_next()
    data = orch._load()
    t = data["tasks"][0]
    assert t["status"] == "running"


def test_start_next_respects_max_concurrent():
    reset_registry()
    with mock.patch.dict(os.environ, {"ZOE_MAX_CONCURRENT": "2"}):
        orch.enqueue("task-1", "backend_dev", "/wt/1", "a")
        orch.enqueue("task-2", "backend_dev", "/wt/2", "b")
        orch.enqueue("task-3", "backend_dev", "/wt/3", "c")
        orch.start_next()
        data = orch._load()
        statuses = {t["id"]: t["status"] for t in data["tasks"]}
        assert statuses["task-1"] == "running"
        assert statuses["task-2"] == "running"
        assert statuses["task-3"] == "pending"


def test_mark_updates_status_and_output():
    reset_registry()
    orch.enqueue("task-1", "backend_dev", "/wt/1", "a")
    orch.start_next()
    orch.mark("task-1", "finished", "all good")
    data = orch._load()
    t = data["tasks"][0]
    assert t["status"] == "finished"
    assert t["output"] == "all good"
    assert "updated_at" in t


def test_can_spawn_when_under_limit():
    reset_registry()
    with mock.patch.dict(os.environ, {"ZOE_MAX_CONCURRENT": "2"}):
        assert orch.can_spawn() is True
        orch.enqueue("task-1", "backend_dev", "/wt/1", "a")
        orch.start_next()
        assert orch.can_spawn() is True
        orch.enqueue("task-2", "backend_dev", "/wt/2", "b")
        orch.start_next()
        assert orch.can_spawn() is False


def test_summary_counts():
    reset_registry()
    orch.enqueue("task-1", "backend_dev", "/wt/1", "a")
    orch.enqueue("task-2", "backend_dev", "/wt/2", "b")
    orch.enqueue("task-3", "backend_dev", "/wt/3", "c")
    orch.start_next()  # starts task-1 (default limit 3)
    orch.mark("task-1", "finished", "done")
    orch.mark("task-2", "failed", "oops")
    counts = orch._summary_counts()
    assert counts == {"running": 0, "finished": 1, "failed": 1, "pending": 1}


def test_cli_enqueue():
    reset_registry()
    sys.argv = ["orchestrator.py", "enqueue", "task-1", "backend_dev", "/wt/1", "build auth API"]
    orch.main()
    data = orch._load()
    assert any(t["id"] == "task-1" for t in data["tasks"])


def test_cli_summary():
    reset_registry()
    orch.enqueue("task-1", "backend_dev", "/wt/1", "a")
    orch.start_next()
    orch.mark("task-1", "finished", "done")
    sys.argv = ["orchestrator.py", "summary"]
    orch.main()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
