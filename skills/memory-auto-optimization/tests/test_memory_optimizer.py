"""Tests for memory_optimizer.py."""

from pathlib import Path

import pytest

from memory_optimizer import (
    MemoryEntry,
    find_conflicts,
    find_duplicates,
    find_stale,
    find_vague,
    jaccard_similarity,
    main,
    parse_memory_file,
    scan_directory,
    tokenize,
)


def _load_entries(paths: list[Path]) -> list[MemoryEntry]:
    """Parse memory files and assert all are valid."""
    entries = [parse_memory_file(p) for p in paths]
    assert all(entry is not None for entry in entries)
    return entries  # type: ignore[return-value]


@pytest.fixture
def sample_memory(tmp_path: Path) -> Path:
    """Create a sample memory file."""
    path = tmp_path / "user_preference.md"
    path.write_text(
        "---\n"
        "name: user-preference\n"
        "description: User prefers dark mode\n"
        "---\n"
        "\n"
        "Always use dark mode in the UI.\n",
        encoding="utf-8",
    )
    return path


@pytest.fixture
def duplicate_memory(tmp_path: Path) -> Path:
    """Create a memory file similar to sample_memory."""
    path = tmp_path / "user_pref.md"
    path.write_text(
        "---\n"
        "name: user-pref\n"
        "description: User likes dark mode\n"
        "---\n"
        "\n"
        "Always use dark mode in the UI.\n",
        encoding="utf-8",
    )
    return path


def test_parse_memory_file(sample_memory: Path) -> None:
    entry = parse_memory_file(sample_memory)
    assert entry is not None
    assert entry.name == "user-preference"
    assert entry.description == "User prefers dark mode"
    assert "dark mode" in entry.body


def test_parse_memory_file_without_frontmatter(tmp_path: Path) -> None:
    path = tmp_path / "plain.md"
    path.write_text("Just some notes.", encoding="utf-8")
    assert parse_memory_file(path) is None


def test_tokenize() -> None:
    tokens = tokenize("Always use dark mode in the UI.")
    assert "dark" in tokens
    assert "mode" in tokens
    assert "the" not in tokens


def test_jaccard_similarity_identical() -> None:
    text = "Always use dark mode in the UI"
    assert jaccard_similarity(text, text) == 1.0


def test_jaccard_similarity_different() -> None:
    a = "Always use dark mode"
    b = "Deploy to Kubernetes cluster"
    assert jaccard_similarity(a, b) == 0.0


def test_find_duplicates(sample_memory: Path, duplicate_memory: Path) -> None:
    entries = _load_entries([sample_memory, duplicate_memory])
    duplicates = find_duplicates(entries, threshold=0.5)
    assert len(duplicates) == 1
    assert duplicates[0][2] > 0.5


def test_find_conflicts(tmp_path: Path) -> None:
    left = tmp_path / "conda.md"
    left.write_text(
        "---\nname: use-conda\ndescription: Use conda\n---\n\nUse conda for Python environments.",
        encoding="utf-8",
    )
    right = tmp_path / "venv.md"
    right.write_text(
        "---\nname: use-venv\ndescription: Use venv\n---\n\nUse venv for Python environments.",
        encoding="utf-8",
    )
    entries = _load_entries([left, right])
    conflicts = find_conflicts(entries)
    assert len(conflicts) == 1
    assert "environment tool conflict" in conflicts[0][2]


def test_find_stale(tmp_path: Path) -> None:
    path = tmp_path / "old.md"
    path.write_text(
        "---\nname: old-way\ndescription: Old approach\n---\n\nThis is a temporary deprecated approach.",
        encoding="utf-8",
    )
    entries = _load_entries([path])
    assert len(find_stale(entries)) == 1


def test_find_vague(tmp_path: Path) -> None:
    path = tmp_path / "vague.md"
    path.write_text(
        "---\nname: vague\ndescription: Be careful\n---\n\nBe careful.",
        encoding="utf-8",
    )
    entries = _load_entries([path])
    assert len(find_vague(entries)) == 1


def test_scan_directory(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text(
        "---\nname: a\ndescription: A\n---\n\nBody A.", encoding="utf-8"
    )
    (tmp_path / "b.txt").write_text("not markdown", encoding="utf-8")
    entries = scan_directory(tmp_path)
    assert len(entries) == 1
    assert entries[0].name == "a"


def test_main_dry_run(tmp_path: Path, sample_memory: Path) -> None:
    output = tmp_path / "report.md"
    main(
        [
            "--project-dir",
            str(sample_memory.parent),
            "--global-dir",
            str(tmp_path / "global"),
            "--output",
            str(output),
        ]
    )
    assert output.exists()
    report = output.read_text(encoding="utf-8")
    assert "Memory Auto-Optimization Report" in report


def test_main_finds_duplicate(
    tmp_path: Path, sample_memory: Path, duplicate_memory: Path
) -> None:
    output = tmp_path / "report.md"
    main(
        [
            "--project-dir",
            str(sample_memory.parent),
            "--global-dir",
            str(tmp_path / "global"),
            "--output",
            str(output),
        ]
    )
    report = output.read_text(encoding="utf-8")
    assert "Duplicates" in report
    assert "user-preference" in report or "user-pref" in report
