# Agent Toolkit

Personal collection of AI agent skills, roles, and orchestration patterns for Claude Code, Codex, and similar agentic coding environments.

## Structure

```
.
├── skills/          # Claude Code skill packages
│   └── zoe/         # Multi-agent orchestrator
└── roles/           # Specialist agent role definitions
    ├── zoe.md       # Orchestrator system prompt
    ├── analyst.md
    ├── architect.md
    ├── backend_dev.md
    ├── frontend_dev.md
    ├── security_auditor.md
    ├── db_designer.md
    ├── tech_writer.md
    ├── qa_engineer.md
    └── devops.md
```

## Skills

### Zoe

Zoe is a multi-agent orchestrator that decomposes software development tasks and dispatches them to specialized agents in isolated git worktrees.

**Trigger words:** `Zoe`, `agent swarm`, `parallel agents`, `spawn agents`, `multi-agent orchestration`, `one-person dev team`, `AI team`

**Usage:**

```
Zoe, implement a user authentication API with tests and documentation.
```

## Installation

To make a skill globally available in Claude Code, copy or symlink it into `~/.claude/skills/`:

```bash
ln -s "$PWD/skills/zoe" ~/.claude/skills/zoe
```

## Status

This is the first committed version (v0.1.0). Expect rough edges and missing automation scripts. A red-team review of all skills is planned.

## License

MIT
