"""get_paper tool — wraps GET /api/papers/{id}."""

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
    if not capabilities.supports("papers"):
        return []

    @mcp.tool()
    async def get_paper(
        paper_id: Annotated[
            str,
            Field(description="집현전 doc_id, arxiv id, or DOI. Raw string — no URL escaping."),
        ],
    ) -> dict[str, Any]:
        """Fetch full metadata for a single paper stored in 집현전.

        Returns the paper record (title, authors, abstract, venue, year,
        pdf_url, embeddings metadata). Raises with a user-facing message when
        the paper is not indexed yet — use ``search_papers`` first, then call
        this with a specific id from the search result.
        """
        safe_pid = validate_id(paper_id, field_name="paper_id")
        async with await client_factory() as client:
            data = await client.get_json(
                f"/api/papers/{safe_pid}",
                operation=f"get paper {safe_pid}",
            )
        return data if isinstance(data, dict) else {"paper": data}

    return ["get_paper"]
