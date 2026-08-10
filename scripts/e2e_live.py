"""Live stdio E2E with safe read checks and opt-in, self-cleaning writes.

Required:
    JIPHYEONJEON_TOKEN=<dedicated test JWT>

Optional:
    JIPHYEONJEON_BASE_URL=https://jiphyeonjeon.kr
    JIPHYEONJEON_LIVE_WRITE_TESTS=1  # create then delete one unique bookmark
    JIPHYEONJEON_LIVE_REVIEW_PAPER_ID=<known paper id>  # starts a fast review
"""

from __future__ import annotations

import json
import os
import selectors
import subprocess
import sys
import time
from typing import Any

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    env = os.environ.copy()
    if not env.get("JIPHYEONJEON_TOKEN"):
        print("set JIPHYEONJEON_TOKEN first", file=sys.stderr)
        return 1

    proc = subprocess.Popen(
        [sys.executable, "-m", "jiphyeonjeon_mcp"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=_HERE,
    )
    assert proc.stdin is not None and proc.stdout is not None
    selector = selectors.DefaultSelector()
    selector.register(proc.stdout, selectors.EVENT_READ)
    next_id = 1

    def send(method: str, params: dict[str, Any] | None = None) -> int:
        nonlocal next_id
        call_id = next_id
        next_id += 1
        assert proc.stdin is not None
        message = {"jsonrpc": "2.0", "id": call_id, "method": method, "params": params or {}}
        proc.stdin.write((json.dumps(message) + "\n").encode())
        proc.stdin.flush()
        return call_id

    def notify(method: str, params: dict[str, Any] | None = None) -> None:
        assert proc.stdin is not None
        message = {"jsonrpc": "2.0", "method": method, "params": params or {}}
        proc.stdin.write((json.dumps(message) + "\n").encode())
        proc.stdin.flush()

    def wait_for(call_id: int, timeout: float = 90.0) -> dict[str, Any]:
        assert proc.stdout is not None
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            remaining = max(0.0, deadline - time.monotonic())
            if not selector.select(timeout=remaining):
                break
            line = proc.stdout.readline().decode().strip()
            if not line:
                if proc.poll() is not None:
                    raise RuntimeError(f"MCP process exited with {proc.returncode}")
                continue
            message = json.loads(line)
            if message.get("id") == call_id:
                return message
        raise TimeoutError(f"id={call_id} did not respond")

    results: list[tuple[str, bool, str]] = []

    def call_tool(
        name: str,
        args: dict[str, Any],
        *,
        timeout: float = 90.0,
        expect_error: bool = False,
    ) -> dict[str, Any] | None:
        try:
            response = wait_for(
                send("tools/call", {"name": name, "arguments": args}),
                timeout=timeout,
            )
        except (TimeoutError, RuntimeError) as exc:
            results.append((name, False, str(exc)))
            return None

        result = response.get("result", {})
        failed = "error" in response or bool(result.get("isError", False))
        passed = failed if expect_error else not failed
        expectation = "expected denial" if expect_error else "success"
        preview = str(response.get("error") or result.get("structuredContent") or result)[:240]
        results.append((name, passed, f"{expectation}: {preview}"))
        return result if not failed else None

    def structured(result: dict[str, Any] | None) -> dict[str, Any]:
        if not result:
            return {}
        payload = result.get("structuredContent")
        return payload if isinstance(payload, dict) else {}

    try:
        init_id = send(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "e2e-live", "version": "0"},
            },
        )
        wait_for(init_id)
        notify("notifications/initialized")

        # Safe/default suite.
        call_tool("search_papers", {"query": "transformer attention", "max_results": 3}, timeout=60)
        call_tool("list_bookmarks", {})
        call_tool(
            "search_papers",
            {"query": "strict validation", "limit": 1},
            expect_error=True,
        )
        call_tool("get_paper", {"paper_id": "../../admin"}, expect_error=True)
        call_tool(
            "get_paper",
            {"paper_id": "definitely-not-exists-mcp-e2e"},
            expect_error=True,
        )

        # Mutations require an explicit repository variable/locally-set opt-in.
        if env.get("JIPHYEONJEON_LIVE_WRITE_TESTS") == "1":
            marker = f"mcp-e2e-{int(time.time())}"
            created = call_tool(
                "add_bookmark",
                {
                    "title": f"Attention Is All You Need [{marker}]",
                    "authors": ["Vaswani et al."],
                    "year": 2017,
                    "topic": marker,
                },
            )
            payload = structured(created)
            bookmark = (
                payload.get("bookmark") if isinstance(payload.get("bookmark"), dict) else payload
            )
            bookmark_id = bookmark.get("id") if isinstance(bookmark, dict) else None
            if isinstance(bookmark_id, str):
                call_tool("remove_bookmark", {"bookmark_id": bookmark_id})
            else:
                results.append(("remove_bookmark", False, "created bookmark id unavailable"))

        review_paper_id = env.get("JIPHYEONJEON_LIVE_REVIEW_PAPER_ID")
        if review_paper_id:
            call_tool(
                "start_review",
                {"paper_ids": [review_paper_id], "num_researchers": 1, "fast_mode": True},
                timeout=30,
            )
    finally:
        selector.close()
        if proc.stdin and not proc.stdin.closed:
            proc.stdin.close()
        time.sleep(0.2)
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()

    print("\n=== E2E tool invocation summary ===")
    for name, passed, detail in results:
        print(f"  {'✓' if passed else '✗'} {name}: {detail[:180]}")
    passed_count = sum(passed for _, passed, _ in results)
    print(f"\n{passed_count}/{len(results)} checks passed")
    return 0 if results and passed_count == len(results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
