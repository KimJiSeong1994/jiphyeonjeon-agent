"""Server lifespan regressions: connection reuse and non-blocking advisories."""

from __future__ import annotations

import asyncio

import httpx
from pydantic import SecretStr

from jiphyeonjeon_mcp.capability import ServerCapabilities
from jiphyeonjeon_mcp.config import Settings
from jiphyeonjeon_mcp.server import _build_client_factory, _build_server, _SharedClientPool
from jiphyeonjeon_mcp.updater import UpdateCheckResult


def _settings() -> Settings:
    return Settings(
        token=SecretStr("tok"),
        base_url="http://backend.test",
        auto_update_check=False,
    )


async def test_server_pool_reuses_transport_and_closes_it_on_shutdown() -> None:
    pool = _SharedClientPool(_settings())
    factory = _build_client_factory(_settings(), pool)

    async with pool:
        first = await factory()
        second = await factory()
        first_transport = first._client
        assert first_transport is not None
        assert second._client is first_transport
        async with first, second:
            pass
        assert not first_transport.is_closed

    assert isinstance(first_transport, httpx.AsyncClient)
    assert first_transport.is_closed


async def test_update_check_does_not_delay_lifespan_readiness(monkeypatch) -> None:
    started = asyncio.Event()
    release = asyncio.Event()

    async def slow_check(_settings: Settings) -> UpdateCheckResult:
        started.set()
        await release.wait()
        return UpdateCheckResult(current_version="test")

    monkeypatch.setattr("jiphyeonjeon_mcp.server.check_for_updates", slow_check)
    mcp, _ = _build_server(
        _settings(),
        ServerCapabilities(version="test", capabilities=frozenset()),
    )

    async with asyncio.timeout(0.2):
        async with mcp._mcp_server.lifespan(mcp._mcp_server):
            await started.wait()
            assert not release.is_set()
            release.set()
