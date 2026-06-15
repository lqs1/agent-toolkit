#!/usr/bin/env bash
# trellis-doctor.sh — Validate .claude/trellis/ structure and task phase metadata.

set -uo pipefail

REPO_ROOT="${1:-.}"
TRELLIS="$REPO_ROOT/.claude/trellis"
ERRORS=0

log() { echo "[trellis-doctor] $*"; }

if [[ ! -d "$TRELLIS" ]]; then
  log "✗ .claude/trellis/ directory not found. Run trellis-plan first."
  exit 1
fi

for dir in prd specs tasks journal; do
  if [[ ! -d "$TRELLIS/$dir" ]]; then
    log "✗ Missing directory: $TRELLIS/$dir"
    ERRORS=$((ERRORS + 1))
  else
    log "✓ Directory exists: $TRELLIS/$dir"
  fi
done

# Validate task files have required frontmatter
for task in "$TRELLIS"/tasks/*.md; do
  [[ -e "$task" ]] || continue
  if ! grep -qE "^status:" "$task"; then
    log "✗ Task file missing 'status' frontmatter: $task"
    ERRORS=$((ERRORS + 1))
  fi
  if ! grep -qE "^phase:" "$task"; then
    log "⚠ Task file missing 'phase' frontmatter (optional but recommended): $task"
  fi
done

# Validate specs
for spec in "$TRELLIS"/specs/*.md; do
  [[ -e "$spec" ]] || continue
  if ! grep -qE "^status:" "$spec"; then
    log "⚠ Spec missing 'status' frontmatter: $spec"
  fi
done

# Check gitignore recommendation
if [[ -f "$REPO_ROOT/.gitignore" ]]; then
  if grep -q ".claude/trellis/.cache" "$REPO_ROOT/.gitignore"; then
    log "✓ .gitignore excludes trellis runtime cache"
  else
    log "⚠ Consider adding '.claude/trellis/.cache/' to .gitignore"
  fi
fi

if [[ $ERRORS -gt 0 ]]; then
  log "Found $ERRORS error(s). Fix before proceeding."
  exit 1
fi

log "All checks passed."
exit 0
