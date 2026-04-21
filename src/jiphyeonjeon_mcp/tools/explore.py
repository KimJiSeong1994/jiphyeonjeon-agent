"""explore_related tool — wraps POST /api/bookmarks/{id}/citation-tree."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from jiphyeonjeon_mcp.capability import ServerCapabilities
from jiphyeonjeon_mcp.tools import ClientFactory
from jiphyeonjeon_mcp.validators import validate_id


def register(
    mcp: FastMCP,
    client_factory: ClientFactory,
    capabilities: ServerCapabilities,
) -> list[str]:
    if not capabilities.supports("explore"):
        return []

    @mcp.tool()
    async def explore_related(
        bookmark_id: Annotated[
            str,
            Field(description="Bookmark id to anchor the exploration around."),
        ],
        depth: Annotated[
            int,
            Field(ge=1, le=3, description="Graph expansion depth (1-3)."),
        ] = 2,
        max_per_direction: Annotated[
            int,
            Field(ge=1, le=30, description="Max papers per hop/direction (1-30)."),
        ] = 10,
    ) -> dict[str, Any]:
        """Build a citation graph (forward + backward) around a bookmarked paper.

        Uses Semantic Scholar under the hood. Slow on first run (~2-5s per paper);
        subsequent calls hit the cached tree until invalidated.
        """
        safe_bid = validate_id(bookmark_id, field_name="bookmark_id")
        body = {"depth": depth, "max_per_direction": max_per_direction}
        async with await client_factory() as client:
            data = await client.post_json(
                f"/api/bookmarks/{safe_bid}/citation-tree",
                body,
                operation=f"explore citations from bookmark {safe_bid}",
            )
        return data if isinstance(data, dict) else {"tree": data}

    return ["explore_related"]
