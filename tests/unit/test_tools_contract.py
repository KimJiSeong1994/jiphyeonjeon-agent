"""Contract tests — verify each tool's outbound body actually matches the
backend's Pydantic request schema field names.

These tests would have caught the Phase 6 BLOCKERs (limit vs max_results,
query vs no-field, status vs published) automatically. They mock httpx,
capture the request body, and assert keys.
"""

from __future__ import annotations

import json as _json
from typing import Any, cast

import httpx
import pytest
import respx
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from pydantic import SecretStr

from jiphyeonjeon_mcp.capability import ServerCapabilities
from jiphyeonjeon_mcp.client import JiphyeonjeonClient
from jiphyeonjeon_mcp.config import Settings
from jiphyeonjeon_mcp.tools import register_all


def _build() -> FastMCP:
    caps = ServerCapabilities(
        version="1.1.0",
        capabilities=frozenset(
            {
                "search",
                "papers",
                "deep_review",
                "bookmarks",
                "curriculum",
                "explore",
                "autofigure",
                "blog",
            }
        ),
    )
    mcp = FastMCP(name="contract-test")
    settings = Settings(
        token=SecretStr("tok"),
        base_url="http://backend.test",
        timeout=5.0,
        verify_ssl=True,
    )

    async def factory() -> JiphyeonjeonClient:
        return JiphyeonjeonClient(settings)

    register_all(mcp, factory, caps)
    return mcp


def _captured(route: respx.Route) -> dict[str, Any]:
    assert route.called, "tool did not make the expected request"
    return cast(dict[str, Any], _json.loads(route.calls.last.request.content.decode()))


@respx.mock
async def test_search_papers_sends_backend_field_names() -> None:
    route = respx.post("http://backend.test/api/search").mock(
        return_value=httpx.Response(200, json={"results": {"arxiv": [{"id": "p1"}]}, "total": 1})
    )
    mcp = _build()
    await mcp.call_tool(
        "search_papers",
        {"query": "x", "max_results": 7, "year_start": 2024, "year_end": 2026},
    )
    body = _captured(route)
    assert body["query"] == "x"
    assert body["max_results"] == 7
    assert body["year_start"] == 2024
    assert body["year_end"] == 2026
    # Must NOT contain legacy MCP-side names
    assert "limit" not in body
    assert "year_from" not in body
    assert "year_to" not in body


@respx.mock
async def test_search_papers_flattens_source_groups() -> None:
    respx.post("http://backend.test/api/search").mock(
        return_value=httpx.Response(
            200,
            json={
                "results": {
                    "arxiv": [{"id": "a1", "title": "A"}],
                    "scholar": [{"id": "s1", "title": "S"}],
                },
                "total": 2,
            },
        )
    )
    mcp = _build()
    result = await mcp.call_tool("search_papers", {"query": "x"})
    # Extract the structured payload regardless of SDK return shape.
    payload = None
    if isinstance(result, tuple):
        _content, payload = result
    for candidate in (payload, result):
        if isinstance(candidate, dict) and "papers" in candidate:
            papers = candidate["papers"]
            break
    else:
        # New SDK returns a CallToolResult object whose ``structuredContent`` holds it
        structured = getattr(result, "structuredContent", None) or getattr(
            result, "structured_content", None
        )
        papers = structured["papers"] if structured else []
    assert len(papers) == 2
    assert {p["source"] for p in papers} == {"arxiv", "scholar"}


@respx.mock
async def test_search_papers_deduplicates_and_preserves_backend_metadata() -> None:
    respx.post("http://backend.test/api/search").mock(
        return_value=httpx.Response(
            200,
            json={
                "results": {
                    "arxiv": [{"id": "2401.12345", "title": "Same"}],
                    "openalex": [{"arxiv_id": "2401.12345", "title": "Same"}],
                },
                "total": 2,
                "degraded": ["ranker_unavailable"],
                "query_hash": "query-1",
                "cache_hit": True,
            },
        )
    )
    mcp = _build()
    result = await mcp.call_tool("search_papers", {"query": "x"})
    payload = result[1] if isinstance(result, tuple) else getattr(result, "structuredContent", None)
    assert payload is not None
    assert len(payload["papers"]) == 1
    assert payload["total"] == 1
    assert payload["source_total"] == 2
    assert payload["degraded"] == ["ranker_unavailable"]
    assert payload["query_hash"] == "query-1"
    assert payload["cache_hit"] is True


