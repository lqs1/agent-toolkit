#!/usr/bin/env bash
# trellis.sh — Unified CLI entry point for the trellis-like workflow.
# Usage: trellis.sh <command> [args]
#
# Commands:
#   plan <task-slug>   Ensure .claude/trellis/ exists and create a task file.
#   check              Delegate to trellis-check.sh.
#   doctor             Delegate to trellis-doctor.sh.
#   finish <task-slug> Archive a task file to .claude/trellis/tasks/done/<YYYY-Qx>/.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="${TRELLIS_REPO_ROOT:-.}"
TRELLIS="$REPO_ROOT/.claude/trellis"

log() { echo "[trellis] $*"; }

usage() {
  cat <<EOF
Usage: $(basename "$0") <command> [args]

Commands:
  plan <task-slug>   Create task file and ensure directory structure.
  check              Run project quality checks (delegates to trellis-check.sh).
  doctor             Validate trellis structure (delegates to trellis-doctor.sh).
  finish <task-slug> Archive completed task to done/<YYYY-Qx>/.

Environment:
  TRELLIS_REPO_ROOT  Repo root to operate on (default: current directory).
EOF
  exit 1
}

# Ensure .claude/trellis/ directory structure exists.
ensure_structure() {
  for dir in prd specs tasks tasks/done journal; do
    if [[ ! -d "$TRELLIS/$dir" ]]; then
      mkdir -p "$TRELLIS/$dir"
      log "Created directory: $TRELLIS/$dir"
    fi
  done
}

# Replace template placeholders with actual values.
render_template() {
  local slug="$1"
  local title="$2"
  local date="$3"
  sed -e "s/{{TASK_SLUG}}/$slug/g" \
      -e "s/{{TASK_TITLE}}/$title/g" \
      -e "s/{{YYYY-MM-DD}}/$date/g"
}

# plan <task-slug>
cmd_plan() {
  local slug="${1:-}"
  if [[ -z "$slug" ]]; then
    log "Error: task-slug required for plan."
    usage
  fi

  ensure_structure

  local task_file="$TRELLIS/tasks/$slug.md"
  if [[ -f "$task_file" ]]; then
    log "Task file already exists: $task_file"
    return 0
  fi

  local template="$SKILL_DIR/templates/task.md"
  if [[ ! -f "$template" ]]; then
    log "Error: template not found: $template"
    exit 1
  fi

  local date
  date="$(date +%Y-%m-%d)"
  render_template "$slug" "$slug" "$date" < "$template" > "$task_file"
  log "Created task file: $task_file"
}

# check
cmd_check() {
  bash "$SCRIPT_DIR/trellis-check.sh" "$REPO_ROOT"
}

# doctor
cmd_doctor() {
  bash "$SCRIPT_DIR/trellis-doctor.sh" "$REPO_ROOT"
}

# finish <task-slug>
cmd_finish() {
  local slug="${1:-}"
  if [[ -z "$slug" ]]; then
    log "Error: task-slug required for finish."
    usage
  fi

  local task_file="$TRELLIS/tasks/$slug.md"
  if [[ ! -f "$task_file" ]]; then
    log "Error: task file not found: $task_file"
    exit 1
  fi

  local year quarter dest_dir dest_file
  year="$(date +%Y)"
  quarter="Q$(( ($(date +%m) - 1) / 3 + 1 ))"
  dest_dir="$TRELLIS/tasks/done/${year}-${quarter}"
  dest_file="$dest_dir/$slug.md"

  mkdir -p "$dest_dir"
  mv "$task_file" "$dest_file"
  log "Archived task to: $dest_file"
}

# Main dispatch
COMMAND="${1:-}"
shift || true

case "$COMMAND" in
  plan)   cmd_plan "$@" ;;
  check)  cmd_check "$@" ;;
  doctor) cmd_doctor "$@" ;;
  finish) cmd_finish "$@" ;;
  *)      usage ;;
esac
