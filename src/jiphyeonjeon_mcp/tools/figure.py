"""generate_figure tool — wraps POST /api/autofigure/method-to-svg.

Backend contract (routers/autofigure.py):
    Request (MethodToSvgRequest): method_text, paper_title, style_hints, optimize_iterations
    Response (MethodToSvgResponse): success, svg_content, figure_png_b64, error

The AutoFigure microservice is a separate process; if unreachable the backend
returns 503 which the auth layer turns into a clear user-facing MCP error.
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
    if not capabilities.supports("autofigure"):
        return []

    @mcp.tool()
    async def generate_figure(
        method_text: Annotated[
            str,
            Field(
                min_length=10,
                description="Methodology description to convert into a diagram.",
            ),
        ],
        paper_title: Annotated[
            str,
            Field(default="", description="Optional paper title for framing context."),
        ] = "",
        optimize_iterations: Annotated[
            int,
            Field(ge=1, le=10, description="LLM refinement passes (1-10, default 1)."),
        ] = 1,
    ) -> dict[str, Any]:
        """Convert a methodology description into an SVG diagram via AutoFigure.

        Returns ``{success, svg_content, figure_png_b64, error}``. If AutoFigure
        is offline the backend returns HTTP 503 and the caller sees a structured
        MCP error — retry after the microservice is back.
        """
        body: dict[str, Any] = {
            "method_text": method_text,
            "paper_title": paper_title,
            "optimize_iterations": optimize_iterations,
        }
        async with await client_factory() as client:
            data = await client.post_json(
                "/api/autofigure/method-to-svg",
                body,
                operation="generate methodology figure",
            )
        return data if isinstance(data, dict) else {"svg_content": data}

    return ["generate_figure"]
