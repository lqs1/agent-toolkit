#!/usr/bin/env bash
set -euo pipefail

REGISTRY="${1:-tasks_registry.json}"

if [[ ! -f "$REGISTRY" ]]; then
  echo "No registry found at ${REGISTRY}" >&2
  exit 0
fi

python3 - "$REGISTRY" <<'PY'
import json
import sys
from pathlib import Path

reg = Path(sys.argv[1])
if not reg.exists():
    print("Registry file does not exist.")
    sys.exit(0)

try:
    data = json.loads(reg.read_text())
except json.JSONDecodeError as e:
    print(f"Invalid registry JSON: {e}")
    sys.exit(1)

tasks = data.get("tasks", [])
if not tasks:
    print("No tasks in registry.")
    sys.exit(0)

print(f"{'ID':<24} {'ROLE':<18} {'STATUS':<12} {'WORKTREE'}")
print("-" * 80)
for t in tasks:
    print(f"{t.get('id',''):<24} {t.get('role',''):<18} {t.get('status',''):<12} {t.get('worktree','')}")
PY
