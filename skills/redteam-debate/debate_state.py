"""State manager for red-team vs blue-team debates with green-team verdict."""

import json
from datetime import datetime
from pathlib import Path


SAVE_DIR = Path.home() / ".claude" / "skills" / "redteam-debate" / "saved_debates"
SCHEMA_VERSION = 1


class DebateState:
    """Tracks a multi-round adversarial debate with persistent storage."""

    def __init__(self, topic: str, max_rounds: int = 5) -> None:
        self.topic = topic
        self.max_rounds = max_rounds
        self.current_round = 0
        self.rounds: list[dict] = []
        self.schema_version = SCHEMA_VERSION
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def add_round(
        self,
        red_points: list[str],
        blue_rebuttals: list[str],
        green_notes: list[str] | None = None,
        resolved: list[bool] | None = None,
    ) -> None:
        """Record one complete round of red/blue exchange.

        Args:
            resolved: Optional list of bools, one per red_point, indicating
                      whether the blue rebuttal successfully addressed it.
        """
        if resolved is not None and len(resolved) != len(red_points):
            raise ValueError(
                f"resolved length ({len(resolved)}) must match "
                f"red_points length ({len(red_points)})"
            )
        self.rounds.append({
            "round": self.current_round + 1,
            "red_points": red_points,
            "blue_rebuttals": blue_rebuttals,
            "green_notes": green_notes or [],
            "resolved": resolved,
            "timestamp": datetime.now().isoformat(),
        })
        self.current_round += 1
        self.updated_at = datetime.now().isoformat()

    def can_continue(self) -> bool:
        return self.current_round < self.max_rounds

    def is_complete(self) -> bool:
        return self.current_round >= self.max_rounds

    def extend_rounds(self, extra: int) -> None:
        """Allow user to request additional rounds mid-debate."""
        self.max_rounds += extra
        self.updated_at = datetime.now().isoformat()

    def generate_verdict(self) -> str:
        """Produce the green-team pragmatic verdict."""
        all_red: list[str] = []
        all_blue: list[str] = []
        unresolved: list[str] = []
        has_resolved_tracking = False

        for r in self.rounds:
            red = r["red_points"]
            blue = r["blue_rebuttals"]
            resolved = r.get("resolved")
            all_red.extend(red)
            all_blue.extend(blue)

            if resolved is not None:
                has_resolved_tracking = True
                for i, (p, ok) in enumerate(zip(red, resolved)):
                    if not ok:
                        unresolved.append(p)
            # If no resolved tracking, we intentionally do NOT guess —
            # the caller must supply resolved flags for accurate auto-verdict.

        lines = [
            "# 绿队最终评估",
            f"## 议题：{self.topic}",
            f"\n总轮数：{self.current_round} / {self.max_rounds}",
            "\n### 红队提出的核心问题",
        ]
        for i, p in enumerate(all_red, 1):
            lines.append(f"{i}. {p}")

        lines.append("\n### 蓝队的主要反驳")
        for i, b in enumerate(all_blue, 1):
            lines.append(f"{i}. {b}")

        if unresolved:
            lines.append("\n### 尚未解决的风险")
            for p in unresolved:
                lines.append(f"- {p}")

        lines.append("\n### 结论")
        if not has_resolved_tracking:
            lines.append(
                "**需人工判断** — 自动评估未收到 resolved 标记，请绿队人工审查后下结论。"
            )
        elif len(unresolved) > len(all_red) * 0.5:
            lines.append("**不可用** — 核心风险未被有效反驳，建议重新设计或放弃。")
        elif unresolved:
            lines.append(
                "**谨慎可用** — 大部分问题有应对方案，但剩余风险需要修改后重新评估。"
            )
        else:
            lines.append(
                "**可用** — 红队提出的风险均得到有效回应，方案具备实施条件。"
            )

        lines.append("\n### 修改建议")
        if unresolved:
            lines.append("针对未解决问题优先处理：")
            for p in unresolved[:3]:
                lines.append(f"- {p}")
        else:
            lines.append("- 记录本轮辩论结论作为设计依据")
            lines.append("- 实施阶段保持监控，建立反馈回路")

        return "\n".join(lines)

    def default_save_path(self) -> Path:
        safe_topic = "".join(
            c if c.isalnum() or c in "-_" else "_" for c in self.topic
        )[:40]
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        return SAVE_DIR / f"{safe_topic}_{self.created_at[:10]}.json"

    def save(self, path: Path | None = None) -> Path:
        target = path or self.default_save_path()
        self.updated_at = datetime.now().isoformat()
        target.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False))
        return target

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "topic": self.topic,
            "max_rounds": self.max_rounds,
            "current_round": self.current_round,
            "rounds": self.rounds,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def load(cls, path: Path | str) -> "DebateState":
        path = Path(path)
        data = json.loads(path.read_text())
        obj = cls.__new__(cls)
        obj.topic = data["topic"]
        obj.max_rounds = data["max_rounds"]
        obj.current_round = data["current_round"]
        obj.rounds = data["rounds"]
        obj.schema_version = data.get("schema_version", 1)
        obj.created_at = data["created_at"]
        obj.updated_at = data["updated_at"]
        return obj
