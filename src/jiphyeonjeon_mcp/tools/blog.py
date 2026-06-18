"""create_blog_draft tool — wraps POST /api/blog/posts.

Admin-only on 집현전 side. Non-admin JWT holders see a 403 which the auth
layer translates to a clear ``권한 부족`` MCP error.

Backend contract (routers/blog.py PostCreateRequest):
    title, content, excerpt, tags, thumbnail_url, published (bool, default True)
We force ``published=False`` so this tool always creates a DRAFT that the
admin can review and publish from the web UI.
"""

from __future__ import annotations

from typing import Annotated, Any

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
    if not capabilities.supports("blog"):
        return []

    @mcp.tool(annotations=ToolAnnotations(title="Create blog draft", readOnlyHint=False))
    async def create_blog_draft(
        title: Annotated[
            str,
            Field(min_length=1, max_length=300, description="Blog post title."),
        ],
        content: Annotated[
            str,
            Field(min_length=10, description="Markdown body."),
        ],
        excerpt: Annotated[
            str,
            Field(default="", max_length=500, description="Short summary (<= 500 chars)."),
        ] = "",
        tags: Annotated[
            list[str] | None,
            Field(default=None, description="Optional tags."),
        ] = None,
        thumbnail_url: Annotated[
            str | None,
            Field(default=None, description="Optional cover image URL."),
        ] = None,
    ) -> dict[str, Any]:
        """Write up a paper or topic as a blog post DRAFT (always saved unpublished).
        Admin JWT required.

        Use when the user wants to turn research into a post, write-up, or research note
        ("draft a blog post about this paper", "블로그 글로 정리해줘"). Always creates an
        unpublished draft — the admin reviews and publishes from the web UI.

        Returns the created post (id, slug, created_at). Non-admin JWTs get a clear
        Korean permission error (403).
        """
        body: dict[str, Any] = {
            "title": title,
            "content": content,
            "excerpt": excerpt,
            "published": False,
        }
        if tags:
            body["tags"] = tags
        if thumbnail_url:
            body["thumbnail_url"] = thumbnail_url
        async with await client_factory() as client:
            data = await client.post_json(
                "/api/blog/posts",
                body,
                operation="create blog draft",
            )
        return data if isinstance(data, dict) else {"post": data}

    return ["create_blog_draft"]