@respx.mock
async def test_start_review_body_matches_backend() -> None:
    route = respx.post("http://backend.test/api/deep-review").mock(
        return_value=httpx.Response(200, json={"session_id": "s1"})
    )
    mcp = _build()
    await mcp.call_tool(
        "start_review",
        {"paper_ids": ["p1", "p2"], "num_researchers": 2, "fast_mode": False},
    )
    body = _captured(route)
    assert body["paper_ids"] == ["p1", "p2"]
    assert body["num_researchers"] == 2
    assert body["fast_mode"] is False
    # Must NOT send phantom 'query' field that backend would silently drop.
    assert "query" not in body


@respx.mock
async def test_start_review_normalizes_user_facing_arxiv_references() -> None:
    route = respx.post("http://backend.test/api/deep-review").mock(
        return_value=httpx.Response(200, json={"session_id": "s1"})
    )
    mcp = _build()
    await mcp.call_tool(
        "start_review",
        {
            "paper_ids": [
                "https://arxiv.org/abs/2401.12345",
                "https://arxiv.org/pdf/2401.12346v2.pdf",
                "cs/0501001",
            ],
            "fast_mode": False,
        },
    )
    body = _captured(route)
    assert body["paper_ids"] == ["2401.12345", "2401.12346v2", "cs/0501001"]


@respx.mock
async def test_get_review_report_fetches_completed_markdown() -> None:
    route = respx.get("http://backend.test/api/deep-review/report/session-1").mock(
        return_value=httpx.Response(
            200,
            json={
                "session_id": "session-1",
                "report_markdown": "# Review\n\nResult",
                "report_json": {"summary": "Result"},
            },
        )
    )
    mcp = _build()
    await mcp.call_tool("get_review_report", {"session_id": "session-1"})
    assert route.called


@respx.mock
async def test_add_bookmark_resolves_paper_then_posts_metadata() -> None:
    # Step 1: get_paper
    respx.get("http://backend.test/api/papers/2401.12345").mock(
        return_value=httpx.Response(
            200,
            json={
                "title": "Resolved Paper Title",
                "authors": ["A", "B"],
                "year": 2024,
                "arxiv_id": "2401.12345",
                "venue": "NeurIPS",
            },
        )
    )
    # Step 2: from-paper
    post_route = respx.post("http://backend.test/api/bookmarks/from-paper").mock(
        return_value=httpx.Response(200, json={"id": "bm1", "title": "Resolved Paper Title"})
    )
    mcp = _build()
    await mcp.call_tool(
        "add_bookmark",
        {"paper_id": "2401.12345", "topic": "test-topic"},
    )
    body = _captured(post_route)
    assert body["title"] == "Resolved Paper Title"
    assert body["authors"] == ["A", "B"]
    assert body["year"] == 2024
    assert body["topic"] == "test-topic"
    assert body["arxiv_id"] == "2401.12345"
    # paper_id is NOT a field on BookmarkFromPaperRequest
    assert "paper_id" not in body


@respx.mock
async def test_add_bookmark_with_explicit_title_skips_resolution() -> None:
    resolve_route = respx.get("http://backend.test/api/papers/abc").mock(
        return_value=httpx.Response(200, json={})
    )
    post_route = respx.post("http://backend.test/api/bookmarks/from-paper").mock(
        return_value=httpx.Response(200, json={"id": "bm2"})
    )
    mcp = _build()
    await mcp.call_tool(
        "add_bookmark",
        {"title": "Explicit Title", "authors": ["X"], "year": 2025, "topic": "t"},
    )
    assert not resolve_route.called  # no paper_id → no GET
    body = _captured(post_route)
    assert body["title"] == "Explicit Title"
    assert body["authors"] == ["X"]


