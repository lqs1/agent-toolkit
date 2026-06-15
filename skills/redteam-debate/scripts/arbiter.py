#!/usr/bin/env python3
"""Arbiter scoring module for redteam-debate unresolved issues."""

import json
import re
import sys
from pathlib import Path

# Severity keyword mapping (case-insensitive)
SEVERITY_KEYWORDS = {
    "critical": ["data loss", "security breach", "crash", "deadlock", "indefinite"],
    "high": ["security", "broken", "wrong", "corrupt", "leakage", "rollback"],
    "medium": ["race", "concurrency", "retry", "missing", "gap", "blind spot"],
    "low": ["cleanup", "trivial", "documentation", "naming"],
}

CATEGORY_KEYWORDS = {
    "security": ["security", "sandbox", "leakage", "breach", "auth", "injection"],
    "correctness": ["wrong", "broken", "bug", "corrupt", "race", "deadlock", "retry"],
    "maintainability": ["cleanup", "documentation", "naming", "modular"],
    "ux": ["usability", "user experience", "confusing", "unclear"],
    "performance": ["performance", "slow", "latency", "throughput", "memory leak"],
}


def _score_severity(text: str) -> str:
    text_lower = text.lower()
    for sev, keywords in SEVERITY_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return sev
    return "medium"


def _score_confidence(text: str) -> float:
    """Heuristic: specificity = named entities, numbers, file paths, concrete scenarios."""
    score = 0.5
    # Concrete indicators
    if re.search(r"\.[a-zA-Z]+", text):  # file extension or path
        score += 0.15
    if re.search(r"[A-Z_]+[A-Z]", text):  # constant / env var
        score += 0.1
    if re.search(r"\d+", text):  # numbers
        score += 0.1
    if len(text.split()) > 15:  # detailed description
        score += 0.1
    if "example" in text.lower() or "e.g." in text.lower():
        score += 0.05
    return min(1.0, round(score, 2))


def _classify(text: str) -> str:
    text_lower = text.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return cat
    return "other"


SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def load_unresolved(path: Path) -> list[dict]:
    data = json.loads(path.read_text())
    unresolved = []
    for r in data.get("rounds", []):
        resolved = r.get("resolved") or []
        red_points = r.get("red_points", [])
        for i, (point, ok) in enumerate(zip(red_points, resolved)):
            if not ok:
                item = {
                    "point": point,
                    "round": r.get("round", 0),
                    "severity": _score_severity(point),
                    "confidence": _score_confidence(point),
                    "category": _classify(point),
                }
                # Respect existing metadata if present
                meta = r.get("metadata")
                if isinstance(meta, dict):
                    for key in ("severity", "confidence", "category"):
                        if key in meta:
                            item[key] = meta[key]
                unresolved.append(item)
    return unresolved


def generate_report(unresolved: list[dict], topic: str) -> str:
    unresolved.sort(key=lambda x: (SEVERITY_ORDER.get(x["severity"], 2), -x["confidence"]))

    lines = [
        "# Arbiter Verdict Report",
        f"**Topic:** {topic}",
        f"**Unresolved Issues:** {len(unresolved)}",
        "",
        "## Severity-Sorted Issues",
        "",
    ]

    current_sev = None
    for item in unresolved:
        sev = item["severity"]
        if sev != current_sev:
            lines.append(f"### {sev.upper()}")
            current_sev = sev
        lines.append(
            f"- **R{item['round']}** [{item['category']}] "
            f"(confidence {item['confidence']}) — {item['point']}"
        )

    lines.extend([
        "",
        "## Top 3 Recommended Actions",
        "",
    ])

    for i, item in enumerate(unresolved[:3], 1):
        lines.append(
            f"{i}. **[{item['severity'].upper()}]** {item['point']} "
            f"(category: {item['category']}, confidence: {item['confidence']})"
        )

    if len(unresolved) > 3:
        lines.append(f"\n*And {len(unresolved) - 3} additional issues — see full list above.*")

    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: arbiter.py <debate_state.json>", file=sys.stderr)
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(path.read_text())
    topic = data.get("topic", "Unknown")
    unresolved = load_unresolved(path)
    report = generate_report(unresolved, topic)
    print(report)


if __name__ == "__main__":
    main()
