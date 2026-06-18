"""get_paper tool — wraps GET /api/papers/{id}."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
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

    @mcp.tool(annotations=ToolAnnotations(title="Get paper", readOnlyHint=True))
    async def get_paper(
        paper_id: Annotated[
            str,
            Field(description="집현전 doc_id, arxiv id, or DOI. Raw string — no URL escaping."),
        ],
    ) -> dict[str, Any]:
        """Fetch full metadata for one specific, known paper (by arXiv id, DOI, or
        집현전 doc_id).

        Use when the user references a single concrete paper and you already have its id
        ("get details for arXiv 2310.06825", "이 논문 정보 보여줘"). To discover papers from a
        topic or keywords, use ``search_papers`` first.

        Returns the paper record (title, authors, abstract, venue, year, pdf_url,
        embeddings metadata). Raises a user-facing message when the paper is not indexed.
        """
        safe_pid = validate_id(paper_id, field_name="paper_id")
        async with await client_factory() as client:
            data = await client.get_json(
                f"/api/papers/{safe_pid}",
                operation=f"get paper {safe_pid}",
            )
        return data if isinstance(data, dict) else {"paper": data}

    return ["get_paper"]
