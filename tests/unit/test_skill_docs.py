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
    assert "get_review_report({session_id})" in text


def test_all_skills_avoid_legacy_tool_arguments() -> None:
    skill_dir = ROOT / "skills"
    texts = "\n".join(path.read_text(encoding="utf-8") for path in skill_dir.glob("*.md"))

    assert "search_papers({query: 주제, limit:" not in texts
    assert "search_papers({query: topic, limit:" not in texts
    assert "year_from:" not in texts
    assert "create_blog_draft({title, content, tags, style})" not in texts


def test_readme_skill_count_matches_bundled_skills() -> None:
    skill_count = len(list((ROOT / "skills").glob("*.md")))
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert f"### Skills ({skill_count})" in readme


def test_blog_skill_preflights_and_updates_in_place() -> None:
    text = (ROOT / "skills" / "jh-draft-blog.md").read_text(encoding="utf-8")
    assert "check_blog_draft({content" in text
    assert "update_blog_draft({post_id" in text
