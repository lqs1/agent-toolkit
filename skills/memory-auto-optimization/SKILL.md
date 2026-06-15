---
name: memory-auto-optimization
description: Analyzes Claude Code memory files for duplicates, conflicts, stale entries, and vague entries. Generates a Markdown report and applies changes only with explicit user approval.
---

# Memory Auto-Optimization

This skill analyzes Claude Code memory files and suggests optimizations: merging duplicates, resolving conflicts, archiving stale entries, and improving vague entries.

## When to Use

Use this skill when the user:

- Says "optimize my memory", "clean up memory", "audit memory", or "memory auto-optimization"
- Has accumulated many memory entries and suspects duplicates or conflicts
- Wants to find outdated or low-quality memory entries
- Needs help extracting a new memory from the current conversation

## Workflow

### 1. Analyze

1. Identify the project memory directory: `.claude/memory/` relative to the current project root.
2. Identify the global memory directory: `~/.claude/projects/<project-key>/memory/` (where `<project-key>` is derived from the project path).
3. Run the analyzer script:
   ```bash
   python ~/.claude/skills/memory-auto-optimization/memory_optimizer.py \
       --project-dir <project-memory-dir> \
       --global-dir <global-memory-dir> \
       --output /tmp/memory-report.md
   ```
4. Read the report and present it to the user.

### 2. Review

Present the report sections in order:

1. **Duplicates** — semantically similar entries that could be merged.
2. **Conflicts** — entries that recommend opposing tools or practices.
3. **Potentially Stale** — entries mentioning temporary, deprecated, or old approaches.
4. **Vague Entries** — entries with too little actionable detail.

For each issue, explain the recommended action and ask for approval.

### 3. Apply (only with approval)

If the user approves a specific action:

- **Merge duplicates**: Create a new consolidated memory file, then archive the old ones.
- **Resolve conflicts**: Ask the user to choose the preferred recommendation, then update or archive the losing entry.
- **Archive stale**: Move the entry to `.claude/memory/archive/` or append `ARCHIVED` to the file name.
- **Improve vague**: Ask the user for more detail and rewrite the entry.

There is no automated "apply mode" in the analyzer; all changes are made manually by the orchestrator with explicit user approval. Never modify memory files without explicit user approval.

### 4. Suggest New Memory

After analyzing existing memory, review the current conversation for:

- User corrections ("No, always do X instead")
- Confirmed preferences ("Yes, that's the right way")
- Important project decisions

If found, suggest 1–3 new memory entries using the standard frontmatter format and ask before writing them.

## Constraints

- Default to dry-run analysis; do not write or delete files unless approved.
- Project memory and global memory are analyzed separately in the report.
- Keep all memory files under 300 lines; split if necessary.
- Use kebab-case for memory file names.
- Preserve the standard memory frontmatter format (`name`, `description`, `metadata`).

## Example Invocation

```bash
/trellis:memory-auto-optimization
```

Or in natural language:

> "Please audit my memory files for duplicates and conflicts."
