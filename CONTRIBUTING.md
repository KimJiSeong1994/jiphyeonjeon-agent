# Contributing to jiphyeonjeon-agent

Thanks for considering a contribution. This project is a Claude agent bridge
to the [집현전 / PaperReviewAgent](https://github.com/KimJiSeong1994/PaperReview)
API, exposed over the Model Context Protocol (MCP).

This is a **solo-maintained alpha** — responses and merges are best-effort,
not SLA-backed. File an issue before a large PR so we can align on scope.

## Quick setup

```bash
# 1. Fork + clone
git clone https://github.com/<your-fork>/jiphyeonjeon-agent.git
cd jiphyeonjeon-agent

# 2. Install uv (https://docs.astral.sh/uv/)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Install dependencies + dev group
uv sync

# 4. Run the test suite
uv run pytest tests/unit -v   # 37 test functions, ~47 cases with parametrize
```

## Development workflow

### Running the agent locally

You need a running 집현전 instance (local or `https://jiphyeonjeon.kr`) and a JWT.

```bash
# obtain a JWT via the login endpoint (replace <user>/<pw>)
curl -sS -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"<user>","password":"<pw>"}' | jq -r .access_token

# run the MCP server against the backend via MCP Inspector
JIPHYEONJEON_TOKEN=<paste-jwt> \
JIPHYEONJEON_BASE_URL=http://localhost:8000 \
uv run mcp dev src/jiphyeonjeon_mcp/server.py
```

MCP Inspector opens at `http://localhost:6274`. You can call any registered
tool from the UI.

### Code style & quality gates

Before opening a PR, run the same gates CI runs:

```bash
uv run ruff check src tests        # lint
uv run ruff format src tests       # auto-format
uv run mypy src                    # strict type check
uv run pytest tests/unit -v        # unit tests
```

PRs that introduce a new tool should also add:

1. A contract test in `tests/unit/test_tools_contract.py` asserting the
   outbound body key names match the 집현전 Pydantic model.
2. A happy-path + at least one error-path test.
3. A short entry in `README.md` Tool Catalog.

### Commit style

- Conventional-commits-adjacent (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
- Korean or English commit messages are both fine.
- Keep the subject line under 72 chars.
- Reference issues as `#123` in the body.

## Project layout

See [`CLAUDE.md`](./CLAUDE.md) for the module-by-module architecture overview
and the critical stdio/SecretStr/testing constraints.

## Adding a tool

1. Pick a capability flag already advertised by 집현전's `GET /api/version`
   (or add it to the backend first).
2. Add a new file under `src/jiphyeonjeon_mcp/tools/` or extend an existing
   domain module. Use `@mcp.tool()` with `Annotated[..., Field(...)]` for
   each parameter so the JSON schema is generated automatically.
3. Register the module in `src/jiphyeonjeon_mcp/tools/__init__.py`.
4. Write tests (see above).
5. Update `README.md` Tool Catalog and `CHANGELOG.md`.

## Reporting bugs

Please include:

- `uv --version`, `python --version`, `uv run python -m jiphyeonjeon_mcp --help` if applicable
- 집현전 backend version (`curl <base>/api/version`)
- Redacted stderr from the MCP server (stdout is the JSON-RPC channel — look
  at the host's MCP log if possible)
- Minimal reproduction: exact tool call + arguments

## Security

See [README.md § Security Notes](./README.md#security-notes). If you believe
you have found a security issue, please open a GitHub security advisory
rather than a public issue.
