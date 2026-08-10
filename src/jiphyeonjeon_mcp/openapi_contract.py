"""Semantic OpenAPI gate for the REST operations used by MCP tools."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class OperationRequirement:
    method: str
    path: str
    request_fields: frozenset[str] = frozenset()
    response_fields: frozenset[str] = frozenset()


REQUIRED_OPERATIONS: tuple[OperationRequirement, ...] = (
    OperationRequirement(
        "get",
        "/api/version",
        response_fields=frozenset({"version", "capabilities", "mcp_min_client"}),
    ),
    OperationRequirement(
        "post",
        "/api/search",
        request_fields=frozenset({"query", "max_results", "year_start", "year_end"}),
    ),
    OperationRequirement("get", "/api/papers/{paper_id}"),
    OperationRequirement(
        "post",
        "/api/deep-review",
        request_fields=frozenset({"paper_ids", "num_researchers", "fast_mode"}),
    ),
    OperationRequirement("get", "/api/deep-review/status/{session_id}"),
    OperationRequirement("get", "/api/deep-review/report/{session_id}"),
    OperationRequirement("get", "/api/bookmarks"),
    OperationRequirement(
        "post",
        "/api/bookmarks/from-paper",
        request_fields=frozenset(
            {"title", "authors", "year", "venue", "arxiv_id", "doi", "topic", "tags", "context"}
        ),
    ),
    OperationRequirement("delete", "/api/bookmarks/{bookmark_id}"),
    OperationRequirement(
        "post",
        "/api/bookmarks/{bookmark_id}/citation-tree",
        request_fields=frozenset({"depth", "max_per_direction"}),
    ),
    OperationRequirement(
        "post",
        "/api/curricula/generate",
        request_fields=frozenset({"topic", "difficulty", "num_modules"}),
    ),
    OperationRequirement(
        "post",
        "/api/autofigure/method-to-svg",
        request_fields=frozenset({"method_text", "paper_title", "optimize_iterations"}),
    ),
    OperationRequirement(
        "post",
        "/api/blog/posts",
        request_fields=frozenset(
            {"title", "content", "excerpt", "tags", "thumbnail_url", "published", "category"}
        ),
    ),
    OperationRequirement(
        "put",
        "/api/blog/posts/{post_id}",
        request_fields=frozenset(
            {
                "title",
                "content",
                "excerpt",
                "tags",
                "thumbnail_url",
                "slug",
                "published",
                "category",
            }
        ),
    ),
)


def _resolve_schema(document: dict[str, Any], schema: Any) -> dict[str, Any]:
    if not isinstance(schema, dict):
        return {}
    reference = schema.get("$ref")
    if not isinstance(reference, str):
        return schema
    if not reference.startswith("#/"):
        return {}
    current: Any = document
    for part in reference[2:].split("/"):
        if not isinstance(current, dict):
            return {}
        current = current.get(part.replace("~1", "/").replace("~0", "~"))
    return current if isinstance(current, dict) else {}


def _json_schema(content: Any, document: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(content, dict):
        return {}
    media = content.get("application/json")
    if not isinstance(media, dict):
        return {}
    return _resolve_schema(document, media.get("schema"))


def _request_schema(operation: dict[str, Any], document: dict[str, Any]) -> dict[str, Any]:
    request_body = operation.get("requestBody")
    if not isinstance(request_body, dict):
        return {}
    request_body = _resolve_schema(document, request_body)
    return _json_schema(request_body.get("content"), document)


def _response_schema(operation: dict[str, Any], document: dict[str, Any]) -> dict[str, Any]:
    responses = operation.get("responses")
    if not isinstance(responses, dict):
        return {}
    response = responses.get("200") or responses.get("201")
    if not isinstance(response, dict):
        return {}
    response = _resolve_schema(document, response)
    return _json_schema(response.get("content"), document)


def _missing_fields(schema: dict[str, Any], expected: frozenset[str]) -> list[str]:
    properties = schema.get("properties")
    actual = set(properties) if isinstance(properties, dict) else set()
    return sorted(expected - actual)


def validate_openapi_contract(document: dict[str, Any]) -> list[str]:
    """Return human-readable compatibility errors; an empty list means compatible."""
    errors: list[str] = []
    paths = document.get("paths")
    if not isinstance(paths, dict):
        return ["OpenAPI document has no paths object"]

    for requirement in REQUIRED_OPERATIONS:
        path_item = paths.get(requirement.path)
        operation = path_item.get(requirement.method) if isinstance(path_item, dict) else None
        label = f"{requirement.method.upper()} {requirement.path}"
        if not isinstance(operation, dict):
            errors.append(f"missing operation: {label}")
            continue
        if requirement.request_fields:
            missing = _missing_fields(
                _request_schema(operation, document), requirement.request_fields
            )
            if missing:
                errors.append(f"{label} request schema missing fields: {', '.join(missing)}")
        if requirement.response_fields:
            missing = _missing_fields(
                _response_schema(operation, document), requirement.response_fields
            )
            if missing:
                errors.append(f"{label} response schema missing fields: {', '.join(missing)}")
    return errors
