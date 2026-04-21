"""Bookmark tools — list/add/remove. Per-user scoped by JWT identity.

Backend contract notes:
- ``POST /api/bookmarks/from-paper`` takes `BookmarkFromPaperRequest` which
  requires ``title`` (no ``paper_id`` field). To keep the MCP surface
  convenient (``add_bookmark(paper_id=...)``), we first call
  ``GET /api/papers/{paper_id}`` to pull metadata, then POST the mapped body.
  A caller may also supply explicit metadata via ``paper``/``title``.
"""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData
from pydantic import Field

from jiphyeonjeon_mcp.capability import ServerCapabilities
from jiphyeonjeon_mcp.tools import ClientFactory
from jiphyeonjeon_mcp.validators import validate_id


def register(
    mcp: FastMCP,
    client_factory: ClientFactory,
    capabilities: ServerCapabilities,
) -> list[str]:
    if not capabilities.supports("bookmarks"):
        return []

    @mcp.tool()
    async def list_bookmarks() -> dict[str, Any]:
        """List the authenticated user's bookmarks with metadata.

        Returns ``{bookmarks: [{id, title, topic, tags, created_at, ...}]}``.
        Each bookmark is scoped to the JWT user — cannot list others'.
        """
        async with await client_factory() as client:
            data = await client.get_json("/api/bookmarks", operation="list bookmarks")
        return data if isinstance(data, dict) else {"bookmarks": data}

    @mcp.tool()
    async def add_bookmark(
        paper_id: Annotated[
            str | None,
            Field(
                default=None,
                description=(
                    "집현전 paper id to auto-resolve metadata via GET /api/papers/{id}. "
                    "Required unless ``title`` is provided explicitly."
                ),
            ),
        ] = None,
        title: Annotated[
            str | None,
            Field(default=None, description="Paper title (overrides resolved metadata)."),
        ] = None,
        authors: Annotated[
            list[str] | None,
            Field(default=None, description="Author names."),
        ] = None,
        year: Annotated[
            int | None,
            Field(default=None, description="Publication year."),
        ] = None,
        venue: Annotated[
            str | None,
            Field(default=None, description="Venue / journal / conference."),
        ] = None,
        arxiv_id: Annotated[
            str | None,
            Field(default=None, description="arXiv id if applicable."),
        ] = None,
        doi: Annotated[
            str | None,
            Field(default=None, description="DOI if applicable."),
        ] = None,
        topic: Annotated[
            str,
            Field(default="Claude Agent", description="Bookmark topic tag."),
        ] = "Claude Agent",
        tags: Annotated[
            list[str] | None,
            Field(default=None, description="Optional tags."),
        ] = None,
        context: Annotated[
            str | None,
            Field(default=None, description="Optional note explaining why this is bookmarked."),
        ] = None,
    ) -> dict[str, Any]:
        """Bookmark a paper for the authenticated user.

        Usage modes:
        1. ``add_bookmark(paper_id="arxiv-2401.1234")`` — resolves metadata via
           GET /api/papers/{paper_id}, then POSTs from-paper.
        2. ``add_bookmark(title=..., authors=..., year=...)`` — caller supplies
           metadata directly (useful when paper not yet in 집현전 index).
        3. Mix — explicit fields override resolved ones.

        Wraps ``POST /api/bookmarks/from-paper`` which requires at minimum ``title``.
        """
        resolved: dict[str, Any] = {}
        if paper_id is not None:
            safe_pid = validate_id(paper_id, field_name="paper_id")
            async with await client_factory() as client:
                paper_meta = await client.get_json(
                    f"/api/papers/{safe_pid}",
                    operation=f"resolve paper {safe_pid} for bookmark",
                )
            if isinstance(paper_meta, dict):
                resolved = paper_meta

        final_title = title or resolved.get("title")
        if not final_title:
            raise McpError(
                ErrorData(
                    code=INVALID_PARAMS,
                    message=(
                        "북마크 생성에 제목(title)이 필요합니다. "
                        "paper_id 로 자동 조회에 실패했거나, 명시적으로 title 을 지정하세요."
                    ),
                )
            )

        body: dict[str, Any] = {
            "title": final_title,
            "topic": topic,
        }
        final_authors = authors if authors is not None else resolved.get("authors")
        if final_authors:
            body["authors"] = list(final_authors)
        final_year = year if year is not None else resolved.get("year")
        if final_year is not None:
            body["year"] = int(final_year)
        final_venue = venue or resolved.get("venue")
        if final_venue:
            body["venue"] = final_venue
        final_arxiv = arxiv_id or resolved.get("arxiv_id")
        if final_arxiv:
            body["arxiv_id"] = final_arxiv
        final_doi = doi or resolved.get("doi")
        if final_doi:
            body["doi"] = final_doi
        if context:
            body["context"] = context
        if tags:
            body["tags"] = tags

        async with await client_factory() as client:
            data = await client.post_json(
                "/api/bookmarks/from-paper",
                body,
                operation="add bookmark",
            )
        return data if isinstance(data, dict) else {"bookmark": data}

    @mcp.tool()
    async def remove_bookmark(
        bookmark_id: Annotated[
            str,
            Field(description="Bookmark id (from list_bookmarks)."),
        ],
    ) -> dict[str, Any]:
        """Delete a bookmark. DESTRUCTIVE — 복구 불가. Ask user to confirm before calling.

        Scoped to the authenticated user — deleting someone else's bookmark
        returns 404 (집현전 hides existence to prevent enumeration).
        """
        safe_bid = validate_id(bookmark_id, field_name="bookmark_id")
        async with await client_factory() as client:
            data = await client.delete(
                f"/api/bookmarks/{safe_bid}",
                operation=f"remove bookmark {safe_bid}",
            )
        return {"deleted": True, "bookmark_id": safe_bid, "raw": data}

    return ["list_bookmarks", "add_bookmark", "remove_bookmark"]
