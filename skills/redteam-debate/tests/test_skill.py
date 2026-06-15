"""Tests for redteam-debate skill."""

import os
import re
import tempfile
from pathlib import Path

import pytest
import yaml

SKILL_DIR = Path("/Users/qslu/.claude/skills/redteam-debate")
SKILL_MD = SKILL_DIR / "SKILL.md"
DEBATE_STATE = SKILL_DIR / "debate_state.py"


class TestSkillMd:
    """Validate SKILL.md structure and content."""

    @pytest.fixture(scope="class")
    def skill_content(self):
        assert SKILL_MD.exists(), f"SKILL.md not found at {SKILL_MD}"
        return SKILL_MD.read_text()

    @pytest.fixture(scope="class")
    def frontmatter(self, skill_content):
        match = re.match(r"^---\n(.*?)\n---\n", skill_content, re.DOTALL)
        assert match, "YAML frontmatter not found in SKILL.md"
        return yaml.safe_load(match.group(1))

    def test_frontmatter_name(self, frontmatter):
        assert frontmatter.get("name") == "redteam-debate", "name must be 'redteam-debate'"

    def test_frontmatter_description(self, frontmatter):
        desc = frontmatter.get("description", "")
        assert "red team" in desc.lower() or "debate" in desc.lower(), \
            "description should mention red team or debate"

    def test_contains_red_team(self, skill_content):
        assert "红队" in skill_content or "Red Team" in skill_content, \
            "Must define Red Team role"

    def test_contains_blue_team(self, skill_content):
        assert "蓝队" in skill_content or "Blue Team" in skill_content, \
            "Must define Blue Team role"

    def test_contains_green_team(self, skill_content):
        assert "绿队" in skill_content or "Green Team" in skill_content, \
            "Must define Green Team (pragmatic) role"

    def test_contains_round_mechanism(self, skill_content):
        assert "轮" in skill_content or "round" in skill_content.lower(), \
            "Must define round-based debate mechanism"

    def test_contains_continue_mechanism(self, skill_content):
        content_lower = skill_content.lower()
        assert "续" in skill_content or "continue" in content_lower or "再来" in skill_content, \
            "Must support continuing debates for more rounds"

    def test_contains_state_persistence(self, skill_content):
        content_lower = skill_content.lower()
        assert (
            "save" in content_lower or "persist" in content_lower
            or "保存" in skill_content or "状态" in skill_content
        ), "Must persist debate state between sessions"

    def test_contains_final_verdict(self, skill_content):
        content_lower = skill_content.lower()
        assert (
            "verdict" in content_lower or "结论" in skill_content
            or "是否可用" in skill_content or "怎么修改" in skill_content
        ), "Must produce final verdict with usability/modification advice"

    def test_max_lines(self, skill_content):
        lines = skill_content.splitlines()
        assert len(lines) <= 300, f"SKILL.md has {len(lines)} lines, max 300"


class TestDebateState:
    """Validate debate_state.py functionality."""

    @pytest.fixture
    def state_module(self):
        assert DEBATE_STATE.exists(), f"debate_state.py not found at {DEBATE_STATE}"
        import importlib.util
        spec = importlib.util.spec_from_file_location("debate_state", DEBATE_STATE)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_has_debate_state_class(self, state_module):
        assert hasattr(state_module, "DebateState"), "debate_state.py must export DebateState"

    def test_save_and_load(self, state_module, tmp_path):
        state = state_module.DebateState(topic="测试方案")
        state.add_round(red_points=["问题1"], blue_rebuttals=["反驳1"])

        save_path = tmp_path / "test_debate.json"
        state.save(save_path)
        assert save_path.exists()

        loaded = state_module.DebateState.load(save_path)
        assert loaded.topic == "测试方案"
        assert loaded.schema_version == state_module.SCHEMA_VERSION
        assert len(loaded.rounds) == 1
        assert loaded.rounds[0]["red_points"] == ["问题1"]
        assert loaded.rounds[0]["blue_rebuttals"] == ["反驳1"]

    def test_continue_rounds(self, state_module, tmp_path):
        state = state_module.DebateState(topic="测试方案")
        state.add_round(red_points=["问题1"], blue_rebuttals=["反驳1"])
        state.max_rounds = 5
        state.current_round = 1

        save_path = tmp_path / "test_debate.json"
        state.save(save_path)

        loaded = state_module.DebateState.load(save_path)
        assert loaded.can_continue()

        loaded.extend_rounds(3)
        assert loaded.max_rounds == 8

    def test_final_verdict(self, state_module):
        state = state_module.DebateState(topic="测试方案")
        state.add_round(red_points=["性能差"], blue_rebuttals=["有优化空间"])
        state.current_round = 1
        state.max_rounds = 1

        assert state.is_complete()
        verdict = state.generate_verdict()
        assert "可用" in verdict or "修改" in verdict or "结论" in verdict

    def test_default_save_location(self, state_module):
        state = state_module.DebateState(topic="测试")
        path = state.default_save_path()
        assert "redteam-debate" in str(path)

    def test_round_with_resolved(self, state_module):
        state = state_module.DebateState(topic="测试方案")
        state.add_round(
            red_points=["性能差"],
            blue_rebuttals=["已优化"],
            resolved=[True],
        )
        state.current_round = 1
        state.max_rounds = 1
        verdict = state.generate_verdict()
        assert "可用" in verdict
        assert "不可用" not in verdict

    def test_round_with_unresolved(self, state_module):
        state = state_module.DebateState(topic="测试方案")
        state.add_round(
            red_points=["性能差", "成本高"],
            blue_rebuttals=["已优化", ""],
            resolved=[True, False],
        )
        state.current_round = 1
        state.max_rounds = 1
        verdict = state.generate_verdict()
        assert "谨慎可用" in verdict
        assert "成本高" in verdict

    def test_verdict_without_resolved_fallback(self, state_module):
        state = state_module.DebateState(topic="测试方案")
        state.add_round(red_points=["性能差"], blue_rebuttals=["有优化空间"])
        state.current_round = 1
        state.max_rounds = 1
        verdict = state.generate_verdict()
        assert "自动评估" in verdict or "人工判断" in verdict or "结论" in verdict
        assert "不可用" not in verdict

    def test_multiple_rounds_resolved_tracking(self, state_module):
        state = state_module.DebateState(topic="测试方案")
        state.add_round(
            red_points=["问题A"],
            blue_rebuttals=["反驳A"],
            resolved=[True],
        )
        state.add_round(
            red_points=["问题B"],
            blue_rebuttals=["反驳B"],
            resolved=[False],
        )
        state.current_round = 2
        state.max_rounds = 2
        verdict = state.generate_verdict()
        assert "问题B" in verdict
        # 问题A resolved=True，不应出现在"尚未解决的风险"中
        unresolved_section = verdict.split("### 尚未解决的风险")[1] if "### 尚未解决的风险" in verdict else ""
        assert "问题B" in unresolved_section
        assert "问题A" not in unresolved_section
