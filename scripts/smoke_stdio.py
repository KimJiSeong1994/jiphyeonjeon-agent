"""Full stdio round-trip smoke test.

Spawns the MCP server as a subprocess, sends the MCP handshake + tools/list
via JSON-RPC over stdio, asserts we get back the registered tool list.

Run:
    JIPHYEONJEON_TOKEN=<jwt> \\
    JIPHYEONJEON_BASE_URL=http://localhost:8000 \\
    uv run python scripts/smoke_stdio.py
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

    def send(msg: dict) -> None:
        assert proc.stdin is not None
        proc.stdin.write((json.dumps(msg) + "\n").encode())
        proc.stdin.flush()

    def recv() -> dict | None:
        assert proc.stdout is not None
        line = proc.stdout.readline().decode().strip()
        return json.loads(line) if line else None

    send({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "smoke", "version": "0"},
        },
    })
    init_resp = recv()
    print("initialize ->", init_resp and init_resp.get("result", {}).get("serverInfo"))

    send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
    send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    list_resp = recv()
    assert list_resp is not None, "no tools/list response"
    tools = [t["name"] for t in list_resp["result"]["tools"]]
    print(f"registered {len(tools)} tools:")
    for t in tools:
        print(f"  - {t}")

    # Clean shutdown
    proc.stdin.close()
    time.sleep(0.3)
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()

    return 0 if tools else 2


if __name__ == "__main__":
    sys.exit(main())
