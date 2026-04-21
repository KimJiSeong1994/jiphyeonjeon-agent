"""Contract tests — verify each tool's outbound body actually matches the
backend's Pydantic request schema field names.

These tests would have caught the Phase 6 BLOCKERs (limit vs max_results,
query vs no-field, status vs published) automatically. They mock httpx,
capture the request body, and assert keys.
"""

from __future__ import annotations

import json as _json
from typing import Any

import httpx
import respx
from mcp.server.fastmcp import FastMCP
from pydantic import SecretStr

from jiphyeonjeon_mcp.capability import ServerCapabilities
from jiphyeonjeon_mcp.client import JiphyeonjeonClient
from jiphyeonjeon_mcp.config import Settings
from jiphyeonjeon_mcp.tools import register_all


def _build() -> FastMCP:
    caps = ServerCapabilities(
        version="1.1.0",
        capabilities=frozenset(
            {"search", "papers", "deep_review", "bookmarks", "curriculum",
             "explore", "autofigure", "blog"}
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
    return _json.loads(route.calls.last.request.content.decode())


@respx.mock
async def test_search_papers_sends_backend_field_names() -> None:
    route = respx.post("http://backend.test/api/search").mock(
        return_value=httpx.Response(
            200, json={"results": {"arxiv": [{"id": "p1"}]}, "total": 1}
        )
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
async def test_create_blog_draft_sends_published_false_not_status() -> None:
    route = respx.post("http://backend.test/api/blog/posts").mock(
        return_value=httpx.Response(200, json={"id": "post1"})
    )
    mcp = _build()
    await mcp.call_tool(
        "create_blog_draft",
        {"title": "T", "content": "body " * 10, "tags": ["a"]},
    )
    body = _captured(route)
    assert body["title"] == "T"
    assert body["published"] is False  # critical — "draft" is implemented via published=False
    assert body["tags"] == ["a"]
    # Must NOT send legacy fields the backend would ignore.
    assert "style" not in body
    assert "status" not in body


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
