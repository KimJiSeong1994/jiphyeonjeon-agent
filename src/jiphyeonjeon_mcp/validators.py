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

from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS, ErrorData

# Allow: letters, digits, dot, dash, underscore, colon, slash-in-arxiv (none),
# forward-slash is NOT in the allowlist — DOIs like 10.1038/nphys1170 get dropped.
# Real DOIs have at most one '/' and we do not currently expose any tool that
# needs to accept a raw DOI in a path segment, so this tightened allowlist is safe.
_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{1,200}$")


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
