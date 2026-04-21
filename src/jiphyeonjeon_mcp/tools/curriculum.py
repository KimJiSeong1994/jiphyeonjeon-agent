"""create_curriculum tool — wraps POST /api/curricula/generate."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from jiphyeonjeon_mcp.capability import ServerCapabilities
from jiphyeonjeon_mcp.tools import ClientFactory


def register(
    mcp: FastMCP,
    client_factory: ClientFactory,
    capabilities: ServerCapabilities,
) -> list[str]:
    if not capabilities.supports("curriculum"):
        return []

    @mcp.tool()
    async def create_curriculum(
        topic: Annotated[
            str,
            Field(description="Topic to build a curriculum on (e.g. 'GraphRAG')."),
        ],
        difficulty: Annotated[
            Literal["beginner", "intermediate", "advanced"],
            Field(description="Target learner level."),
        ] = "intermediate",
        num_modules: Annotated[
            int,
            Field(ge=2, le=15, description="Number of modules/weeks (2-15, default 5)."),
        ] = 5,
    ) -> dict[str, Any]:
        """Generate a structured learning curriculum for the given topic.

        Long-running (~30-90s). Returns modules with recommended papers, goals,
        and checkpoints. The call blocks until completion — for streamed
        progress, use the SSE variant directly against 집현전 (not exposed as MCP).
        """
        body = {
            "topic": topic,
            "difficulty": difficulty,
            "num_modules": num_modules,
        }
        async with await client_factory() as client:
            # Curriculum generation blocks on multi-step LLM + OpenAlex lookup;
            # override per-call timeout regardless of base Settings.timeout.
            data = await client.post_json(
                "/api/curricula/generate",
                body,
                operation="generate curriculum",
                timeout=180.0,
            )
        return data if isinstance(data, dict) else {"curriculum": data}

    return ["create_curriculum"]