@respx.mock
async def test_add_bookmark_accepts_search_result_metadata_without_index_lookup() -> None:
    resolve_route = respx.get("http://backend.test/api/papers/2401.12345")
    post_route = respx.post("http://backend.test/api/bookmarks/from-paper").mock(
        return_value=httpx.Response(200, json={"id": "bm3"})
    )
    mcp = _build()
    await mcp.call_tool(
        "add_bookmark",
        {
            "paper_id": "2401.12345",
            "paper": {
                "title": "Search Result",
                "authors": ["A"],
                "year": 2026,
                "arxiv_id": "2401.12345",
            },
            "topic": "t",
        },
    )
    assert not resolve_route.called
    body = _captured(post_route)
    assert body["title"] == "Search Result"
    assert body["arxiv_id"] == "2401.12345"


@respx.mock
async def test_create_blog_draft_sends_published_false_not_status() -> None:
    route = respx.post("http://backend.test/api/blog/posts").mock(
        return_value=httpx.Response(200, json={"id": "post1"})
    )
    mcp = _build()
    await mcp.call_tool(
        "create_blog_draft",
        {
            "title": "T",
            "content": (
                "**DeepWalk**는 그래프 임베딩 방법이다. Micro-F1 35.9를 기록했다.\n\n"
                "**TL;DR** — DeepWalk는 비지도 기법이다. DeepWalk는 Micro-F1 35.9를 "
                "기록했다. DeepWalk는 라벨 희소 조건에 유리하지만 가중 그래프에는 제한이 있다."
            ),
            "tags": ["a"],
        },
    )
    body = _captured(route)
    assert body["title"] == "T"
    assert body["published"] is False  # critical — "draft" is implemented via published=False
    assert body["tags"] == ["a"]
    # Defaults to a paper review since this tool turns papers into posts.
    assert body["category"] == "paper-review"
    # Must NOT send legacy fields the backend would ignore.
    assert "style" not in body
    assert "status" not in body


@respx.mock
async def test_create_blog_draft_accepts_engineering_category() -> None:
    route = respx.post("http://backend.test/api/blog/posts").mock(
        return_value=httpx.Response(200, json={"id": "post1"})
    )
    mcp = _build()
    await mcp.call_tool(
        "create_blog_draft",
        {"title": "T", "content": "body " * 10, "category": "engineering"},
    )
    body = _captured(route)
    assert body["category"] == "engineering"
    assert body["published"] is False


@respx.mock
async def test_create_blog_draft_blocks_preflight_warnings_before_post() -> None:
    route = respx.post("http://backend.test/api/blog/posts").mock(
        return_value=httpx.Response(200, json={"id": "post1"})
    )
    mcp = _build()
    content = (
        '# 제목\n\n**Paper:** Someone. "A Paper." 2026.\n\n'
        "본 문서는 A Paper 논문을 해설한다. " + "내용 " * 20
    )
    with pytest.raises(ToolError) as exc_info:
        await mcp.call_tool("create_blog_draft", {"title": "T", "content": content})
    assert "정의 리드" in str(exc_info.value)
    assert "TL;DR" in str(exc_info.value)
    assert not route.called


async def test_check_blog_draft_returns_read_only_preflight_result() -> None:
    mcp = _build()
    result = await mcp.call_tool(
        "check_blog_draft",
        {"content": "본 문서는 A Paper 논문을 해설한다. " + "내용 " * 20},
    )
    payload = result[1] if isinstance(result, tuple) else result
    assert "ready" in str(payload)
    assert "citability_warnings" in str(payload)


@respx.mock
async def test_create_blog_draft_explicit_override_preserves_warning_result() -> None:
    route = respx.post("http://backend.test/api/blog/posts").mock(
        return_value=httpx.Response(200, json={"id": "post1"})
    )
    mcp = _build()
    content = "본 문서는 A Paper 논문을 해설한다. " + "내용 " * 20
    result = await mcp.call_tool(
        "create_blog_draft",
        {"title": "T", "content": content, "allow_citability_warnings": True},
    )
    assert route.called
    assert "citability_warnings" in str(result)


@respx.mock
async def test_update_blog_draft_sends_partial_put_and_keeps_unpublished() -> None:
    route = respx.put("http://backend.test/api/blog/posts/post1").mock(
        return_value=httpx.Response(200, json={"id": "post1", "published": False})
    )
    mcp = _build()
    await mcp.call_tool(
        "update_blog_draft",
        {
            "post_id": "post1",
            "title": "Updated",
            "category": "engineering",
        },
    )
    assert _captured(route) == {
        "title": "Updated",
        "category": "engineering",
        "published": False,
    }


