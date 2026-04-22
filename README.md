<div align="center">
  <h1>jiphyeonjeon-agent</h1>

  <p><strong>Bring 집현전 to Claude — 논문 검색 · 딥리뷰 · 북마크 · 커리큘럼까지 Claude 대화창에서</strong></p>

  [![License](https://img.shields.io/badge/License-Apache_2.0-green?style=for-the-badge)](./LICENSE)
  [![Python](https://img.shields.io/badge/Python-3.12-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
  [![Claude Code Compatible](https://img.shields.io/badge/Claude_Code-Compatible-blue?style=for-the-badge)](https://claude.ai)
  [![Status](https://img.shields.io/badge/Status-Alpha-yellow?style=for-the-badge)](./CHANGELOG.md)
</div>

---

한 번의 Claude 대화로 집현전의 모든 기능 접근. 자신의 계정 권한 그대로, 검색·리뷰·북마크·커리큘럼을 자동 실행합니다.

---

## Why jiphyeonjeon-agent?

- **Claude 대화 한 번으로 집현전 6개 소스 검색 (arXiv, Google Scholar, OpenAlex, DBLP, Connected Papers, OpenAlex Korean) 부터 딥리뷰·북마크·커리큘럼까지** — 자연어로 "GraphRAG 논문 5개 찾아서 리뷰해줘" 하면 자동 실행
- **내 집현전 계정 권한 그대로** — 북마크·리뷰 기록은 내 것만 보이고 수정됨
- **11개 도구 + 6개 스킬** — Claude가 자연어 요청을 자동으로 매핑하는 에이전트 인터페이스
- **집현전 버전에 맞춰 노출 도구 집합 자동 조정** — capability negotiation으로 호환성 보장
- **로컬 머신 stdio — 외부 서버·OAuth 셋업 없이 즉시 동작**

> Named after the Jiphyeonjeon (집현전), the Hall of Worthies from the Joseon Dynasty — this bridge brings that collection of scholars into your Claude conversation.

---

## Quick Start

### Option 1: Claude 한 줄 설치 (추천)

Claude Code에서 다음 중 하나를 말하면 자동 설치됩니다:

```
"집현전 agent 설치해줘"
"jiphyeonjeon setup"
"집현전 연결해줘"
```

`/jh:setup` 스킬이 자동 트리거되어 설치 과정을 안내합니다.

**단계:**
1. Claude Code에 위 텍스트 입력
2. 집현전 username/password 물어봄 → 사용자가 터미널에서 `setup.sh` 실행
3. 설치 완료 — 이후 `/jh:*` 스킬 즉시 사용 가능

### Option 2: 터미널 원샷

```bash
# 1) clone — 경로는 자유 (아래는 예시)
git clone https://github.com/KimJiSeong1994/jiphyeonjeon-agent.git ~/jiphyeonjeon-agent
cd ~/jiphyeonjeon-agent

# 2) 한 번에 설치 (uv sync + JWT 발급 프롬프트 + claude mcp add + 스킬 복사)
bash scripts/setup.sh
```

집현전 username/password 프롬프트 → Claude MCP 등록 → 완료.

### Option 3: 수동 (고급)

JWT를 이미 가진 경우:

```bash
JIPHYEONJEON_TOKEN=<your-jwt> bash scripts/setup.sh
```

또는 `~/.claude/claude.json`에 수동 등록:

```json
{
  "mcpServers": {
    "jiphyeonjeon": {
      "command": "uv",
      "args": ["--directory", "path/to/jiphyeonjeon-agent", "run", "jiphyeonjeon-mcp"],
      "env": {
        "JIPHYEONJEON_TOKEN": "<your-jwt>",
        "JIPHYEONJEON_BASE_URL": "http://localhost:8000"
      }
    }
  }
}
```

**참고**: `.venv/bin/python -m jiphyeonjeon_mcp` 직접 호출도 가능하며, uv 오버헤드 없이 더 빠르게 기동됩니다.

---

## Features

### Tools (11)

| Tool | What it does | 집현전 엔드포인트 |
|------|------------|-------------------|
| `search_papers` | 키워드로 논문 검색 (6개 소스) | `POST /api/search` |
| `get_paper` | 단일 논문 메타데이터 조회 | `GET /api/papers/{id}` |
| `start_review` | 논문 딥리뷰 시작 (비동기 → session_id) | `POST /api/deep-review` |
| `get_review_status` | 리뷰 진행 상태 폴링 | `GET /api/deep-review/status/{id}` |
| `list_bookmarks` | 내 북마크 목록 | `GET /api/bookmarks` |
| `add_bookmark` | 논문을 북마크 (metadata 직접 지정 가능) | `POST /api/bookmarks/from-paper` |
| `remove_bookmark` | 북마크 삭제 | `DELETE /api/bookmarks/{id}` |
| `create_curriculum` | 주제별 학습 커리큘럼 생성 | `POST /api/curricula/generate` |
| `explore_related` | 인용 그래프 탐색 (cite/cited-by) | `POST /api/bookmarks/{id}/citation-tree` |
| `generate_figure` | 방법론 텍스트 → SVG 다이어그램 | `POST /api/autofigure/method-to-svg` |
| `create_blog_draft` | 블로그 초안 작성 (admin 권한) | `POST /api/blog/posts` |

### Skills (6)

스킬은 여러 도구를 조합해 복잡한 워크플로우를 자동 실행합니다. `make install-skills`로 설치하면 트리거 키워드가 자동 인식됩니다.

| 스킬 | 트리거 | 흐름 |
|------|-------|------|
| `/jh:setup` | "집현전 agent 설치", "jiphyeonjeon setup" | 집현전 로그인 → JWT 발급 → Claude MCP 등록 → 스킬 복사 |
| `/jh:review-paper` | "딥리뷰", "deep review", "review this paper" | search → start_review → 폴링 → 리뷰 표시 |
| `/jh:build-curriculum` | "커리큘럼", "study plan", "학습 경로" | 주제·난이도 입력 → 커리큘럼 생성 |
| `/jh:daily-digest` | "오늘 논문", "digest", "브리핑", "daily update" | 북마크 기반 일일 브리핑 생성 |
| `/jh:explore` | "관련 논문", "citation tree", "more like this" | 특정 논문 주변 인용 그래프 탐색 |
| `/jh:draft-blog` | "블로그 초안", "blog draft", "post draft" | 여러 논문 기반 블로그 포스트 작성 |

스킬 설치:

```bash
make install-skills   # ~/.claude/skills/ 로 복사
```

### Safety & Protocol

- **Capability Negotiation** — `GET /api/version` 프로브로 집현전 버전 확인 후 지원 도구만 등록. 구형 서버도 9개 도구로 fallback 호환.
- **Path Traversal Defense** — 모든 URL 내 id는 정규식 검증 (`[a-zA-Z0-9\-_.:]` 범위, 최대 256자).
- **Prompt-Injection Framing** — 백엔드 에러 메시지는 `[backend said: ...]` 프레임으로 감싸고 제어문자 제거.
- **JWT Security** — 토큰은 `SecretStr`로 관리, 로그/repr에 노출 안 함. 24시간 만료, revocation 지원.
- **Stdio JSON-RPC** — 모든 로그는 stderr로, stdout은 JSON-RPC만 → Claude Code 통신 간섭 없음.

---

## Architecture

```
Claude Code (stdio)
        │
        ↓ (JSON-RPC)
  jiphyeonjeon-agent server
  (FastMCP 1.0, async)
        │
        ↓ (httpx + Bearer JWT)
  집현전 FastAPI
  (localhost:8000)
```

부트스트랩 순서:

1. **Config Load** — `JIPHYEONJEON_TOKEN` + `JIPHYEONJEON_BASE_URL` env 읽기
2. **Capability Probe** — `GET /api/version` 호출로 지원 도구 확인
3. **Tool Registration** — 동적으로 지원 도구만 등록
4. **Server Run** — `mcp.run()` (stdio 선택) → Claude Code 연결 대기

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Agent Runtime** | `mcp>=1.2.0` with FastMCP 1.0 |
| **HTTP Client** | `httpx>=0.27.0` (async) |
| **Config & Secrets** | `pydantic-settings>=2.3.0` with `SecretStr` |
| **Validation** | `pydantic>=2.7.0` (v2 strict) |
| **Transport** | stdio (SSE/HTTP roadmap) |
| **Dev Tooling** | `uv` (package manager), `ruff` (lint/format), `mypy` (strict type check) |
| **Testing** | `pytest>=8.0.0`, `pytest-asyncio>=0.23.0`, `respx>=0.21.0` (mock httpx) |
| **Distribution** | `uv build`, `uvx` compatible |

---

## Environment Variables

| 변수 | 필수 | 설명 |
|------|------|------|
| `JIPHYEONJEON_TOKEN` | Yes | JWT Bearer token (from `POST /api/auth/login`) |
| `JIPHYEONJEON_BASE_URL` | No | 집현전 FastAPI 주소 (기본: `http://localhost:8000`) |
| `JIPHYEONJEON_TIMEOUT` | No | 요청 타임아웃 초 (기본: `30.0`, 검색은 90 권장) |
| `JIPHYEONJEON_VERIFY_SSL` | No | TLS 인증서 검증 (기본: `true`, 로컬 자체 서명만 false) |
| `JIPHYEONJEON_SCOPE` | No | Claude Code MCP 등록 스코프 (기본: `user`) |

---

## Tool Catalog (상세)

각 도구의 파라미터 및 반환값:

### search_papers
- **params**: `query` (필수, min 1자), `max_results` (1-50, 기본 10), `sources` (arxiv/google_scholar/openalex/dblp/connected_papers/openalex_korean, 선택), `year_start` (int, 선택), `year_end` (int, 선택), `fast_mode` (bool, 기본 true)
- **returns**: `{papers: [{title, authors, abstract, arxiv_id, ...}], total: int, query_analysis: str}`

### get_paper
- **params**: `paper_id` (arxiv id/DOI/doc_id)
- **returns**: `{paper: {title, authors, abstract, venue, year, pdf_url, ...}}`

### start_review
- **params**: `paper_ids` (list, min 1), `num_researchers` (1-6, 기본 3), `fast_mode` (bool, 기본 true)
- **returns**: `{session_id: str, status: str}`

### get_review_status
- **params**: `session_id` (from start_review)
- **returns**: `{session_id, status: "processing"|"completed"|"failed", progress: int, report_available: bool}`

### list_bookmarks
- **params**: none
- **returns**: `{bookmarks: [{id, title, topic, tags, created_at, ...}]}`

### add_bookmark
- **params**: `paper_id` (선택, auto-resolve metadata) 또는 `title` + `authors` + `year` + `venue` + `arxiv_id` + `doi` (direct metadata), `topic` (기본 "Claude Agent"), `tags`, `context` (선택)
- **returns**: `{bookmark: {id, title, ...}}`

### remove_bookmark
- **params**: `bookmark_id`
- **returns**: `{deleted: true, bookmark_id, raw}`

### create_curriculum
- **params**: `topic` (필수), `difficulty` (beginner/intermediate/advanced, 기본 intermediate), `num_modules` (2-15, 기본 5)
- **returns**: `{curriculum: {modules: [{week, title, papers, goals, ...}]}}`

### explore_related
- **params**: `bookmark_id`, `depth` (1-3, 기본 2), `max_per_direction` (1-30, 기본 10)
- **returns**: `{graph: {nodes: [...], edges: [...]}}`

### generate_figure
- **params**: `method_text` (min 10자), `paper_title` (선택), `optimize_iterations` (1-10, 기본 1)
- **returns**: `{success: bool, svg_content: str, figure_png_b64: str (optional), error: str (optional)}`

### create_blog_draft
- **params**: `title` (1-300자), `content` (markdown, min 10자), `excerpt` (optional), `tags` (optional), `thumbnail_url` (optional)
- **returns**: `{post: {id, slug, title, published: false, ...}}`

---

## Project Layout

```
src/jiphyeonjeon_mcp/
  __init__.py          Package marker
  server.py            FastMCP instance + main() entry point
  client.py            JiphyeonjeonClient (httpx + JWT auth + error translation)
  auth.py              401/404/429/403 → McpError translation layer
  config.py            pydantic-settings env loader (SecretStr JWT)
  capability.py        GET /api/version → dynamic tool set negotiation
  validators.py        Path traversal defense, id validation
  tools/               One module per domain
    __init__.py          register_all() orchestrator
    search.py            search_papers
    papers.py            get_paper
    review.py            start_review, get_review_status
    bookmarks.py         list_bookmarks, add_bookmark, remove_bookmark
    curriculum.py        create_curriculum
    explore.py           explore_related
    figure.py            generate_figure
    blog.py              create_blog_draft
  resources/           (planned) jh:// URI resource handlers

skills/                Claude Code skill files (trigger patterns + flows)
  jh-setup.md          Auto-install orchestrator
  jh-review-paper.md   Deep review workflow
  jh-build-curriculum.md
  jh-daily-digest.md   Bookmark-based briefing
  jh-explore.md        Citation graph explorer
  jh-draft-blog.md     Blog post generator

scripts/               CLI helpers
  setup.sh             One-shot install (credentials → JWT → MCP register → skills copy)
  smoke_stdio.py       Smoke test (stdio transport)
  e2e_live.py          End-to-end test vs live 집현전 backend

tests/unit/            Unit tests (6 files, 37 functions, 47 cases with parametrize)
  test_auth.py         JWT + error translation
  test_client.py       httpx wrapper behavior
  test_capability.py    Capability probe + fallback
  test_tools.py         Tool contract verification
  test_tools_contract.py  Backend response shape checking
  test_validators.py    Path traversal + id validation

pyproject.toml         Project metadata, dependencies, tool config
Makefile              Common targets (test, lint, typecheck, dev, install-skills)
CHANGELOG.md          Release notes
CLAUDE.md             Developer guidelines (stdio constraints, auth, local dev loop)
```

**참고**: Python 패키지 폴더명이 `jiphyeonjeon_mcp`로 남아있는 것은 PyPI 패키지명/CLI 엔트리포인트(`jiphyeonjeon-mcp`) 및 import 경로와의 일관성 유지를 위함입니다.

---

## Testing

### Unit Tests

```bash
uv run pytest tests/unit/ -v
```

37개 test 함수 (47개 테스트 케이스 with parametrize)가 6개 파일에서 실행:
- auth, client, capability, validators, tool contracts 커버

### Smoke Test (stdio transport)

```bash
python scripts/smoke_stdio.py
```

stdin/stdout JSON-RPC가 제대로 작동하는지 확인.

### End-to-End (live backend)

```bash
python scripts/e2e_live.py
```

실제 집현전 인스턴스를 대상으로 도구 호출 테스트.

---

## Security Notes

- **JWT는 환경변수로만** — 명령어 인자·설정 파일에 노출 금지
- **SecretStr** — 토큰은 로그/traceback에서 자동 마스킹
- **24시간 만료** — 집현전에서 JWT 발급 시 default 만료 시간, 필요 시 연장 가능
- **Path traversal defense** — 모든 `{id}` URL 파라미터는 정규식 검증
- **Prompt-injection framing** — 백엔드 에러는 사용자 메시지 컨테이닝으로 격리
- **stdout 보호** — 모든 로그는 stderr로, stdout은 JSON-RPC만 → Claude와의 통신 안전 보장

---

## Roadmap

### v0.1.0 (현재)
- 11 tools + 5 skills (setup 포함 6 skills)
- JWT 패스스루 인증
- stdio transport
- Capability negotiation + fallback

### v0.2.0 (예정)
- PAT (Personal Access Token) 지원 — 장기 만료 토큰 옵션
- HTTP transport 추가
- Resource handlers (jh:// URIs)

### v1.0.0 (장기)
- OAuth 2.1 + refresh token
- claude.ai remote connector (웹 기반 MCP)
- 커리큘럼 share link 통합

---

## Contributing

Issues, PRs 환영합니다. [CLAUDE.md](./CLAUDE.md) 참조 — 코딩 컨벤션, 테스트 규칙, 커밋 메시지 형식 포함.

코딩 컨벤션:
- Python 3.12, type hints required (mypy strict)
- `async def` for all tool handlers
- 한국어 커밋 메시지 허용
- ruff format + lint (line-length 100)

---

## References

- [Model Context Protocol Spec](https://modelcontextprotocol.io/) (v0.1)
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- [Jiphyeonjeon (PaperReviewAgent)](https://github.com/KimJiSeong1994/PaperReview)
- [FastMCP](https://github.com/jlowin/fastmcp)

---

## License

[Apache License 2.0](./LICENSE)
