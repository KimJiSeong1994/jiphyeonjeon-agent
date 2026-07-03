"""Parameter validation helpers for tool inputs.

httpx normalizes ``../`` segments before sending, so raw f-string path
interpolation would let a user-controlled id reach unintended backend routes
(e.g. ``get_paper("../admin/users")`` → ``GET /api/admin/users``).

All tools that embed an id into a URL path MUST pass it through
``validate_id`` first. The allowlist covers the realistic shape of backend
ids (arXiv ids ``2401.12345``, DOIs ``10.1038/...``, UUIDs, hyphenated slugs)
while rejecting any path-traversal or whitespace characters.
"""

from __future__ import annotations

import re
from typing import NoReturn
from urllib.parse import unquote, urlparse

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData

# Allow: letters, digits, dot, dash, underscore, colon, slash-in-arxiv (none),
# forward-slash is NOT in the allowlist — DOIs like 10.1038/nphys1170 get dropped.
# Real DOIs have at most one '/' and we do not currently expose any tool that
# needs to accept a raw DOI in a path segment, so this tightened allowlist is safe.
_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{1,200}$")
_ARXIV_NEW_RE = re.compile(r"^\d{4}\.\d{4,5}(?:v\d+)?$")
_ARXIV_OLD_RE = re.compile(r"^[a-z-]+(?:\.[A-Z]{2})?/\d{7}(?:v\d+)?$")
_DOI_RE = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Za-z0-9]+$")


def validate_id(value: str, *, field_name: str) -> str:
    """Return ``value`` unchanged if it matches the id allowlist, else raise ``McpError``.

    Rejects values containing ``/``, ``..``, whitespace, quotes, or any character
    outside ``[A-Za-z0-9._:-]`` — these are all prerequisites for URL-path
    traversal or injection into upstream queries. ``..`` (and anything
    containing ``..``) is rejected even though individual dots are allowed.
    """
    if (
        not isinstance(value, str)
        or not _ID_RE.fullmatch(value)
        or ".." in value
        or value.startswith(".")
        or value.startswith("-")
    ):
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message=(
                    f"'{field_name}' 값이 허용된 형식이 아닙니다. "
                    "arXiv id, 숫자, 점·대시·밑줄·콜론만 사용 가능 (길이 1-200)."
                ),
            )
        )
    return value


def validate_paper_reference(value: str, *, field_name: str = "paper_id") -> str:
    """Normalize and validate a paper reference used in JSON request bodies.

    Unlike ``validate_id``, this accepts user-facing paper references that are
    never interpolated into a URL path by this MCP server: arXiv abs/pdf URLs,
    new arXiv ids (``2401.12345v2``), old arXiv ids (``cs/0501001``), and DOI
    strings. Path traversal/control characters are still rejected.
    """
    normalized = _normalize_paper_reference(value)
    if normalized is None or ".." in normalized or any(ch.isspace() for ch in normalized):
        _raise_invalid_paper_reference(field_name)
    assert normalized is not None

    if (
        _ID_RE.fullmatch(normalized)
        or _ARXIV_OLD_RE.fullmatch(normalized)
        or _DOI_RE.fullmatch(normalized)
    ):
        return normalized

    _raise_invalid_paper_reference(field_name)


def _normalize_paper_reference(value: str) -> str | None:
    if not isinstance(value, str):
        return None
    raw = value.strip()
    if not raw:
        return None

    parsed = urlparse(raw)
    host = parsed.netloc.lower()
    if parsed.scheme in {"http", "https"} and host in {"arxiv.org", "www.arxiv.org"}:
        path = unquote(parsed.path).strip("/")
        for prefix in ("abs/", "pdf/"):
            if path.startswith(prefix):
                arxiv_id = path.removeprefix(prefix)
                if arxiv_id.endswith(".pdf"):
                    arxiv_id = arxiv_id.removesuffix(".pdf")
                return arxiv_id
        return None

    if parsed.scheme in {"http", "https"} and host in {"doi.org", "dx.doi.org"}:
        return unquote(parsed.path).strip("/")

    return raw


def _raise_invalid_paper_reference(field_name: str) -> NoReturn:
    raise McpError(
        ErrorData(
            code=INVALID_PARAMS,
            message=(
                f"'{field_name}' 값이 허용된 논문 식별자 형식이 아닙니다. "
                "arXiv id/URL, DOI/DOI URL, 또는 숫자·점·대시·밑줄·콜론 기반 id만 "
                "사용 가능 (길이 1-200)."
            ),
        )
    )
