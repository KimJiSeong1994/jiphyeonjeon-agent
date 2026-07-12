"""create_blog_draft tool — wraps POST /api/blog/posts.

Admin-only on 집현전 side. Non-admin JWT holders see a 403 which the auth
layer translates to a clear ``권한 부족`` MCP error.

Backend contract (routers/blog.py PostCreateRequest):
    title, content, excerpt, tags, thumbnail_url, published (bool, default True),
    category ("paper-review" | "engineering", default "engineering")
We force ``published=False`` so this tool always creates a DRAFT that the
admin can review and publish from the web UI. Since this tool is used to turn
papers into posts, we default ``category="paper-review"``.
"""

from __future__ import annotations

import re
from typing import Annotated, Any, Literal

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from jiphyeonjeon_mcp.capability import ServerCapabilities
from jiphyeonjeon_mcp.tools import ClientFactory

# GEO citability lint. AI answer engines extract self-contained,
# entity-anchored sentences; drafts that open with "본 문서는…" or bury the
# headline numbers in tables get skipped. These heuristics do not block draft
# creation — they surface warnings the calling agent should fix in place.
_META_LEAD_RE = re.compile(r"^\**\s*(본\s?문서|이\s?논문|이\s?글|본\s?글|해당\s?논문)")
_SKIP_LINE_RE = re.compile(r"^(#|\*\*(Paper|Abstract|저자|출처)\b|>|!\[|\||-{3,}$)")


def _citability_warnings(content: str, category: str) -> list[str]:
    """Return GEO citability warnings for a paper-review draft body."""
    if category != "paper-review":
        return []
    warnings: list[str] = []

    first_paragraph = ""
    for raw in content.split("\n"):
        line = raw.strip()
        if not line or _SKIP_LINE_RE.match(line):
            continue
        first_paragraph = line
        break

    if _META_LEAD_RE.match(first_paragraph):
        warnings.append(
            "정의 리드 없음: 본문 첫 문장이 '본 문서/이 논문'으로 시작합니다. "
            "'**[엔티티명]**는 …하는 [범주]다. [핵심 수치 1개].' 형식의 "
            "정의 문장을 맨 앞에 두세요."
        )
    elif "**" not in first_paragraph[:120]:
        warnings.append(
            "정의 리드 확인 필요: 첫 문단에 굵게 표시된 엔티티명(**X**)이 "
            "없습니다. 첫 문장의 주어를 리뷰 대상 기법 이름으로 두세요."
        )

    if "TL;DR" not in content:
        warnings.append(
            "TL;DR 없음: Executive Summary 표 바로 아래에 '**TL;DR** — "
            "(1) 무엇 (2) 헤드라인 수치 (3) 언제 유리한지+한계' 3문장을 "
            "추가하세요. 각 문장은 엔티티명으로 시작하는 자기완결 문장이어야 "
            "합니다."
        )
    return warnings


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
        category: Annotated[
            Literal["paper-review", "engineering"],
            Field(
                default="paper-review",
                description=(
                    "Content type shown as a blog section: 'paper-review' for a "
                    "deep review of a specific paper (default), or 'engineering' "
                    "for a 집현전 product / development writeup."
                ),
            ),
        ] = "paper-review",
    ) -> dict[str, Any]:
        """Write up a paper or topic as a blog post DRAFT (always saved unpublished).
        Admin JWT required.

        Use when the user wants to turn research into a post, write-up, or research note
        ("draft a blog post about this paper", "블로그 글로 정리해줘"). Always creates an
        unpublished draft — the admin reviews and publishes from the web UI.

        ``category`` defaults to "paper-review" (a review of a specific paper). Pass
        "engineering" instead when writing a 집현전 product / development note.

        GEO citability requirements for paper-review drafts (AI answer engines
        extract entity-anchored, self-contained sentences — drafts missing these
        get created but flagged in ``citability_warnings``):
        1. 정의 리드: the first body sentence must define the reviewed method
           with the entity name as subject — "**DeepWalk**는 …하는 방법이다.
           [핵심 수치 1개]." Never open with "본 문서는/이 논문은".
        2. TL;DR: 3 self-contained sentences right below the Executive Summary
           table — (1) 무엇 (2) 헤드라인 수치 (3) 언제 유리한지 + 한계 1개.
        3. 표-산문 미러: every benchmark table's headline numbers must also
           appear verbatim in one prose sentence near the table.
        4. Section leads must not start with dangling 이/그/이것 references.

        Returns the created post (id, slug, created_at) plus
        ``citability_warnings`` — if non-empty, fix the draft content and
        update it rather than leaving the warnings unresolved.
        """
        body: dict[str, Any] = {
            "title": title,
            "content": content,
            "excerpt": excerpt,
            "published": False,
            "category": category,
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
        result = data if isinstance(data, dict) else {"post": data}
        warnings = _citability_warnings(content, category)
        if warnings:
            result = {**result, "citability_warnings": warnings}
        return result

    return ["create_blog_draft"]
