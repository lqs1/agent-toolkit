# Agent Toolkit

Personal collection of AI agent skills and roles for Claude Code and similar agentic coding environments.

## Structure

```
.
├── skills/          # Claude Code skill packages
│   ├── skill-router
│   ├── redteam-debate
│   ├── memory-auto-optimization
│   ├── numina-ui-style
│   └── project-check
├── roles/           # Specialist agent role definitions
│   ├── analyst.md
│   ├── architect.md
│   ├── backend_dev.md
│   ├── frontend_dev.md
│   ├── security_auditor.md
│   ├── db_designer.md
│   ├── tech_writer.md
│   ├── qa_engineer.md
│   └── devops.md
└── debate/          # Red-team debate analysis outputs
```

## Skills

| Skill | Purpose | Trigger Words |
|---|---|---|
| `skill-router` | Recommend the right skill for a task | "which skill", "help me pick", "我忘了有哪些 skill" |
| `redteam-debate` | Structured red/blue/green debate evaluation | "red team", "debate", "挑毛病", "评估", "审视" |
| `memory-auto-optimization` | Analyze memory files for duplicates/conflicts/stale entries | "optimize memory", "清理 memory", "审计 memory" |
| `numina-ui-style` | UI design system for dashboards (neumorphism + tech effects) | "UI design", "dashboard", "科技感", "拟态" |
| `project-check` | Auto-detect project type and run lint/type-check/tests | "check code", "run tests", "代码检查", "跑测试" |

## Installation

To make a skill globally available in Claude Code, copy or symlink it into `~/.claude/skills/`:

```bash
ln -s "$PWD/skills/skill-router" ~/.claude/skills/skill-router
```

## Status

This is a personal toolkit. Skills are updated iteratively; the `~/.claude/skills/` directory is the live source of truth for local usage.

## License

MIT
