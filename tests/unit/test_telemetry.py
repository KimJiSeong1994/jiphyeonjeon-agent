"""Usage telemetry stays bounded, metadata-only, and outside tool semantics."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx
import pytest
from mcp.server.fastmcp.exceptions import ToolError
from mcp.shared.memory import create_connected_server_and_client_session
from mcp.types import Implementation
from pydantic import SecretStr

from jiphyeonjeon_mcp.client import JiphyeonjeonClient
from jiphyeonjeon_mcp.config import Settings
from jiphyeonjeon_mcp.telemetry import (
    Invocation,
    MeasuredFastMCP,
    UsageTelemetry,
    invocation_headers,
)


def _settings(*, enabled: bool = True) -> Settings:
    return Settings(
        token=SecretStr("secret-token"),
        base_url="http://backend.test",
        usage_telemetry=enabled,
        auto_update_check=False,
    )


class RecordingTelemetry(UsageTelemetry):
    def __init__(self, *, enabled: bool = True) -> None:
        super().__init__(_settings(enabled=enabled))
        self.events: list[tuple[Invocation, str, float | None]] = []

    def emit(
        self,
        invocation: Invocation,
        status: str,
        duration_ms: float | None = None,
    ) -> None:
        if self.enabled:
            self.events.append((invocation, status, duration_ms))


def _local_server(telemetry: UsageTelemetry) -> MeasuredFastMCP:
    mcp = MeasuredFastMCP(telemetry=telemetry, name="telemetry-test")

    @mcp.tool()
    async def local_check(content: str) -> dict[str, str]:
        return {"checked": content}

    return mcp


async def test_local_tool_and_schema_failure_each_emit_one_lifecycle() -> None:
    telemetry = RecordingTelemetry()
    mcp = _local_server(telemetry)

    await mcp.call_tool("local_check", {"content": "valid"})
    with pytest.raises(ToolError, match="Field required"):
        await mcp.call_tool("local_check", {})

    assert [status for _, status, _ in telemetry.events] == [
        "started",
        "succeeded",
        "started",
        "failed",
    ]
    assert telemetry.events[0][0].invocation_id == telemetry.events[1][0].invocation_id
    assert telemetry.events[2][0].invocation_id == telemetry.events[3][0].invocation_id
    assert telemetry.events[0][0].invocation_id != telemetry.events[2][0].invocation_id


async def test_protocol_handler_intercepts_validation_and_captures_bounded_client_claims() -> None:
    telemetry = RecordingTelemetry()
    mcp = _local_server(telemetry)

    async with create_connected_server_and_client_session(
        mcp,
        client_info=Implementation(name="Claude Desktop Preview", version="1.2.3"),
    ) as session:
        result = await session.call_tool(
            "local_check",
            {"unknown": "rejected-before-handler"},
        )

    assert result.isError is True
    assert [status for _, status, _ in telemetry.events] == ["started", "failed"]
    invocation = telemetry.events[0][0]
    assert invocation.client_name == "claude-desktop"
    assert invocation.client_version == "1.2.3"


async def test_concurrent_calls_keep_invocation_headers_isolated() -> None:
    telemetry = RecordingTelemetry()
    seen: list[tuple[str, str, str]] = []
    both_started = asyncio.Event()
    waiting = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal waiting
        marker = str(json.loads(request.content)["marker"])
        seen.append(
            (
                marker,
                request.headers["X-Jiphyeonjeon-Invocation-Id"],
                request.headers["X-Jiphyeonjeon-Tool"],
            )
        )
        waiting += 1
        if waiting == 2:
            both_started.set()
        await both_started.wait()
        return httpx.Response(200, json={"marker": marker})

    http_client = httpx.AsyncClient(
        base_url="http://backend.test",
        transport=httpx.MockTransport(handler),
    )
    client = JiphyeonjeonClient(_settings(), http_client=http_client)
    mcp = MeasuredFastMCP(telemetry=telemetry, name="concurrency-test")

    @mcp.tool()
    async def proxy(marker: str) -> dict[str, Any]:
        return await client.post_json("/work", {"marker": marker}, operation="work")

    try:
        await asyncio.gather(
            mcp.call_tool("proxy", {"marker": "first"}),
            mcp.call_tool("proxy", {"marker": "second"}),
        )
    finally:
        await http_client.aclose()

    assert {marker for marker, _, _ in seen} == {"first", "second"}
    assert len({invocation_id for _, invocation_id, _ in seen}) == 2
    assert {tool_name for _, _, tool_name in seen} == {"proxy"}
    assert invocation_headers() == {}


async def test_cancelled_tool_emits_cancelled_terminal_and_reraises() -> None:
    telemetry = RecordingTelemetry()
    mcp = MeasuredFastMCP(telemetry=telemetry, name="cancellation-test")
    entered = asyncio.Event()

    @mcp.tool()
    async def wait_forever() -> None:
        entered.set()
        await asyncio.Event().wait()

    task = asyncio.create_task(mcp.call_tool("wait_forever", {}))
    await entered.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert [status for _, status, _ in telemetry.events] == ["started", "cancelled"]
    assert telemetry.events[-1][2] is not None
    assert invocation_headers() == {}


async def test_wire_payload_never_contains_tool_arguments_results_or_token() -> None:
    telemetry = UsageTelemetry(_settings())
    idle_task = asyncio.create_task(asyncio.sleep(60))
    telemetry._task = idle_task
    mcp = MeasuredFastMCP(telemetry=telemetry, name="privacy-test")

    @mcp.tool()
    async def private_tool(argument_secret: str) -> dict[str, str]:
        return {"result_secret": f"derived-{argument_secret}"}

    try:
        await mcp.call_tool("private_tool", {"argument_secret": "ARGUMENT-SECRET"})
        events = [telemetry._queue.get_nowait(), telemetry._queue.get_nowait()]
    finally:
        telemetry._task = None
        idle_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await idle_task

    encoded = json.dumps(events)
    assert "ARGUMENT-SECRET" not in encoded
    assert "derived-" not in encoded
    assert "secret-token" not in encoded
    assert {event["status"] for event in events} == {"started", "succeeded"}
    assert all(
        set(event)
        <= {
            "invocation_id",
            "tool_name",
            "status",
            "adapter_version",
            "client_name",
            "client_version",
            "duration_ms",
        }
        for event in events
    )


async def test_queue_is_bounded_and_drops_overflow_without_blocking() -> None:
    telemetry = UsageTelemetry(_settings())
    idle_task = asyncio.create_task(asyncio.sleep(60))
    telemetry._task = idle_task
    invocation = Invocation("00000000-0000-4000-8000-000000000001", "local_check")
    try:
        for _ in range(300):
            telemetry.emit(invocation, "started")
        assert telemetry._queue.qsize() == 256
    finally:
        telemetry._task = None
        idle_task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await idle_task


@pytest.mark.parametrize("mode", ["404", "timeout"])
async def test_delivery_outage_is_fail_open_and_queue_drains(mode: str) -> None:
    requests = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal requests
        requests += 1
        if mode == "timeout":
            raise httpx.ReadTimeout("late", request=request)
        return httpx.Response(404)

    telemetry = UsageTelemetry(_settings())
    telemetry._client = httpx.AsyncClient(
        base_url="http://backend.test",
        transport=httpx.MockTransport(handler),
    )
    telemetry._task = asyncio.create_task(telemetry._send_events())
    invocation = Invocation("00000000-0000-4000-8000-000000000001", "local_check")
    try:
        telemetry.emit(invocation, "started")
        await asyncio.wait_for(telemetry._queue.join(), timeout=0.5)
        assert requests == 1

        telemetry.emit(invocation, "succeeded", 5.0)
        await asyncio.wait_for(telemetry._queue.join(), timeout=0.5)
        assert requests == (2 if mode == "timeout" else 1)
        assert telemetry._queue.empty()
    finally:
        await telemetry.close()


async def test_opt_out_skips_lifecycle_and_invocation_headers() -> None:
    telemetry = RecordingTelemetry(enabled=False)
    mcp = _local_server(telemetry)

    await mcp.call_tool("local_check", {"content": "valid"})

    assert telemetry.events == []
    assert invocation_headers() == {}
