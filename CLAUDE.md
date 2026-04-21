# jiphyeonjeon-mcp

MCP server wrapping 집현전 (PaperReviewAgent) REST API. Wraps FastAPI backend at `/Users/jiseong/git/PaperReviewAgent` as Claude tools via stdio transport.

## Architecture

- **Transport**: stdio only (Claude Code / Claude Desktop)
- **Auth**: JWT Bearer token passthrough via `JIPHYEONJEON_TOKEN` env var
- **Client**: `httpx.AsyncClient` wrapper with auto auth header injection
- **SDK**: `mcp[cli]>=1.2.0` (FastMCP 1.0 included)

## Project layout

```
src/jiphyeonjeon_mcp/
  server.py         # FastMCP instance + main() entry point
  client.py         # JiphyeonjeonClient (httpx + auth + error translation)
  auth.py           # 401/404/429 -> McpError translation
  config.py         # pydantic-settings env loader (SecretStr for token)
  capability.py     # GET /api/version -> dynamic tool registration
  tools/            # One module per domain (search, review, bookmarks, ...)
  resources/        # jh:// URI handlers
  generated/        # auto-gen from openapi.json (committed for reproducibility)
```

## Critical constraints

1. **stdout is the JSON-RPC channel**. NEVER `print()`. All logging must go to `sys.stderr`.
2. **No `ctx.report_progress()` on stdio** — SDK bug hangs the server. Use task_id polling pattern for long ops.
3. **Test `Client(mcp)` inside test function**, NOT pytest fixture (event loop conflict).
4. **Token is `SecretStr`** — never log it, never include in error messages verbatim.

## Local dev loop

1. Start 집현전 backend: `cd /Users/jiseong/git/PaperReviewAgent && python api_server.py` (port 8000)
2. Develop MCP: `uv run mcp dev src/jiphyeonjeon_mcp/server.py` (MCP Inspector at :6274)
3. Test in Claude Code: `claude mcp add jiphyeonjeon-dev -- uv --directory $(pwd) run jiphyeonjeon-mcp`

## Cross-repo coordination

- 집현전 repo: `/Users/jiseong/git/PaperReviewAgent` (FastAPI + SQLite + FAISS)
- 집현전 OpenAPI at runtime: `http://localhost:8000/openapi.json`
- 집현전 CLAUDE.md: `/Users/jiseong/git/PaperReviewAgent/.claude/CLAUDE.md`
- Capability endpoint: `GET /api/version` — tells MCP which tools to register

## Coding conventions

- Python 3.12, type hints required (mypy strict)
- `async def` for all tool handlers
- Tool docstrings become Claude-visible descriptions
- Korean allowed in commit messages + user-facing messages
- ruff format + lint (line-length 100)
