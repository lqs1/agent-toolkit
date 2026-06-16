---
name: project-check
description: Auto-detect project type (Python/Node/Rust/Go/Java/Ruby/Elixir/PHP/C#/Swift) and run appropriate lint, type-check, and test commands. Use when asked to "check code", "run lint", "run tests", "quality check", "项目检查", "跑测试", "代码检查".
---

# Project Check

自动检测项目类型并运行对应的质量检查。

## 使用

```bash
bash ~/.claude/skills/project-check/scripts/check.sh [repo-root]
```

## 支持的项目类型

| 类型 | 检测文件 | 检查命令 |
|------|---------|---------|
| Python | pyproject.toml / requirements.txt | ruff / flake8 → mypy → pytest |
| Node | package.json | npm lint → npm test |
| Rust | Cargo.toml | cargo check → cargo test |
| Go | go.mod | go vet → go test |
| Java | pom.xml / build.gradle | mvn test / gradlew test |
| Ruby | Gemfile | rubocop → rspec |
| Elixir | mix.exs | mix format --check → mix test |
| PHP | composer.json | composer lint → composer test |
| C# | *.csproj / *.sln | dotnet test |
| Swift | Package.swift | swift test |

## 规则

- 项目级 `scripts/trellis-check` 或 Makefile `trellis-check` target 优先
- 支持 conda 环境：自动检测 environment.yml 中的环境名
- 未检测到任何项目类型时静默退出
