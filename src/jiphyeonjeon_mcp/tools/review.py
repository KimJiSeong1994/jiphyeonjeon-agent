"""Deep review tools — start_review + get_review_status (async task_id polling).

Backend contract (routers/reviews.py DeepReviewRequest):
    paper_ids (required), papers, num_researchers, model, fast_mode
"""

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
    if not capabilities.supports("deep_review"):
        return []

    @mcp.tool()
    async def start_review(
        paper_ids: Annotated[
            list[str],
            Field(min_length=1, description="One or more paper ids (from search_papers)."),
        ],
        num_researchers: Annotated[
            int,
            Field(ge=1, le=6, description="Number of parallel reviewer agents (default 3)."),
        ] = 3,
        fast_mode: Annotated[
            bool,
            Field(
                default=True,
                description=(
                    "If True, single-pass summarization (~10-30s). "
                    "If False, multi-stage deep review (~60-120s per paper)."
                ),
            ),
        ] = True,
    ) -> dict[str, Any]:
        """Queue a deep review. Returns a session_id to poll with ``get_review_status``.

        The review runs as a background job on 집현전. Typical completion: 1-8 minutes
        depending on paper count and fast_mode. Call ``get_review_status`` every 30-60s
        (exponential backoff recommended) until ``status == 'completed'`` or ``'failed'``.
        """
        # Validate each paper_id to block path-traversal-style injection downstream.
        safe_ids = [validate_id(pid, field_name="paper_ids[]") for pid in paper_ids]
        body = {
            "paper_ids": safe_ids,
            "num_researchers": num_researchers,
            "fast_mode": fast_mode,
        }
        async with await client_factory() as client:
            data = await client.post_json(
                "/api/deep-review",
                body,
                operation="start deep review",
            )
        return data if isinstance(data, dict) else {"session_id": data}

    @mcp.tool()
    async def get_review_status(
        session_id: Annotated[
            str,
            Field(description="session_id returned by start_review."),
        ],
    ) -> dict[str, Any]:
        """Poll deep review progress.

        Returns ``{session_id, status, progress, report_available, ...}``. When
        ``report_available`` is True, the full markdown report can be fetched
        via ``/api/deep-review/report/{session_id}``.
        """
        safe_session = validate_id(session_id, field_name="session_id")
        async with await client_factory() as client:
            data = await client.get_json(
                f"/api/deep-review/status/{safe_session}",
                operation=f"poll review {safe_session}",
            )
        return data if isinstance(data, dict) else {"raw": data}

    return ["start_review", "get_review_status"]
