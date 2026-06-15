---
name: skill-router
description: Helps the user choose and invoke the right Claude Code skill when they are unsure which one to use, or when they say things like "which skill should I use", "what skills do I have", "help me pick a skill", or "I forgot my skills".
last_updated: 2026-06-15
---

# Skill Router

This skill acts as a directory and router for your available Claude Code skills. Use it when you are unsure which skill fits your current task.

## When to Use

Use this skill when the user:

- Asks "我该用哪个 skill"
- Says "我忘了有哪些 skill"
- Asks "which skill should I use"
- Says "help me pick a skill"
- Describes a task but does not explicitly name a skill
- Asks "你有哪些 skill"

## Available Skills Index

| Skill | Use When | Example Triggers | Boundaries / Limitations |
|---|---|---|---|
| `agent-browser` | 需要浏览器自动化、截图、填表、点击、抓取数据 | open website, screenshot, scrape, login to site | 无法处理需要复杂登录态保存的私有站点 |
| `capability-evolver` | 需要让 agent 自我进化、分析历史、改进能力 | evolve, self-improve, capability | 需要历史对话或日志作为输入 |
| `excel-automation` | 需要处理 Excel 文件、表格、数据 | excel, spreadsheet, xlsx | 不支持复杂的宏或 VBA 逆向 |
| `find-skills` | 想查找或安装市场上的 skill | find skill, install skill, skills.sh | 依赖外部 skill registry 可用性 |
| `memory-auto-optimization` | 想审计、清理、优化 memory 文件 | optimize memory, audit memory, clean memory | 仅分析，不自动修改 |
| `numina-ui-style` | 需要前端 UI 设计规范、仪表盘风格 | UI design, dashboard, neumorphism | 只出规范，不生成完整组件库 |
| `pdf-extraction` | 需要从 PDF 提取文本、表格、元数据 | extract pdf, pdf text, pdfplumber | 扫描版 PDF 识别能力有限 |
| `redteam-debate` | 需要红蓝队对抗辩论评估方案 | red team, debate, evaluate, critique, 挑毛病 | 多轮流程较重，小问题可能过度 |
| `security-review` | 需要安全审计、漏洞检查 | security review, XSS, injection, audit | 不能替代专业渗透测试 |
| `self-improvement` | 需要记录失败/纠正/学习 | learning, correction, mistake, improve | 需要用户明确反馈才能形成记忆 |
| `skill-vetter` | 安装新 skill 前检查安全性 | vet skill, is this skill safe | 静态检查，不能发现所有恶意行为 |
| `summarize` | 需要总结 URL、视频、文章、PDF | summarize, transcript, TL;DR | 长视频/长文档可能超出上下文 |
| `trellis-like` | 需要结构化规划-实现-检查-归档流程 | plan feature, trellis, finish work, check work | 小任务可能显得过重 |
| `universal-markdown-converter` | 需要 Markdown 与其他格式互转 | convert markdown, pandoc, docx, html | 依赖本地 pandoc 或其他工具 |
| `webapp-testing` | 需要测试本地 web 应用、截图、看日志 | test web app, playwright, screenshot UI | 需要应用已在运行 |
| `word-document-processor` | 需要创建/编辑 Word 文档 | word, docx, tracked changes | 复杂排版可能不完全精确 |
| `skill-router` | 不知道该用哪个 skill | which skill, 推荐 skill, 我忘了 | 依赖索引更新，可能不知道最新安装的 skill |

## How to Route

1. Listen to the user's request.
2. Match it against the table above.
3. If the table seems stale or the user mentions a skill not in the index, run the dynamic router:
   ```bash
   python3 /Users/qslu/personal/agent-toolkit/skills/skill-router/scripts/router.py "<user query>"
   ```
   This scans all SKILL.md files, parses frontmatter, and returns a ranked JSON list of top matches with scores and boundary notes. Use the output to include any unknown skill in the recommendation.
4. Recommend the best 1–3 skills with a one-sentence reason **and a one-sentence boundary/limitation** each.
5. Tell the user how to invoke each one:
   - Direct slash command: `/skill-name`
   - Natural language with trigger keywords
6. If the recommendation was wrong, ask the user to invoke `/self-improvement` to record the correction.
7. If no skill matches, say so and offer to help directly.

## Example Responses

**User**: "我想评估一下这个方案"
**Response**: "推荐用 `/redteam-debate` 进行红蓝队对抗辩论。它会组织红队挑刺、蓝队反驳、绿队出结论。注意：多轮流程较重，适合重要方案，小问题可能过度。直接输入 `/redteam-debate` 或告诉我你想评估什么。"

**User**: "我有哪些 skill 来着？"
**Response**: "你一共有 17 个 skill。最近常用的有...（列出相关项）"

## Maintenance Note

This index is a snapshot. When new skills are added:
1. Update this SKILL.md to include them.
2. Update `last_updated` in the frontmatter.
3. Run the dynamic scan above to catch skills not yet in the index.
