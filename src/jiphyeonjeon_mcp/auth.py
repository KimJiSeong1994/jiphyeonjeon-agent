"""HTTP status → MCP error translation.

We keep this in a dedicated module so tool handlers don't duplicate the
status-code-to-user-message mapping.
"""

from __future__ import annotations

import httpx
from mcp.shared.exceptions import McpError
from mcp.types import INTERNAL_ERROR, INVALID_PARAMS, ErrorData


def raise_for_http_error(response: httpx.Response, operation: str) -> None:
    """Translate a non-2xx 집현전 response into an ``McpError``.

    Parameters
    ----------
    response:
        The httpx response. If ``response.is_success`` is True this is a no-op.
    operation:
        Short human-readable label for the attempted action (e.g. "search papers").
        Shown in the error message so Claude can explain what failed to the user.
    """
    if response.is_success:
        return

    status = response.status_code
    detail = _safe_detail(response)

    if status == 401:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message=(
                    f"집현전 인증 실패 ({operation}). "
                    "JIPHYEONJEON_TOKEN 이 만료되었거나 유효하지 않습니다. "
                    "POST /api/auth/login 으로 새 JWT 를 발급받고 "
                    "환경 변수 JIPHYEONJEON_TOKEN 을 갱신하세요."
                ),
            )
        )

    if status == 403:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message=(
                    f"권한 부족 ({operation}). "
                    f"이 작업에는 더 높은 권한(예: admin)이 필요합니다. 응답: {detail}"
                ),
            )
        )

    if status == 404:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message=f"리소스를 찾을 수 없습니다 ({operation}): {detail}",
            )
        )

    if status == 422:
        raise McpError(
            ErrorData(
                code=INVALID_PARAMS,
                message=f"요청 검증 실패 ({operation}): {detail}",
            )
        )

    if status == 429:
        retry_after = response.headers.get("Retry-After", "unknown")
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=(
                    f"집현전 요청 한도 초과 ({operation}). "
                    f"Retry-After: {retry_after} 초. 잠시 후 다시 시도하세요."
                ),
            )
        )

    if 500 <= status < 600:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"집현전 서버 오류 HTTP {status} ({operation}): {detail}",
            )
        )

    raise McpError(
        ErrorData(
            code=INTERNAL_ERROR,
            message=f"예기치 않은 응답 HTTP {status} ({operation}): {detail}",
        )
    )


def _safe_detail(response: httpx.Response) -> str:
    """Extract a human-readable error string without leaking huge bodies.

    Prompt-injection defense: backend-controlled strings are wrapped in an
    explicit ``[backend said: ...]`` frame and stripped of control characters
    so a malicious ``detail`` cannot impersonate MCP instructions to Claude.
    """
    try:
        data = response.json()
    except Exception:
        data = None
    raw: str
    if isinstance(data, dict):
        detail = data.get("detail") or data.get("error") or data.get("message")
        raw = str(detail) if detail else (response.text or "")
    else:
        raw = response.text or ""
    if not raw:
        return f"(empty body, HTTP {response.status_code})"
    # Strip control characters (including newlines) that could restructure prompts.
    cleaned = "".join(ch for ch in raw if ch == " " or (ch.isprintable() and ch != "\n"))
    cleaned = cleaned.strip()[:400]
    if not cleaned:
        return f"(unprintable body, HTTP {response.status_code})"
    return f"[backend said: {cleaned}]"
