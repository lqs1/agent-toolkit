#!/usr/bin/env python3
"""Dynamic skill router scorer.

Scans ~/.claude/skills/ and <repo>/.claude/skills/ for SKILL.md files,
parses YAML frontmatter, and ranks skills by relevance to a user query.
"""

import json
import os
import re
import sys
from pathlib import Path


def find_skill_dirs() -> list[Path]:
    """Return all skill directories containing a SKILL.md file."""
    dirs: list[Path] = []
    for base in (
        Path.home() / ".claude" / "skills",
        Path.cwd() / ".claude" / "skills",
    ):
        if not base.exists():
            continue
        for sub in base.iterdir():
            if sub.is_dir() and (sub / "SKILL.md").exists():
                dirs.append(sub)
    return dirs


def parse_frontmatter(text: str) -> dict:
    """Parse YAML-like frontmatter from a SKILL.md file."""
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    fm = text[3:end].strip()
    data: dict = {}
    current_key = None
    current_list: list[str] = []
    for line in fm.splitlines():
        stripped = line.rstrip()
        if stripped.startswith("- "):
            current_list.append(stripped[2:].strip().strip('"').strip("'"))
            continue
        if current_key and current_list:
            data[current_key] = current_list
            current_list = []
            current_key = None
        if ":" not in stripped:
            continue
        key, _, val = stripped.partition(":")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if val:
            data[key] = val
        else:
            current_key = key
    if current_key and current_list:
        data[current_key] = current_list
    return data


def tokenize(text: str) -> set[str]:
    """Lowercase and extract alphanumeric tokens."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def score_skill(query: str, meta: dict) -> float:
    """Compute a simple relevance score for a skill."""
    q_tokens = tokenize(query)
    if not q_tokens:
        return 0.0

    desc = meta.get("description", "")
    name = meta.get("name", "")
    tags = meta.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]

    desc_tokens = tokenize(desc)
    name_tokens = tokenize(name)
    tag_tokens = set()
    for t in tags:
        tag_tokens.update(tokenize(str(t)))

    # Jaccard on description
    inter = len(q_tokens & desc_tokens)
    union = len(q_tokens | desc_tokens) or 1
    score = 2.0 * (inter / union)

    # Exact name matches
    for tok in q_tokens:
        if tok in name_tokens:
            score += 1.5

    # Tag matches
    for tok in q_tokens:
        if tok in tag_tokens:
            score += 1.0

    # Substring bonus for exact phrases in description
    q_lower = query.lower()
    if q_lower in desc.lower():
        score += 2.0
    if q_lower in name.lower():
        score += 2.0

    # Trigger-word bonus: if any query token appears in a trigger phrase
    trigger_words = {"screenshot", "browser", "scrape", "login", "click", "form",
                     "extract", "pdf", "summarize", "transcribe", "convert",
                     "excel", "word", "security", "audit", "debate", "red team"}
    for tok in q_tokens:
        if tok in trigger_words and tok in desc.lower():
            score += 1.0

    return round(score, 3)


def _boundary_from_text(text: str, header: str) -> str:
    idx = text.find(header)
    if idx == -1:
        return ""
    snippet = text[idx + len(header):idx + 300]
    lines = [l.strip("- ").strip() for l in snippet.splitlines() if l.strip()][1:4]
    return " ".join(lines)


def boundary_note(meta: dict) -> str:
    """Return a short boundary/limitation note if available."""
    text = meta.get("_raw", "")
    for header in ("## Limitations", "## Boundaries"):
        note = _boundary_from_text(text, header)
        if note:
            return note
    return ""


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: router.py <query>", file=sys.stderr)
        sys.exit(1)

    query = sys.argv[1]
    dirs = find_skill_dirs()
    results: list[dict] = []

    for d in dirs:
        path = d / "SKILL.md"
        raw = path.read_text(encoding="utf-8")
        meta = parse_frontmatter(raw)
        if not meta or not meta.get("name"):
            continue
        meta["_raw"] = raw
        score = score_skill(query, meta)
        if score > 0:
            results.append(
                {
                    "name": meta.get("name"),
                    "description": meta.get("description", "")[:200],
                    "score": score,
                    "boundary": boundary_note(meta) or "See SKILL.md for limitations.",
                }
            )

    results.sort(key=lambda x: x["score"], reverse=True)
    print(json.dumps(results[:3], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
