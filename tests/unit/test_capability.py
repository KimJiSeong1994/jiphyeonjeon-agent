"""Unit tests for capability negotiation."""

from __future__ import annotations

import httpx
import respx
from pydantic import SecretStr

from jiphyeonjeon_mcp.capability import BASELINE_CAPABILITIES, discover_capabilities
from jiphyeonjeon_mcp.config import Settings


def _settings() -> Settings:
    return Settings(
        token=SecretStr("tok"),
        base_url="http://backend.test",
        timeout=5.0,
        verify_ssl=True,
    )


@respx.mock
async def test_version_endpoint_present() -> None:
    respx.get("http://backend.test/api/version").mock(
        return_value=httpx.Response(
            200,
            json={
                "version": "1.1.0",
                "capabilities": ["search", "papers", "deep_review", "autofigure", "blog"],
                "mcp_min_client": "0.1.0",
            },
        )
    )
    caps = await discover_capabilities(_settings())
    assert caps.version == "1.1.0"
    assert caps.supports("search")
    assert caps.supports("blog")
    assert not caps.supports("nonexistent")


@respx.mock
async def test_404_falls_back_to_baseline() -> None:
    respx.get("http://backend.test/api/version").mock(return_value=httpx.Response(404))
    caps = await discover_capabilities(_settings())
    assert caps.version == "legacy"
    assert caps.capabilities == BASELINE_CAPABILITIES


@respx.mock
async def test_connection_error_falls_back_to_baseline() -> None:
    respx.get("http://backend.test/api/version").mock(
        side_effect=httpx.ConnectError("backend down")
    )
    caps = await discover_capabilities(_settings())
    assert caps.capabilities == BASELINE_CAPABILITIES


@respx.mock
async def test_malformed_response_falls_back() -> None:
    respx.get("http://backend.test/api/version").mock(
        return_value=httpx.Response(200, text="not json")
    )
    caps = await discover_capabilities(_settings())
    assert caps.capabilities == BASELINE_CAPABILITIES


@respx.mock
async def test_empty_capabilities_uses_baseline() -> None:
    respx.get("http://backend.test/api/version").mock(
        return_value=httpx.Response(200, json={"version": "2.0", "capabilities": []})
    )
    caps = await discover_capabilities(_settings())
    assert caps.capabilities == BASELINE_CAPABILITIES
