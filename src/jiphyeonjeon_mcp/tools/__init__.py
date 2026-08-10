"""MCP tool handlers grouped by 집현전 capability domain.

Each submodule exposes a ``register(mcp, client_factory, capabilities)``
function. ``server.py`` iterates over all domains and lets each one decide
whether to register its tools based on the negotiated capability set.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from mcp.server.fastmcp import FastMCP

from jiphyeonjeon_mcp.capability import ServerCapabilities
from jiphyeonjeon_mcp.client import JiphyeonjeonClient

ClientFactory = Callable[[], Awaitable[JiphyeonjeonClient]]


def register_all(
    mcp: FastMCP,
    client_factory: ClientFactory,
    capabilities: ServerCapabilities,
) -> list[str]:
    """Register every tool module, returning the list of active tool names."""
    from jiphyeonjeon_mcp.tools import (  # noqa: PLC0415 — avoid cycles at import time
        blog,
        bookmarks,
        curriculum,
        explore,
        figure,
        papers,
        review,
        search,
    )

    registered: list[str] = []
    for module in (search, papers, review, bookmarks, curriculum, explore, figure, blog):
        registered.extend(module.register(mcp, client_factory, capabilities))
    _forbid_unknown_tool_arguments(mcp, registered)
    return registered


def _forbid_unknown_tool_arguments(mcp: FastMCP, names: list[str]) -> None:
    """Make FastMCP/Pydantic reject rather than discard undeclared arguments.

    MCP 1.x builds a separate Pydantic argument model per decorated function,
    with Pydantic's default ``extra='ignore'`` behavior. Tightening each model
    after registration keeps runtime validation and advertised JSON Schema in
    sync (`additionalProperties: false`).
    """
    for name in names:
        tool = mcp._tool_manager.get_tool(name)
        if tool is None:  # pragma: no cover - list comes from successful registration
            continue
        arg_model = tool.fn_metadata.arg_model
        arg_model.model_config["extra"] = "forbid"
        arg_model.model_rebuild(force=True)
        tool.parameters = arg_model.model_json_schema(by_alias=True)
