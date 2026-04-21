"""Unit tests for JiphyeonjeonClient using respx to mock httpx."""

from __future__ import annotations

import httpx
import pytest
import respx
from mcp.shared.exceptions import McpError
from pydantic import SecretStr

from jiphyeonjeon_mcp.client import JiphyeonjeonClient
from jiphyeonjeon_mcp.config import Settings


def _settings() -> Settings:
    return Settings(
        token=SecretStr("test-jwt-token"),
        base_url="http://backend.test",
        timeout=5.0,
        verify_ssl=True,
    )


@respx.mock
async def test_get_json_success() -> None:
    route = respx.get("http://backend.test/api/papers/abc").mock(
        return_value=httpx.Response(200, json={"id": "abc", "title": "X"})
    )
    async with JiphyeonjeonClient(_settings()) as client:
        data = await client.get_json("/api/papers/abc", operation="get")
    assert data == {"id": "abc", "title": "X"}
    assert route.called
    # Auth header forwarded
    sent = route.calls.last.request.headers.get("authorization")
    assert sent == "Bearer test-jwt-token"


@respx.mock
async def test_post_json_forwards_body() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        import json as _json
        captured["body"] = _json.loads(request.content.decode())
        return httpx.Response(200, json={"session_id": "s1"})

    respx.post("http://backend.test/api/deep-review").mock(side_effect=handler)
    async with JiphyeonjeonClient(_settings()) as client:
        data = await client.post_json(
            "/api/deep-review",
            {"paper_ids": ["p1"], "query": "why"},
            operation="start review",
        )
    assert data == {"session_id": "s1"}
    assert captured["body"] == {"paper_ids": ["p1"], "query": "why"}


@respx.mock
async def test_401_translates_to_mcp_error() -> None:
    respx.get("http://backend.test/api/bookmarks").mock(
        return_value=httpx.Response(401, json={"detail": "expired"})
    )
    async with JiphyeonjeonClient(_settings()) as client:
        with pytest.raises(McpError) as exc_info:
            await client.get_json("/api/bookmarks", operation="list bookmarks")
    assert "인증 실패" in str(exc_info.value)


@respx.mock
async def test_connection_error_wrapped() -> None:
    respx.get("http://backend.test/api/version").mock(
        side_effect=httpx.ConnectError("refused")
    )
    async with JiphyeonjeonClient(_settings()) as client:
        with pytest.raises(McpError) as exc_info:
            await client.get_json("/api/version", operation="probe")
    msg = str(exc_info.value)
    assert "네트워크 오류" in msg
    # Never leak token in error message
    assert "test-jwt-token" not in msg


async def test_client_outside_context_raises() -> None:
    client = JiphyeonjeonClient(_settings())
    with pytest.raises(RuntimeError, match="outside async context"):
        await client.get_json("/api/x", operation="x")


@respx.mock
async def test_delete_returns_none_for_empty_body() -> None:
    respx.delete("http://backend.test/api/bookmarks/123").mock(
        return_value=httpx.Response(204)
    )
    async with JiphyeonjeonClient(_settings()) as client:
        data = await client.delete("/api/bookmarks/123", operation="remove bm")
    assert data is None
