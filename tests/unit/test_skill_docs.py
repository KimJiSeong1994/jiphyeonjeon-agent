"""Regression tests for bundled Claude skills that call MCP tools."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_review_skill_uses_current_tool_schema() -> None:
    text = (ROOT / "skills" / "jh-review-paper.md").read_text(encoding="utf-8")

    assert "search_papers({query, max_results:" in text
    assert "search_papers({query, limit:" not in text
    assert "start_review({paper_ids: [선택 id], query:" not in text
    assert "start_review({paper_ids: [선택 id 또는 정규화한 arXiv ID], fast_mode: false})" in text
