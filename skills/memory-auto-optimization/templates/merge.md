# Merge Template

Use this template when consolidating two duplicate or semantically similar memory entries into a single, authoritative entry.

## Instructions

1. Read both source files carefully.
2. Decide which file path should be the canonical (merged) entry. Prefer the more descriptive file name and the path that is closer to the project root (project memory over global memory when both exist).
3. Combine the `name` and `description` fields. If they differ, choose the clearer one or synthesize a short, accurate summary.
4. Merge the body text. Eliminate redundancy, preserve all unique facts, and rewrite for clarity. Keep the result concise (under 300 lines total).
5. Retain any useful `metadata` from either source.
6. The old entries should be archived (moved to `.claude/memory/archive/`) after the merged entry is written.

## Template

```yaml
---
name: {{merged_name}}
description: {{merged_description}}
---

{{merged_body}}
```

## Fields

| Field | Guidance |
|-------|----------|
| `merged_name` | Prefer the clearer or more specific name. If both are similar, pick the kebab-case version that reads like a topic. |
| `merged_description` | One-sentence summary covering both original descriptions without redundancy. |
| `merged_body` | Unified body containing all unique facts from both sources, rewritten for clarity. Remove contradictions by choosing the newer or more authoritative statement. |

## Example

**Source A:** `user-preference.md`
```yaml
---
name: user-preference
description: User prefers dark mode
---

Always use dark mode in the UI.
```

**Source B:** `user_pref.md`
```yaml
---
name: user-pref
description: User likes dark mode
---

Always use dark mode in the UI. Also prefers high contrast.
```

**Merged:** `user-preference.md`
```yaml
---
name: user-preference
description: User prefers dark mode and high contrast
---

Always use dark mode in the UI with high contrast enabled.
```

After writing the merged file, archive `user_pref.md`.
