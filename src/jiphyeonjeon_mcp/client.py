"""HTTP client wrapping the 집현전 REST API.

One `JiphyeonjeonClient` instance is shared by all tool handlers. It owns the
underlying ``httpx.AsyncClient``, injects the ``Authorization: Bearer`` header
on every call, and translates non-2xx responses via :mod:`.auth`.
"""

from __future__ import annotations

from types import TracebackType
from typing import Any

import httpx
from mcp.shared.exceptions import McpError
from mcp.types import INTERNAL_ERROR, ErrorData

from jiphyeonjeon_mcp import __version__
from jiphyeonjeon_mcp.auth import raise_for_http_error
from jiphyeonjeon_mcp.config import Settings


class JiphyeonjeonClient:
    """Thin async HTTP client with auth header + error translation.

    Usage::

        async with JiphyeonjeonClient(settings) as client:
            data = await client.post_json("/api/search", {"query": "..."},
                                          operation="search papers")
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> JiphyeonjeonClient:
        self._client = httpx.AsyncClient(
            base_url=self._settings.normalized_base_url,
            timeout=self._settings.timeout,
            verify=self._settings.verify_ssl,
            headers=self._auth_headers(),
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _auth_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._settings.token.get_secret_value()}",
            "Accept": "application/json",
            "User-Agent": f"jiphyeonjeon-mcp/{__version__}",
        }

    async def get_json(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        operation: str,
    ) -> Any:
        """GET ``path`` with query params, return parsed JSON or raise ``McpError``."""
        response = await self._request("GET", path, params=params, operation=operation)
        return response.json()

    async def post_json(
        self,
        path: str,
        body: dict[str, Any] | None = None,
        *,
        operation: str,
        timeout: float | None = None,  # noqa: ASYNC109 — forwarded to httpx
    ) -> Any:
        """POST JSON body to ``path``, return parsed JSON or raise ``McpError``.

        ``timeout`` overrides ``Settings.timeout`` for this one call only — use
        for long-running endpoints (curriculum generate, deep review start).
        """
        response = await self._request(
            "POST", path, json=body, operation=operation, timeout=timeout,
        )
        if not response.content:
            return None
        return response.json()

    async def delete(
        self,
        path: str,
        *,
        operation: str,
    ) -> Any:
        """DELETE ``path``. Returns JSON if present, else None."""
        response = await self._request("DELETE", path, operation=operation)
        if response.content:
            try:
                return response.json()
            except Exception:
                return None
        return None

    async def _request(
        self,
        method: str,
        path: str,
        *,
        operation: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,  # noqa: ASYNC109 — forwarded to httpx
    ) -> httpx.Response:
        if self._client is None:
            raise RuntimeError("JiphyeonjeonClient used outside async context manager")
        kwargs: dict[str, Any] = {"params": params, "json": json}
        if timeout is not None:
            kwargs["timeout"] = timeout
        try:
            response = await self._client.request(method, path, **kwargs)
        except httpx.TimeoutException as exc:
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message=(
                        f"집현전 요청 타임아웃 ({operation}): "
                        f"{self._settings.timeout}s 내 응답 없음. "
                        "백엔드가 실행 중인지 확인하세요."
                    ),
                )
            ) from exc
        except httpx.RequestError as exc:
            # Connection refused, DNS failure, etc. Avoid leaking auth headers.
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message=(
                        f"집현전 네트워크 오류 ({operation}): {type(exc).__name__}. "
                        "JIPHYEONJEON_BASE_URL 설정과 백엔드 기동 여부를 확인하세요."
                    ),
                )
            ) from exc

        raise_for_http_error(response, operation)
        return response
