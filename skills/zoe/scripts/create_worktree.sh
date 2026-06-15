#!/usr/bin/env bash
set -euo pipefail

TASK_ID="${1:-}"
BASE_BRANCH="${2:-main}"

if [[ -z "$TASK_ID" ]]; then
  echo "Usage: $0 <task-id> [base-branch]" >&2
  exit 1
fi

WORKTREE_DIR="worktrees/${TASK_ID}"
mkdir -p worktrees

if git rev-parse --verify "${TASK_ID}" >/dev/null 2>&1; then
  # Branch already exists; just check it out as a worktree.
  git worktree add "${WORKTREE_DIR}" "${TASK_ID}"
else
  # Create a new branch and worktree from the base branch.
  git worktree add -b "${TASK_ID}" "${WORKTREE_DIR}" "${BASE_BRANCH}"
fi

# Return the absolute path so callers do not have to guess.
realpath "${WORKTREE_DIR}"
