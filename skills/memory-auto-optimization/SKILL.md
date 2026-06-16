---
name: memory-auto-optimization
description: Analyzes Claude Code memory files for duplicates, conflicts, stale entries, and vague entries. Generates recommendations and applies changes only with explicit user approval.
---

# Memory Auto-Optimization

分析 Claude Code memory 文件，发现重复、冲突、过时和模糊条目，提出优化建议。

## 何时使用

- 用户说 "优化 memory"、"清理 memory"、"审计 memory"
- 怀疑 memory 有重复或冲突条目
- 想找出过时或低质量的 memory

## 分析步骤

1. **扫描**：Read 项目的 `.claude/memory/` 和全局的 `~/.claude/projects/<key>/memory/` 下所有 `.md` 文件
2. **分析**（纯语义判断，无需脚本）：
   - **重复**：语义相似的条目 → 建议合并
   - **冲突**：推荐了相反工具/做法的条目 → 建议二选一
   - **过时**：提到临时、已废弃、旧方案的条目 → 建议归档
   - **模糊**：body 内容太短、缺少可操作细节的条目 → 建议补充
3. **展示**：按以上分类呈现分析结果，每个问题附带建议操作
4. **执行**（仅在用户明确批准后）：
   - 合并：写新的合并条目，归档旧的
   - 冲突：让用户选择，归档落选的
   - 过时：移动到 `archive/` 子目录
   - 模糊：让用户补充后重写
5. **建议新 memory**：检查当前对话中是否有用户纠正或确认的偏好，建议 1-3 条新 memory

## 规则

- 默认 dry-run，不写不删，除非用户批准
- 保持所有 memory 文件 < 300 行
- 保持 kebab-case 文件名
- 保留标准 frontmatter 格式（name, description, metadata）
