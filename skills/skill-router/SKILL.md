---
name: skill-router
description: Helps the user choose and invoke the right Claude Code skill when they are unsure which one to use, or when they say things like "which skill should I use", "what skills do I have", "help me pick a skill", or "I forgot my skills".
last_updated: 2026-06-15
---

# Skill Router

当用户不确定该用哪个 skill 时，动态扫描并语义匹配。

## 路由方法

1. **扫描**：用 Glob 工具匹配 `~/.claude/skills/*/SKILL.md`
2. **读取**：读取每个 SKILL.md 的 frontmatter（name + description 字段）
3. **语义匹配**：基于用户意图，结合 description 中的触发词和使用场景，推荐 1-3 个最合适的 skill
4. **输出格式**：每个推荐附带一句话推荐理由 + 一句话局限性
5. **调用**：告诉用户如何调用（`/skill-name` 或自然语言触发）

## 规则

- **不维护静态索引表**，每次动态扫描，新 skill 自动发现
- 如果没有匹配的 skill，直接帮忙，不要硬塞不相关的 skill
- 如果推荐错误，建议用户调用 `/self-improvement` 记录纠正
- 中文查询和英文查询同等对待

## 示例

**用户**: "帮我审视一下这个架构决策"
**推荐**: `/redteam-debate` — 红蓝队对抗辩论，深度评估方案。注意：多轮流程较重，适合重要方案。

**用户**: "我想让仪表盘界面有科技感"
**推荐**: `/numina-ui-style` — 深色 sidebar+拟态浅色内容区+科技感动效的 UI 设计规范。注意：只出规范，不生成完整组件库。
