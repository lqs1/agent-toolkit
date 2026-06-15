---
name: trellis-like
description: A lightweight, local alternative to the Trellis agent harness. Triggers a structured Plan → Spec → Implement → Check → Learn → Finish workflow for coding tasks, with artifacts persisted in .claude/trellis/.
---

# Trellis-like Workflow

This skill provides a lightweight, local alternative to the Trellis agent harness. It structures coding work into six phases and persists plans, specs, tasks, and learnings inside the project repository.

## When to Use

Use this skill when the user:

- Asks to plan or design a feature, fix, or refactor
- Wants a structured workflow similar to Trellis
- Needs to capture engineering decisions and lessons in the repo
- Wants explicit task tracking for multi-step work
- Says something like "trellis this", "plan this feature", "start a task", or "finish work"

## Core Workflow

Run the following six phases in order. Create/update Claude Code tasks for tracking.

### 1. Plan (`trellis-plan`)

When the user describes a feature, bug, or ambiguous request:

1. Ask clarifying questions if requirements are unclear (max 3).
2. Create a task with `TaskCreate`.
3. Generate `prd.md` from `templates/prd.md` (located in the skill's `templates/` directory) and save to `.claude/trellis/prd/<task-slug>.md`. The `{{TASK_TITLE}}` placeholders are replaced by Claude Code when generating the file.
4. Summarize the plan to the user and ask for confirmation before proceeding.

### 2. Before-Dev (`trellis-before-dev`)

Before writing code for an in-progress task:

1. Read `.claude/trellis/specs/` directory.
2. List relevant spec files for the package/domain being changed.
3. Summarize the key constraints, patterns, and decisions the user cares about.
4. **Resolve spec conflicts** using this priority chain: project-level `CLAUDE.md` > domain-specific spec (e.g., `auth.md`) > `architecture.md` > `conventions.md`. If two specs at the same level conflict, ask the user to choose.
5. Load these constraints into context before implementing.

### 3. Implement

Implement the feature/bugfix normally, respecting the PRD and specs. Update the task status with `TaskUpdate` as work progresses.

### 4. Check (`trellis-check`)

After implementation, before marking done:

1. Detect the project type and pick the default check commands. If multiple project types exist, use the priority order: project-level `trellis-check` script > `Makefile` target > most-specific config (e.g., `pyproject.toml` over `package.json` when both exist in a fullstack repo) > default table below.

   | Project Files | Type | Default Check Command |
   |---|---|---|
   | `package.json` | Node.js | `npm run lint && npm run test` |
   | `pyproject.toml` or `requirements.txt` | Python (conda) | `conda run -n <env> ruff check . && conda run -n <env> mypy . && conda run -n <env> pytest` |
   | `Cargo.toml` | Rust | `cargo check && cargo test` |
   | `go.mod` | Go | `go vet ./... && go test ./...` |
   | `pom.xml` / `build.gradle` | Java | `mvn test` / `./gradlew test` |
   | `Gemfile` | Ruby | `bundle exec rubocop && bundle exec rspec` |
   | `mix.exs` | Elixir | `mix format --check-formatted && mix test` |
   | `composer.json` | PHP | `composer lint && composer test` |
   | `*.csproj` / `*.sln` | C# | `dotnet test` |
   | `Package.swift` | Swift | `swift test` |

2. **Fallback strategy**: if a primary tool is missing (e.g., `ruff` not installed), fall back to the next available tool (`flake8`, then `python -m compileall`). If no check command can run, stop and report the blocker to the user rather than silently skipping checks.
3. **Security warning**: `trellis-check` may execute project-defined scripts. Review unknown scripts before running; Claude Code will prompt for Bash approval.
4. Run the project's quality checks (lint, typecheck, tests).
5. Record check results in the task's metadata (e.g., `check_passed=true`, `check_output=...`).
6. Review the diff for correctness, simplicity, and adherence to specs.
7. If issues are found, fix them or ask the user for guidance.
8. Do not mark the task complete until checks pass.

### 5. Update-Spec (`trellis-update-spec`)

When a new learning, decision, or gotcha emerges:

1. Identify the right spec file under `.claude/trellis/specs/` (or create one).
2. Append a concise entry documenting the learning.
3. Tell the user what was added.

### 6. Finish-Work (`trellis-finish-work`)

When the user confirms the task is done:

1. Verify checks have passed by reading the task metadata (`check_passed`). If not, run final checks.
2. Write a journal entry to `.claude/trellis/journal/<YYYY-MM-DD>_<task-slug>.md` from `templates/journal.md`.
3. Archive/move the task file from `.claude/trellis/tasks/` to `.claude/trellis/tasks/done/<YYYY-Qx>/`.
4. Mark the Claude Code task as `completed` with `TaskUpdate`.

## Error Recovery / Resume

If a task is interrupted (session crash, agent error, user stop):
1. Read the existing task file in `.claude/trellis/tasks/<task-slug>.md` and the PRD.
2. Read the Claude Code task status with `TaskGet`.
3. Resume from the last completed phase. Do not restart from Plan unless explicitly asked.
4. If a phase produced broken artifacts, create a new task branch or worktree before retrying.

## Git Strategy

`.claude/trellis/` contains project knowledge and should usually be committed. Add this to `.gitignore` only for files that are clearly temporary or machine-generated at runtime:

```gitignore
# Trellis runtime artifacts (keep prd/specs/journal/tasks committed)
.claude/trellis/.cache/
```

If your team prefers not to commit trellis artifacts, add `.claude/trellis/` to `.gitignore` and document that decision in the project README.

## Directory Structure

Create this structure inside the project root on first use:

```text
.claude/trellis/
├── prd/
├── specs/
│   ├── architecture.md
│   ├── conventions.md
│   └── <domain>.md
├── tasks/
│   └── done/
└── journal/
```

Use kebab-case for all file names.

## Constraints

- Never delete existing specs or journal entries.
- Keep PRDs under 300 lines; split large features into multiple PRDs by independent deliverable (e.g., one API endpoint, one component, one migration).
- Keep spec entries concise: **Context** ≤ 1 sentence, **Decision** ≤ 1 sentence, **Consequences** ≤ 5 bullets.
- Always run checks before finishing a task.
- Always update specs when a new reusable lesson is learned.
- `trellis-like` is designed for git-based projects.
