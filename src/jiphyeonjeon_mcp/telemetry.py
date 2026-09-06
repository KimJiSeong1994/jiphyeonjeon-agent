"""Bounded, best-effort usage metadata; never tool arguments or results.

FastMCP.call_tool is the SDK boundary before Pydantic argument validation.
Its override preserves the normal SDK conversion and exception semantics.
See python-sdk v1.x server/fastmcp/server.py and MCP initialize.clientInfo.
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
from collections.abc import Sequence
from contextlib import suppress
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.types import ContentBlock

from jiphyeonjeon_mcp import __version__
from jiphyeonjeon_mcp.config import Settings

logger = logging.getLogger(__name__)
_VERSION = re.compile(r"^[0-9][A-Za-z0-9.+-]{0,31}$")


def _client_category(name: str) -> str:
    name = name.lower().replace("_", "-").replace(" ", "-")
    for category in ("claude-code", "claude-desktop", "cursor", "codex", "vscode"):
        if category in name:
            return category
    return "other" if name else "unknown"


@dataclass(frozen=True)
class Invocation:
    invocation_id: str
    tool_name: str
    client_name: str = "unknown"
    client_version: str = "unknown"


_invocation: ContextVar[Invocation | None] = ContextVar("mcp_invocation", default=None)


def invocation_headers() -> dict[str, str]:
    invocation = _invocation.get()
    if invocation is None:
        return {}
    return {
        "X-Jiphyeonjeon-Invocation-Id": invocation.invocation_id,
        "X-Jiphyeonjeon-Tool": invocation.tool_name,
        "X-Jiphyeonjeon-Client-Name": invocation.client_name,
        "X-Jiphyeonjeon-Client-Version": invocation.client_version,
    }


class UsageTelemetry:
    """One bounded queue/HTTP pool per server lifespan; no call-path waits."""

    def __init__(self, settings: Settings) -> None:
        self.enabled = settings.usage_telemetry
        self._settings = settings
        self._queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=256)
        self._task: asyncio.Task[None] | None = None
        self._client: httpx.AsyncClient | None = None
        self._unsupported = False

    async def start(self) -> None:
        if not self.enabled or self._task is not None:
            return
        self._client = httpx.AsyncClient(
            base_url=self._settings.normalized_base_url,
            verify=self._settings.verify_ssl,
            timeout=1.0,
            headers={
                "Authorization": f"Bearer {self._settings.token.get_secret_value()}",
                "User-Agent": f"jiphyeonjeon-mcp/{__version__}",
            },
        )
        self._task = asyncio.create_task(self._send_events())

    def emit(self, invocation: Invocation, status: str, duration_ms: float | None = None) -> None:
        if not self.enabled or self._task is None or self._unsupported:
            return
        event: dict[str, Any] = {
            "invocation_id": invocation.invocation_id,
            "tool_name": invocation.tool_name,
            "status": status,
            "adapter_version": __version__,
            "client_name": invocation.client_name,
            "client_version": invocation.client_version,
        }
        if duration_ms is not None:
            event["duration_ms"] = round(max(0.0, duration_ms), 2)
        with suppress(asyncio.QueueFull):
            self._queue.put_nowait(event)

    async def _send_events(self) -> None:
        while True:
            event = await self._queue.get()
            try:
                if self._client is not None and not self._unsupported:
                    # No retry: a missing ACK cannot cause duplicated usage or
                    # hold up tool work. The dashboard reports observed counts.
                    async with asyncio.timeout(1.25):
                        response = await self._client.post("/api/mcp/telemetry", json=event)
                    if response.status_code in {404, 405}:
                        self._unsupported = True
            except Exception:
                logger.debug("Usage measurement unavailable; tool execution continues")
            finally:
                self._queue.task_done()

    async def close(self) -> None:
        if self._task is not None:
            with suppress(TimeoutError):
                await asyncio.wait_for(self._queue.join(), timeout=1.5)
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task
            self._task = None
        if self._client is not None:
            await self._client.aclose()
            self._client = None


class MeasuredFastMCP(FastMCP[Any]):
    def __init__(self, *, telemetry: UsageTelemetry, **kwargs: Any) -> None:
        self.usage_telemetry = telemetry
        super().__init__(**kwargs)

    def _client_identity(self) -> tuple[str, str]:
        try:
            params = self.get_context().session.client_params
            if params is not None:
                info = params.clientInfo
                return _client_category(info.name), (
                    info.version if _VERSION.fullmatch(info.version) else "unknown"
                )
        except (ValueError, AttributeError, LookupError):
            pass  # Direct Python calls and older SDKs have no initialized host.
        return "unknown", "unknown"

    async def call_tool(
        self, name: str, arguments: dict[str, Any]
    ) -> Sequence[ContentBlock] | dict[str, Any]:
        if not self.usage_telemetry.enabled or self._tool_manager.get_tool(name) is None:
            return await super().call_tool(name, arguments)
        client_name, client_version = self._client_identity()
        invocation = Invocation(str(uuid4()), name, client_name, client_version)
        token = _invocation.set(invocation)
        started = time.perf_counter()
        outcome = "failed"
        self.usage_telemetry.emit(invocation, "started")
        try:
            result = await super().call_tool(name, arguments)
            outcome = "succeeded"
            return result
        except asyncio.CancelledError:
            outcome = "cancelled"
            raise
        finally:
            self.usage_telemetry.emit(invocation, outcome, (time.perf_counter() - started) * 1000)
            _invocation.reset(token)
