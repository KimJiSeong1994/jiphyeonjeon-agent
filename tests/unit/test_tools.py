"""End-to-end tool invocation tests via FastMCP in-memory Client.

Uses the MCP SDK's own Client talking directly to our FastMCP instance — no
subprocess, no stdio parsing, but full schema validation + handler exec.
"""

from __future__ import annotations

import httpx
import respx
from mcp.server.fastmcp import FastMCP
from pydantic import SecretStr

from jiphyeonjeon_mcp.capability import ServerCapabilities
from jiphyeonjeon_mcp.client import JiphyeonjeonClient
from jiphyeonjeon_mcp.config import Settings
from jiphyeonjeon_mcp.tools import register_all


def _settings() -> Settings:
    return Settings(
        token=SecretStr("tok"),
        base_url="http://backend.test",
        timeout=5.0,
        verify_ssl=True,
    )


def _build_mcp_with_all_tools() -> tuple[FastMCP, list[str]]:
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
    mcp = FastMCP(name="test")
    settings = _settings()

    async def factory() -> JiphyeonjeonClient:
        return JiphyeonjeonClient(settings)

    registered = register_all(mcp, factory, caps)
    return mcp, registered


def test_all_eleven_tools_registered() -> None:
    _mcp, registered = _build_mcp_with_all_tools()
    assert len(registered) == 11
    expected = {
        "search_papers",
        "get_paper",
        "start_review",
        "get_review_status",
        "list_bookmarks",
        "add_bookmark",
        "remove_bookmark",
        "create_curriculum",
        "explore_related",
        "generate_figure",
        "create_blog_draft",
    }
    assert set(registered) == expected


def test_missing_capability_skips_tool() -> None:
    # Only search capability — other tools must NOT register
    caps = ServerCapabilities(version="1.0", capabilities=frozenset({"search"}))
    mcp = FastMCP(name="test2")
    settings = _settings()

    async def factory() -> JiphyeonjeonClient:
        return JiphyeonjeonClient(settings)

    registered = register_all(mcp, factory, caps)
    assert registered == ["search_papers"]


@respx.mock
async def test_tool_schema_contains_expected_fields() -> None:
    """Each tool's MCP-exposed schema must reflect its Pydantic Field descriptions."""
    mcp, _ = _build_mcp_with_all_tools()
    tools = await mcp.list_tools()
    by_name = {t.name: t for t in tools}

    sp = by_name["search_papers"]
    assert sp.description is not None and "search" in sp.description.lower()
    props = sp.inputSchema.get("properties", {})
    assert "query" in props
    assert "max_results" in props  # backend field name (was 'limit')
    assert "year_start" in props  # backend field name (was 'year_from')

    sr = by_name["start_review"]
    props_sr = sr.inputSchema.get("properties", {})
    assert "paper_ids" in props_sr
    assert "fast_mode" in props_sr
    assert "query" not in props_sr  # removed — backend doesn't accept it

    rb = by_name["remove_bookmark"]
    assert "DESTRUCTIVE" in (rb.description or "") or "복구 불가" in (rb.description or "")


@respx.mock
async def test_search_papers_end_to_end() -> None:
    """Invoke the tool through the real call chain (httpx mocked)."""
    respx.post("http://backend.test/api/search").mock(
        return_value=httpx.Response(200, json={"papers": [{"id": "p1", "title": "Survey"}]})
    )
    mcp, _ = _build_mcp_with_all_tools()
    result = await mcp.call_tool("search_papers", {"query": "LLM agents", "limit": 5})
    # call_tool returns a tuple (content, structured) in recent mcp versions;
    # handle both shapes defensively.
    if isinstance(result, tuple):
        content, structured = result
    else:
        content, structured = result, None  # older SDK
    assert structured is not None or content, "tool returned empty"
