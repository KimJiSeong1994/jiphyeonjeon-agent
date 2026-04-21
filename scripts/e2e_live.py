"""Live end-to-end: invoke a few tools through stdio JSON-RPC against a running 집현전.

Run with a valid JWT + base URL:
    JIPHYEONJEON_TOKEN=<jwt> JIPHYEONJEON_BASE_URL=http://localhost:8000 \\
    uv run python scripts/e2e_live.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    env = os.environ.copy()
    if "JIPHYEONJEON_TOKEN" not in env:
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

    next_id = 1

    def send(method: str, params: dict | None = None) -> int:
        nonlocal next_id
        call_id = next_id
        next_id += 1
        assert proc.stdin is not None
        proc.stdin.write(
            (
                json.dumps(
                    {"jsonrpc": "2.0", "id": call_id, "method": method, "params": params or {}}
                )
                + "\n"
            ).encode()
        )
        proc.stdin.flush()
        return call_id

    def notify(method: str, params: dict | None = None) -> None:
        assert proc.stdin is not None
        proc.stdin.write(
            (
                json.dumps({"jsonrpc": "2.0", "method": method, "params": params or {}}) + "\n"
            ).encode()
        )
        proc.stdin.flush()

    def wait_for(call_id: int, timeout: float = 90.0) -> dict:
        assert proc.stdout is not None
        deadline = time.time() + timeout
        while time.time() < deadline:
            line = proc.stdout.readline().decode().strip()
            if not line:
                continue
            msg = json.loads(line)
            if msg.get("id") == call_id:
                return msg
        raise TimeoutError(f"id={call_id} did not respond")

    results: list[tuple[str, str]] = []

    def call_tool(name: str, args: dict, timeout: float = 90.0) -> None:
        cid = send("tools/call", {"name": name, "arguments": args})
        try:
            resp = wait_for(cid, timeout=timeout)
        except TimeoutError as exc:
            results.append((name, f"TIMEOUT after {timeout}s: {exc}"))
            return
        if "error" in resp:
            results.append((name, f"ERROR {resp['error'].get('code')}: {resp['error'].get('message')[:200]}"))
        else:
            result = resp.get("result", {})
            is_error = result.get("isError", False)
            status = "ERROR" if is_error else "OK"
            preview = str(result.get("structuredContent") or result.get("content") or "")[:200]
            results.append((name, f"{status} — {preview}"))

    # Handshake
    send("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "e2e-live", "version": "0"},
    })
    wait_for(1)
    notify("notifications/initialized")

    # Suite
    call_tool("search_papers", {"query": "transformer attention", "max_results": 3}, timeout=60)
    call_tool("list_bookmarks", {})
    # add_bookmark with explicit metadata (skip paper_id resolution)
    call_tool(
        "add_bookmark",
        {
            "title": "Attention Is All You Need [mcp-e2e]",
            "authors": ["Vaswani et al."],
            "year": 2017,
            "topic": "mcp-e2e-test",
        },
    )
    # list again to see the added one
    call_tool("list_bookmarks", {})
    # get_paper with an obviously-missing id (expect 404 translated to error)
    call_tool("get_paper", {"paper_id": "definitely-not-exists-12345"})
    # path traversal — expect validation error (no HTTP at all)
    call_tool("get_paper", {"paper_id": "../../admin"})
    # start_review with a fake id (backend returns session or error — we just
    # verify our outbound contract is accepted)
    call_tool(
        "start_review",
        {"paper_ids": ["dummy-id-for-e2e"], "fast_mode": True},
        timeout=30,
    )

    # Clean shutdown
    proc.stdin.close()
    time.sleep(0.3)
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()

    # Summary
    print("\n=== E2E tool invocation summary ===")
    ok = 0
    for name, outcome in results:
        marker = "✓" if outcome.startswith("OK") else "✗"
        print(f"  {marker} {name}: {outcome[:160]}")
        if outcome.startswith("OK") or "허용된 형식" in outcome:
            ok += 1
    print(f"\n{ok}/{len(results)} tool calls returned cleanly (including expected validation denials)")
    return 0 if ok == len(results) else 2


if __name__ == "__main__":
    sys.exit(main())
