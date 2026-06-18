# Changelog

## v0.1.3 — 2026-06-18

Agent discoverability & distribution. No behavior change — tool signatures,
request/response shapes, and the web UI are untouched.

### Changed
- Tool docstrings rewritten action/trigger-first (Korean + English) so MCP
  clients map natural-language intent to the right tool more reliably.
- All 11 tools now carry `ToolAnnotations` (`title`, `readOnlyHint`,
  `destructiveHint`, `idempotentHint`); `remove_bookmark` flagged destructive.

### Added
- `server.json` — manifest for the official MCP Registry (schema 2025-12-11,
  PyPI / stdio).
- `CITATION.cff` — citable software metadata (GitHub "Cite this repository").
- `docs/strategy/` and `docs/distribution/` — SEO·GEO strategy plus MCP
  Registry publishing, awesome-list, and website `llms.txt` guides.
- README: PyPI ownership marker (`mcp-name`) and agent-native positioning.

## v0.1.0 — 2026-04-21

Initial release.

### Features
- 11 MCP tools wrapping 집현전 FastAPI:
  `search_papers`, `get_paper`, `start_review`, `get_review_status`,
  `list_bookmarks`, `add_bookmark`, `remove_bookmark`, `create_curriculum`,
  `explore_related`, `generate_figure`, `create_blog_draft`.
- 5 Claude Code skills in `skills/` (review-paper, build-curriculum,
  daily-digest, draft-blog, explore).
- Capability negotiation via `GET /api/version` with baseline-fallback for
  pre-MCP-aware 집현전 servers (registers 9 of 11 tools).
- Stdio transport only. JWT Bearer auth via `JIPHYEONJEON_TOKEN` env var
  (`SecretStr` — never logged).
- Path-traversal defense on all URL-embedded ids.
- Backend-error prompt-injection defense: error messages wrapped in an
  explicit `[backend said: ...]` frame with control chars stripped.

### Backend additions
- `GET /api/papers/{paper_id}` — single-paper lookup.
- `GET /api/version` — capability map for MCP client negotiation.

### Tests
- 47 unit tests covering auth translation, HTTP client, capability probe,
  tool registration, contract verification, id validation.