@respx.mock
async def test_update_blog_draft_blocks_content_warnings_before_put() -> None:
    route = respx.put("http://backend.test/api/blog/posts/post1").mock(
        return_value=httpx.Response(200, json={"id": "post1"})
    )
    mcp = _build()
    with pytest.raises(ToolError, match="사전 검증에 실패"):
        await mcp.call_tool(
            "update_blog_draft",
            {
                "post_id": "post1",
                "content": "본 문서는 검증되지 않은 초안이다. " + "내용 " * 10,
            },
        )
    assert not route.called


@respx.mock
async def test_create_blog_draft_clean_content_has_no_warnings() -> None:
    respx.post("http://backend.test/api/blog/posts").mock(
        return_value=httpx.Response(200, json={"id": "post1"})
    )
    mcp = _build()
    content = (
        '# 제목\n\n**Paper:** Someone. "A Paper." 2026.\n\n'
        "**DeepWalk**는 random walk를 문장처럼 다뤄 정점 임베딩을 학습하는 "
        "방법이다. 라벨 1% 조건에서 Micro-F1을 10%p 앞선다.\n\n"
        "| 항목 | 값 |\n|---|---|\n| F1 | 35.9 |\n\n"
        "**TL;DR** — DeepWalk는 비지도 임베딩 기법이다. Micro-F1 35.9를 "
        "기록했다. 라벨 희소 조건에 유리하지만 가중 그래프는 다루지 못한다.\n"
    )
    result = await mcp.call_tool("create_blog_draft", {"title": "T", "content": content})
    payload = result[1] if isinstance(result, tuple) else result
    assert "citability_warnings" not in str(payload)


@respx.mock
async def test_create_blog_draft_engineering_skips_citability_lint() -> None:
    respx.post("http://backend.test/api/blog/posts").mock(
        return_value=httpx.Response(200, json={"id": "post1"})
    )
    mcp = _build()
    result = await mcp.call_tool(
        "create_blog_draft",
        {
            "title": "T",
            "content": "본 글은 검색 개선 작업 기록이다. " + "내용 " * 10,
            "category": "engineering",
        },
    )
    payload = result[1] if isinstance(result, tuple) else result
    assert "citability_warnings" not in str(payload)


@respx.mock
async def test_generate_figure_sends_paper_title_not_caption() -> None:
    route = respx.post("http://backend.test/api/autofigure/method-to-svg").mock(
        return_value=httpx.Response(200, json={"success": True, "svg_content": "<svg/>"})
    )
    mcp = _build()
    await mcp.call_tool(
        "generate_figure",
        {"method_text": "x" * 20, "paper_title": "My Paper", "optimize_iterations": 2},
    )
    body = _captured(route)
    assert body["method_text"]
    assert body["paper_title"] == "My Paper"
    assert body["optimize_iterations"] == 2
    assert "caption" not in body


@respx.mock
async def test_curriculum_sends_required_fields() -> None:
    route = respx.post("http://backend.test/api/curricula/generate").mock(
        return_value=httpx.Response(200, json={"curriculum_id": "c1"})
    )
    mcp = _build()
    await mcp.call_tool(
        "create_curriculum",
        {"topic": "GraphRAG", "difficulty": "advanced", "num_modules": 6},
    )
    body = _captured(route)
    assert body == {"topic": "GraphRAG", "difficulty": "advanced", "num_modules": 6}


async def test_get_paper_rejects_path_traversal() -> None:
    """Path-traversal attempts must be rejected BEFORE any HTTP request.

    No respx mock is installed — if the tool attempted a real HTTP call it
    would fail with a ConnectError (backend.test is not resolvable). We
    assert the validation error fires first, so the HTTP layer is never
    reached.
    """
    import pytest
    from mcp.server.fastmcp.exceptions import ToolError

    mcp = _build()
    with pytest.raises(ToolError) as exc_info:
        await mcp.call_tool("get_paper", {"paper_id": "../admin/users"})
    assert "허용된 형식" in str(exc_info.value)
