#!/usr/bin/env python3
"""Memory auto-optimization analyzer for Claude Code memory files."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class MemoryEntry:
    """A single memory entry parsed from a Markdown file."""

    path: Path
    name: str
    description: str
    body: str

    @property
    def text(self) -> str:
        """Return normalized text for comparison."""
        return f"{self.name} {self.description} {self.body}".lower()


def parse_memory_file(path: Path) -> MemoryEntry | None:
    """Parse a memory markdown file and return a MemoryEntry."""
    content = path.read_text(encoding="utf-8")
    name_match = re.search(r"^name:\s*(.+)$", content, re.MULTILINE)
    desc_match = re.search(r"^description:\s*(.+)$", content, re.MULTILINE)
    if not name_match:
        return None

    name = name_match.group(1).strip()
    description = desc_match.group(1).strip() if desc_match else ""
    body = re.sub(r"^---\n.*?^---\n", "", content, flags=re.DOTALL | re.MULTILINE)
    return MemoryEntry(path=path, name=name, description=description, body=body.strip())


def scan_directory(directory: Path) -> list[MemoryEntry]:
    """Scan a directory for memory markdown files, excluding archive subdirs."""
    if not directory.exists():
        return []
    entries: list[MemoryEntry] = []
    for path in sorted(directory.rglob("*.md")):
        # Skip archive directories and common backup/preview files.
        if "/archive/" in str(path) or path.name.startswith("~") or path.name.endswith(".md.bak"):
            continue
        try:
            entry = parse_memory_file(path)
        except PermissionError:
            continue
        if entry:
            entries.append(entry)
    return entries


def scan_directory_excluding_archive(directory: Path) -> list[MemoryEntry]:
    """Scan a directory for memory markdown files, explicitly excluding .claude/memory/archive/."""
    if not directory.exists():
        return []
    entries: list[MemoryEntry] = []
    for path in sorted(directory.rglob("*.md")):
        # Skip any path under an archive/ directory
        if any(part == "archive" for part in path.relative_to(directory).parts[:-1]):
            continue
        if path.name.startswith("~") or path.name.endswith(".md.bak"):
            continue
        try:
            entry = parse_memory_file(path)
        except PermissionError:
            continue
        if entry:
            entries.append(entry)
    return entries


def tokenize(text: str) -> set[str]:
    """Return a set of meaningful words from text."""
    stopwords = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "shall",
        "can",
        "need",
        "dare",
        "ought",
        "used",
        "to",
        "of",
        "in",
        "for",
        "on",
        "with",
        "at",
        "by",
        "from",
        "as",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "and",
        "but",
        "or",
        "yet",
        "so",
        "if",
        "because",
        "although",
        "this",
        "that",
        "these",
        "those",
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
        "them",
        "their",
        "there",
        "then",
        "than",
    }
    words = re.findall(r"\w+", text.lower(), flags=re.UNICODE)
    return {w for w in words if len(w) > 1 and w not in stopwords}


def jaccard_similarity(a: str, b: str) -> float:
    """Compute Jaccard similarity between two texts."""
    tokens_a = tokenize(a)
    tokens_b = tokenize(b)
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = len(tokens_a & tokens_b)
    union = len(tokens_a | tokens_b)
    return intersection / union if union else 0.0


def find_duplicates(
    entries: list[MemoryEntry], threshold: float = 0.6
) -> list[tuple[MemoryEntry, MemoryEntry, float]]:
    """Find pairs of memory entries that are semantically similar."""
    duplicates: list[tuple[MemoryEntry, MemoryEntry, float]] = []
    for i, left in enumerate(entries):
        for right in entries[i + 1 :]:
            similarity = jaccard_similarity(left.text, right.text)
            if similarity >= threshold:
                duplicates.append((left, right, similarity))
    return duplicates


CONFLICT_PAIRS: tuple[tuple[set[str], set[str], str], ...] = (
    ({"venv", "virtualenv", "pipenv"}, {"conda"}, "environment tool conflict"),
    ({"pytest"}, {"unittest"}, "testing framework conflict"),
    ({"ruff"}, {"black", "flake8", "pylint"}, "linting tool conflict"),
    ({"mypy"}, {"pyright"}, "type checker conflict"),
    ({"fastapi"}, {"django", "flask"}, "web framework conflict"),
    ({"docker"}, {"kubernetes"}, "deployment platform conflict"),
)


def find_conflicts(
    entries: list[MemoryEntry],
) -> list[tuple[MemoryEntry, MemoryEntry, str]]:
    """Find memory entries with conflicting recommendations."""
    conflicts: list[tuple[MemoryEntry, MemoryEntry, str]] = []
    for i, left in enumerate(entries):
        left_tokens = tokenize(left.text)
        for right in entries[i + 1 :]:
            right_tokens = tokenize(right.text)
            for set_a, set_b, reason in CONFLICT_PAIRS:
                if (left_tokens & set_a and right_tokens & set_b) or (
                    left_tokens & set_b and right_tokens & set_a
                ):
                    conflicts.append((left, right, reason))
    return conflicts


STALE_KEYWORDS = {
    "temporary",
    "temp",
    "deprecated",
    "old",
    "previous",
    "before",
    "was using",
    "no longer",
    "used to",
    " outdated",
    "legacy",
    " abandoned",
    "experiment",
    "实验",
    "临时",
    "旧的",
    "已废弃",
}


def find_stale(entries: list[MemoryEntry]) -> list[MemoryEntry]:
    """Find memory entries that may be outdated."""
    return [
        entry for entry in entries if any(kw in entry.text for kw in STALE_KEYWORDS)
    ]


def find_vague(
    entries: list[MemoryEntry], min_body_words: int = 15
) -> list[MemoryEntry]:
    """Find memory entries that lack actionable detail."""
    vague: list[MemoryEntry] = []
    for entry in entries:
        body_words = len(tokenize(entry.body))
        if body_words < min_body_words:
            vague.append(entry)
    return vague


def generate_report(
    project_dir: Path,
    global_dir: Path,
    duplicates: list[tuple[MemoryEntry, MemoryEntry, float]],
    conflicts: list[tuple[MemoryEntry, MemoryEntry, str]],
    stale_entries: list[MemoryEntry],
    vague_entries: list[MemoryEntry],
) -> str:
    """Generate a Markdown optimization report."""
    lines: list[str] = ["# Memory Auto-Optimization Report\n"]
    lines.append(f"- Project memory: `{project_dir}`")
    lines.append(f"- Global memory: `{global_dir}`\n")

    lines.append(f"## Duplicates ({len(duplicates)})\n")
    if duplicates:
        for left, right, score in duplicates:
            lines.append(
                f"- **{left.name}** ↔ **{right.name}** (similarity: {score:.2f})"
            )
            lines.append(f"  - `{left.path}`")
            lines.append(f"  - `{right.path}`")
            lines.append("  - **Suggestion**: Merge into a single entry.\n")
    else:
        lines.append("No duplicate entries detected.\n")

    lines.append(f"## Conflicts ({len(conflicts)})\n")
    if conflicts:
        for left, right, reason in conflicts:
            lines.append(f"- **{left.name}** ↔ **{right.name}**")
            lines.append(f"  - Reason: {reason}")
            lines.append(
                "  - **Suggestion**: Review and reconcile the two recommendations.\n"
            )
    else:
        lines.append("No conflicting entries detected.\n")

    lines.append(f"## Potentially Stale ({len(stale_entries)})\n")
    if stale_entries:
        for entry in stale_entries:
            lines.append(f"- **{entry.name}** (`{entry.path}`)")
            lines.append("  - **Suggestion**: Verify relevance; archive if outdated.\n")
    else:
        lines.append("No stale entries detected.\n")

    lines.append(f"## Vague Entries ({len(vague_entries)})\n")
    if vague_entries:
        for entry in vague_entries:
            lines.append(f"- **{entry.name}** (`{entry.path}`)")
            lines.append("  - **Suggestion**: Add concrete, actionable details.\n")
    else:
        lines.append("No vague entries detected.\n")

    lines.append("## Next Steps\n")
    lines.append("1. Review the report above.")
    lines.append("2. Approve each suggested action.")
    lines.append("3. Run the skill in apply mode to execute approved changes.\n")

    return "\n".join(lines)


def generate_merge(left: MemoryEntry, right: MemoryEntry, template_path: Path) -> str:
    """Generate a merged memory entry using the merge template and two entries."""
    template = template_path.read_text(encoding="utf-8")
    merged_name = left.name if len(left.name) >= len(right.name) else right.name
    merged_description = left.description if len(left.description) >= len(right.description) else right.description
    merged_body = f"{left.body}\n\n{right.body}"
    result = template.replace("{{merged_name}}", merged_name)
    result = result.replace("{{merged_description}}", merged_description)
    result = result.replace("{{merged_body}}", merged_body)
    return result


def archive_entries(entries: list[MemoryEntry], memory_dir: Path) -> None:
    """Move approved stale entries into <memory_dir>/archive/."""
    archive_dir = memory_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    for entry in entries:
        target = archive_dir / entry.path.name
        entry.path.rename(target)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Analyze Claude Code memory files.")
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--global-dir", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=0.6)
    parser.add_argument("--min-body-words", type=int, default=15)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument(
        "--archive",
        action="store_true",
        help="Move approved stale entries to <memory-dir>/archive/.",
    )
    parser.add_argument(
        "--merge-pair",
        nargs=2,
        metavar=("PATH1", "PATH2"),
        help="Generate a merged entry from two memory files and print to stdout.",
    )
    args = parser.parse_args(argv)

    if args.merge_pair:
        left_path = Path(args.merge_pair[0])
        right_path = Path(args.merge_pair[1])
        left = parse_memory_file(left_path)
        right = parse_memory_file(right_path)
        if left is None or right is None:
            print("Error: Could not parse one or both memory files.", file=sys.stderr)
            return 1
        skill_dir = Path(__file__).resolve().parent
        template_path = skill_dir / "templates" / "merge.md"
        if not template_path.exists():
            print(f"Error: Merge template not found at {template_path}", file=sys.stderr)
            return 1
        print(generate_merge(left, right, template_path))
        return 0

    project_entries = scan_directory_excluding_archive(args.project_dir)
    global_entries = scan_directory_excluding_archive(args.global_dir)
    all_entries = project_entries + global_entries

    duplicates = find_duplicates(all_entries, threshold=args.threshold)
    conflicts = find_conflicts(all_entries)
    stale_entries = find_stale(all_entries)
    vague_entries = find_vague(all_entries, min_body_words=args.min_body_words)

    if args.archive:
        for memory_dir in (args.project_dir, args.global_dir):
            dir_stale = [e for e in stale_entries if e.path.is_relative_to(memory_dir)]
            archive_entries(dir_stale, memory_dir)

    report = generate_report(
        args.project_dir,
        args.global_dir,
        duplicates,
        conflicts,
        stale_entries,
        vague_entries,
    )

    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
