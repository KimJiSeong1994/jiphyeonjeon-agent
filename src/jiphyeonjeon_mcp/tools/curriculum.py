"""create_curriculum tool — wraps POST /api/curricula/generate."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
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

    @mcp.tool(
        annotations=ToolAnnotations(
            title="Create learning curriculum", readOnlyHint=False, openWorldHint=True
        )
    )
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
        """Generate a structured, multi-module learning curriculum (study roadmap) for a
        topic — ordered papers, goals, and checkpoints per module.

        Use when the user wants a study plan, learning path, reading list, syllabus, or
        roadmap to learn a field ("how do I learn diffusion models", "GraphRAG 공부 순서
        짜줘", "study plan for RAG").

        Long-running (~30-90s); the call blocks until completion. Returns modules with
        recommended papers, goals, and checkpoints.
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
