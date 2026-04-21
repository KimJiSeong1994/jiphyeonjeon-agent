# jiphyeonjeon-mcp

집현전(PaperReviewAgent) 기능을 Claude Code/Desktop에 MCP tool·skill로 노출하는 Python 서버.

## 개요

집현전 FastAPI 백엔드를 MCP (Model Context Protocol) 서버로 래핑해서, Claude가 로그인한 사용자를 대신해 논문 검색/딥리뷰/북마크/커리큘럼 등을 호출할 수 있게 합니다.

**v0.1.0 스코프**: JWT 패스스루 인증 + stdio transport + 11개 tool + 5개 Claude Code skill. 로컬 개발 환경 사용.

## 설치 (로컬 dev)

집현전 repo는 `/Users/jiseong/git/PaperReviewAgent`에서 실행 중이어야 합니다.

```bash
git clone <this-repo> /Users/jiseong/git/jiphyeonjeon-mcp
cd /Users/jiseong/git/jiphyeonjeon-mcp
uv sync
```

## 설정

### 1. JWT 토큰 발급 (집현전)

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"<your>","password":"<your>"}' | jq -r .access_token
```

### 2. Claude Code 등록 (로컬 dev)

```bash
claude mcp add jiphyeonjeon \
  --scope user \
  --env JIPHYEONJEON_TOKEN=<JWT> \
  --env JIPHYEONJEON_BASE_URL=http://localhost:8000 \
  -- uv --directory /Users/jiseong/git/jiphyeonjeon-mcp run jiphyeonjeon-mcp
```

또는 `~/.claude.json`에 직접:

```json
{
  "mcpServers": {
    "jiphyeonjeon": {
      "command": "uv",
      "args": ["--directory", "/Users/jiseong/git/jiphyeonjeon-mcp", "run", "jiphyeonjeon-mcp"],
      "env": {
        "JIPHYEONJEON_TOKEN": "<JWT>",
        "JIPHYEONJEON_BASE_URL": "http://localhost:8000"
      }
    }
  }
}
```

## Tool 목록

| Tool | 집현전 엔드포인트 | 설명 |
|---|---|---|
| `search_papers` | `POST /api/search` | 논문 검색 (arxiv + rerank) |
| `get_paper` | `GET /api/papers/{id}` | 단일 논문 메타데이터 |
| `start_review` | `POST /api/deep-review` | 딥리뷰 시작 (비동기 → session_id) |
| `get_review_status` | `GET /api/deep-review/status/{id}` | 리뷰 진행 폴링 |
| `list_bookmarks` | `GET /api/bookmarks` | 내 북마크 목록 |
| `add_bookmark` | `POST /api/bookmarks/from-paper` | 논문 북마크 |
| `remove_bookmark` | `DELETE /api/bookmarks/{id}` | 북마크 삭제 (destructive) |
| `create_curriculum` | `POST /api/curricula/generate` | 학습 커리큘럼 생성 |
| `explore_related` | `POST /api/bookmarks/{id}/citation-tree` | 인용 그래프 탐색 |
| `generate_figure` | `POST /api/autofigure/method-to-svg` | 방법론 다이어그램 생성 |
| `create_blog_draft` | `POST /api/blog/posts` | 블로그 초안 (admin only) |

## Skills 설치

```bash
make install-skills   # ~/.claude/skills/ 로 복사
```

- `/jh:review-paper` — 딥리뷰 플로우 (search → start_review → 폴링 → resource)
- `/jh:build-curriculum` — 커리큘럼 설계
- `/jh:daily-digest` — 일일 브리핑
- `/jh:draft-blog` — 블로그 초안 작성
- `/jh:explore` — 관련 논문 그래프 탐색

## 개발

자세한 가이드는 `docs/` 및 `CONTRIBUTING.md` 참조.

```bash
uv sync                                      # deps 설치
uv run pytest                                # 테스트
uv run mcp dev src/jiphyeonjeon_mcp/server.py  # MCP Inspector 로 tool 확인
```

## License

Apache License 2.0 — see LICENSE.
