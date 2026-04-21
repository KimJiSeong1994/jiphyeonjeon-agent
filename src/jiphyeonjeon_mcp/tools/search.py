"""search_papers tool — wraps POST /api/search.

Backend contract (routers/search.py SearchRequest):
    query, max_results, sources, sort_by, year_start, year_end, author,
    category, fast_mode, save_papers, collect_references, extract_texts
Response (SearchResponse): ``{results: {source: [papers]}, total, query_analysis}``.
We flatten ``results`` into a single ranked list so Claude doesn't have to
inspect per-source grouping.
"""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from jiphyeonjeon_mcp.capability import ServerCapabilities
from jiphyeonjeon_mcp.tools import ClientFactory


def register(
    mcp: FastMCP,
    client_factory: ClientFactory,
    capabilities: ServerCapabilities,
) -> list[str]:
    if not capabilities.supports("search"):
        return []

    @mcp.tool()
    async def search_papers(
        query: Annotated[
            str,
            Field(min_length=1, description="Natural-language query (Korean or English)."),
        ],
        max_results: Annotated[
            int,
            Field(ge=1, le=50, description="Max number of results (default 10, cap 50)."),
        ] = 10,
        sources: Annotated[
            list[str] | None,
            Field(
                default=None,
                description=(
                    "Optional paper sources to query. Allowed: arxiv, connected_papers, "
                    "google_scholar, openalex, dblp, openalex_korean. "
                    "Defaults to backend behavior."
                ),
            ),
        ] = None,
        year_start: Annotated[
            int | None,
            Field(default=None, description="Earliest publication year (inclusive)."),
        ] = None,
        year_end: Annotated[
            int | None,
            Field(default=None, description="Latest publication year (inclusive)."),
        ] = None,
        fast_mode: Annotated[
            bool,
            Field(
                default=True,
                description=(
                    "If True, skip heavy reranking/save paths for faster response. "
                    "Set False when you want save_papers and reference collection."
                ),
            ),
        ] = True,
    ) -> dict[str, Any]:
        """Search academic papers via 집현전's hybrid retrieval + reranking pipeline.

        Returns ``{papers, total, query_analysis}`` where ``papers`` is a flattened
        and deduplicated list from all source-grouped buckets. Use ``get_paper``
        with a paper id from these results to fetch full metadata.
        """
        body: dict[str, Any] = {
            "query": query,
            "max_results": max_results,
            "fast_mode": fast_mode,
            # In fast mode we also skip auto-save to keep latency low; user can
            # explicitly bookmark interesting papers afterwards.
            "save_papers": not fast_mode,
        }
        if sources:
            body["sources"] = sources
        if year_start is not None:
            body["year_start"] = year_start
        if year_end is not None:
            body["year_end"] = year_end

        async with await client_factory() as client:
            data = await client.post_json(
                "/api/search",
                body,
                operation="search papers",
            )

        # Backend returns {results: {source: [papers]}, total, query_analysis}.
        # Flatten into a single list for easier Claude consumption, but keep
        # the source grouping available for callers that need it.
        if isinstance(data, dict):
            grouped = data.get("results") or {}
            if isinstance(grouped, dict):
                flat: list[dict[str, Any]] = []
                for source_name, papers in grouped.items():
                    if isinstance(papers, list):
                        for paper in papers:
                            if isinstance(paper, dict):
                                paper.setdefault("source", source_name)
                                flat.append(paper)
                return {
                    "papers": flat,
                    "total": data.get("total", len(flat)),
                    "query_analysis": data.get("query_analysis"),
                    "by_source": grouped,
                }
            # Some endpoints may already return a flat list in `results`.
            if isinstance(grouped, list):
                return {"papers": grouped, "total": data.get("total", len(grouped))}
            return dict(data)
        return {"papers": data if isinstance(data, list) else [], "total": 0}

    return ["search_papers"]
