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
from collections.abc import Awaitable, Callable

from mcp.server.fastmcp import FastMCP

from jiphyeonjeon_mcp import __version__
from jiphyeonjeon_mcp.capability import ServerCapabilities, discover_capabilities
from jiphyeonjeon_mcp.client import JiphyeonjeonClient
from jiphyeonjeon_mcp.config import Settings, load_settings
from jiphyeonjeon_mcp.tools import register_all


def _configure_logging() -> None:
    """Route all logging to stderr — never stdout (JSON-RPC channel)."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )


def _build_client_factory(
    settings: Settings,
) -> Callable[[], Awaitable[JiphyeonjeonClient]]:
    """Return an async factory that yields a fresh ``JiphyeonjeonClient`` context.

    Each tool call creates its own client. This is simpler than a shared client
    (no cleanup coordination) and fast enough given httpx connection pooling is
    per-client — tool calls are not hot-loop latency-sensitive.
    """

    async def factory() -> JiphyeonjeonClient:
        return JiphyeonjeonClient(settings)

    return factory


def _build_server(
    settings: Settings,
    capabilities: ServerCapabilities,
) -> tuple[FastMCP, list[str]]:
    mcp = FastMCP(
        name="jiphyeonjeon",
        instructions=(
            f"집현전 (PaperReviewAgent) MCP server v{__version__}. Exposes paper search, "
            "deep review, bookmarks, curriculum, citation graph, and figure generation "
            "as tools. All calls act on behalf of the JWT user configured via "
            "JIPHYEONJEON_TOKEN."
        ),
    )
    factory = _build_client_factory(settings)
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
