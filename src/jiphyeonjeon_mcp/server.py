"""Jiphyeonjeon MCP server — stdio transport entry point.

Boot sequence:
1. Load settings (env vars). Exit 1 if JIPHYEONJEON_TOKEN missing.
2. Probe GET /api/version for capability negotiation (baseline fallback).
3. Register only the tools whose capability is advertised.
4. Run the FastMCP server over stdio.

Never write to stdout — stdio is the JSON-RPC channel. All logging goes
to stderr, which the host (Claude Code) captures in its own logs.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager, suppress
from types import TracebackType
from typing import Any

from mcp.server.fastmcp import FastMCP

from jiphyeonjeon_mcp import __version__
from jiphyeonjeon_mcp.capability import (
    IncompatibleClientError,
    ServerCapabilities,
    discover_capabilities,
    ensure_client_compatible,
)
from jiphyeonjeon_mcp.client import JiphyeonjeonClient
from jiphyeonjeon_mcp.config import Settings, load_settings
from jiphyeonjeon_mcp.tools import register_all
from jiphyeonjeon_mcp.updater import UpdateCheckResult, check_for_updates


def _configure_logging() -> None:
    """Route all logging to stderr — never stdout (JSON-RPC channel)."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )


def _emit_update_notice(result: UpdateCheckResult) -> None:
    """Print a single-line update notice to stderr when a new release exists.

    Format is fixed so log scrapers can parse it. No ANSI colors — Claude Code
    strips them anyway. Errors from the check are demoted to DEBUG so they do
    not noise up MCP status panels.
    """
    if result.error is not None:
        logging.getLogger("jiphyeonjeon_mcp.updater").debug(
            "update check skipped: %s", result.error
        )
        return
    if not result.update_available or not result.latest_version:
        return
    print(
        f"[jiphyeonjeon-mcp] new release {result.latest_version} available "
        f"(current {result.current_version}). Run /jh:update to upgrade. "
        f"Release notes: {result.release_url or 'n/a'}",
        file=sys.stderr,
        flush=True,
    )


def _build_client_factory(
    settings: Settings,
    pool: _SharedClientPool | None = None,
) -> Callable[[], Awaitable[JiphyeonjeonClient]]:
    """Return borrowed clients in server lifespan, fresh clients in direct tests."""

    async def factory() -> JiphyeonjeonClient:
        if pool is not None and pool.client is not None:
            return pool.client.borrow()
        return JiphyeonjeonClient(settings)

    return factory


class _SharedClientPool:
    """Own the authenticated HTTP pool for exactly one FastMCP lifespan."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self.client: JiphyeonjeonClient | None = None

    async def __aenter__(self) -> _SharedClientPool:
        owner = JiphyeonjeonClient(self._settings)
        self.client = await owner.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        client = self.client
        self.client = None
        if client is not None:
            await client.__aexit__(exc_type, exc, tb)


async def _check_for_updates_in_background(settings: Settings) -> None:
    """Run the advisory update check without extending the readiness path."""
    try:
        _emit_update_notice(await check_for_updates(settings))
    except Exception:  # noqa: BLE001 - background advisory must never stop the server
        logging.getLogger("jiphyeonjeon_mcp.updater").debug(
            "unexpected background update-check failure", exc_info=True
        )


def _build_server(
    settings: Settings,
    capabilities: ServerCapabilities,
) -> tuple[FastMCP[Any], list[str]]:
    pool = _SharedClientPool(settings)

    @asynccontextmanager
    async def lifespan(_server: FastMCP[Any]) -> AsyncIterator[None]:
        async with pool:
            update_task = asyncio.create_task(_check_for_updates_in_background(settings))
            try:
                yield None
            finally:
                if not update_task.done():
                    update_task.cancel()
                with suppress(asyncio.CancelledError):
                    await update_task

    mcp = FastMCP(
        name="jiphyeonjeon",
        instructions=(
            f"집현전 (PaperReviewAgent) MCP server v{__version__}. Exposes paper search, "
            "deep review, bookmarks, curriculum, citation graph, and figure generation "
            "as tools. All calls act on behalf of the JWT user configured via "
            "JIPHYEONJEON_TOKEN."
        ),
        lifespan=lifespan,
    )
    # FastMCP 1.x otherwise advertises the SDK version in initialize.serverInfo.
    # The low-level server exposes the implementation-version field directly.
    mcp._mcp_server.version = __version__
    factory = _build_client_factory(settings, pool)
    registered = register_all(mcp, factory, capabilities)
    return mcp, registered


def main() -> None:
    """Entry point used by ``[project.scripts]`` and ``python -m jiphyeonjeon_mcp``."""
    _configure_logging()
    logger = logging.getLogger("jiphyeonjeon_mcp")

    settings = load_settings()
    logger.info(
        "jiphyeonjeon-mcp v%s starting; backend=%s timeout=%.1fs",
        __version__,
        settings.normalized_base_url,
        settings.timeout,
    )

    capabilities = asyncio.run(discover_capabilities(settings))
    try:
        ensure_client_compatible(capabilities)
    except IncompatibleClientError as exc:
        logger.error("MCP/backend compatibility check failed: %s", exc)
        raise SystemExit(1) from exc
    logger.info(
        "Negotiated capabilities (server=%s): %s",
        capabilities.version,
        sorted(capabilities.capabilities),
    )
    mcp, registered = _build_server(settings, capabilities)
    logger.info("Registered %d tools: %s", len(registered), registered)

    mcp.run()


if __name__ == "__main__":
    main()
