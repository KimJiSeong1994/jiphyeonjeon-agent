# MCP Consistency Remediation Plan

## Objective

Make the Jiphyeonjeon MCP adapter a complete and conservative contract boundary for the
PaperReview API. The implementation must complete the deep-review workflow, preserve search
quality metadata, make search-to-bookmark chaining reliable, reject incompatible capability
maps, and keep tool schemas, bundled skills, runtime metadata, and distribution documentation
aligned.

## Acceptance criteria

1. A caller can start a review, poll it, and fetch the completed report using MCP tools only.
2. A paper returned by the default `search_papers` call can be bookmarked without requiring it
   to exist in the backend paper index.
3. A successful capability response is authoritative, including an explicitly empty list.
4. A backend requiring a newer MCP client fails startup clearly instead of registering tools.
5. `get_paper` no longer promises unsupported DOI path lookup.
6. Search results are deduplicated deterministically and retain backend observability fields.
7. Bundled skills use only current tool parameters; legacy names are covered by regression tests.
8. MCP initialization, package metadata, README, skill counts, and registry guidance agree.
9. Unit tests, lint, formatting, strict type checking, stdio smoke testing, and package builds pass.

## Implementation sequence

### Phase 1 — Contract-locking tests

- Add review-report request/response tests.
- Add a default search-to-bookmark chaining test using metadata returned by search.
- Add capability tests for empty capability sets and minimum-client incompatibility.
- Add DOI contract, search deduplication/metadata preservation, skill schema, and runtime version
  assertions.

### Phase 2 — Core tool contracts

- Add `get_review_report(session_id)` for `GET /api/deep-review/report/{session_id}`.
- Extend `add_bookmark` with a `paper` metadata object and make explicit metadata bypass index
  resolution. Keep `paper_id` lookup for indexed-paper convenience.
- Remove DOI claims from `get_paper`; DOI remains valid in JSON-body workflows such as review and
  direct bookmark metadata.
- Deduplicate flattened search results and copy all non-`results` response metadata through.

### Phase 3 — Compatibility negotiation

- Treat a valid capability list as authoritative even when empty.
- Validate the capability payload shape.
- Enforce `mcp_min_client` against the installed adapter version before tool registration.
- Restrict failure fallback to the documented legacy baseline and distinguish fallback from a
  successful empty response.

### Phase 4 — Agent and distribution surfaces

- Update all bundled skills to current argument names and complete review-report retrieval.
- Align README tool schemas, return shapes, skill count, validation length, and roadmap status.
- Mark the PyPI `server.json` as a non-publishable reference or switch the live manifest to the
  repository-supported distribution path; do not claim an unavailable registry package.
- Ensure MCP `serverInfo.version` reports the adapter package version rather than the SDK version.

### Phase 5 — Verification

- Run targeted tests after each phase.
- Run the complete unit suite, Ruff, format check, Mypy strict, stdio handshake, and `uv build`.
- Review the final diff for leaked credentials, unintended API expansion, and documentation drift.

## Compatibility notes

- Existing tool names and current parameters remain stable.
- `add_bookmark(paper_id=...)` remains supported for indexed papers.
- Review and bookmark JSON bodies continue accepting DOI values; only the unsupported DOI claim on
  the path-based `get_paper` tool is removed.
- Unknown backend capabilities remain ignored because registration is the intersection of the
  backend map and locally implemented tool modules.
