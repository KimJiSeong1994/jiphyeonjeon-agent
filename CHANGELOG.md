# Changelog

## v0.1.6 — 2026-09-06

Privacy-bounded MCP usage measurement.

- Added best-effort tool lifecycle telemetry with per-invocation identifiers, terminal outcomes,
  and durations. Telemetry never contains tool arguments, results, bearer tokens, or user IDs.
- Propagated invocation, tool, and client claim headers to related backend requests without
  sharing context between concurrent calls.
- Covered local tools and pre-handler schema failures at the FastMCP call boundary, including
  cancellation outcomes.
- Kept measurement fail-open through a bounded queue, short delivery timeout, no retries, and
  automatic fallback for backends that do not expose the telemetry endpoint.
- Added `JIPHYEONJEON_USAGE_TELEMETRY=0` as an explicit opt-out. Existing adapters remain
  compatible and continue without tool-level measurement.
- Distribution remains GitHub Release/source-install only; this release does not publish to PyPI.

## v0.1.5 — 2026-08-10

Runtime and upstream-contract stabilization.

- Added semantic OpenAPI contract validation to PR CI and a configuration-gated nightly live
  contract check.
- Added a nightly stdio E2E workflow with strict-input checks and opt-in, self-cleaning writes.
- Made all 14 MCP tools reject unknown arguments and advertise
  `additionalProperties: false`.
- Added read-only `check_blog_draft` preflight and unpublished `update_blog_draft`; paper-review
  mutations now stop before HTTP when citability checks fail unless explicitly overridden.
- Reused one authenticated HTTP connection pool per MCP server lifespan and closed it on shutdown.
- Moved the advisory GitHub release check off the readiness-critical startup path.

## v0.1.4 — 2026-08-10

MCP/API contract completion and consistency hardening.

- Added `get_review_report` so deep-review workflows complete entirely through MCP.
- Added direct search-result metadata support to `add_bookmark`, avoiding index lookup failures
  after default fast searches.
- Made successful capability responses authoritative, enforced `mcp_min_client`, and reduced the
  unavailable/legacy fallback to public read-only tools.
- Deduplicated flattened search results while preserving backend quality and timing metadata.
- Aligned bundled skills, runtime server version, README contracts, and distribution guidance.

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
