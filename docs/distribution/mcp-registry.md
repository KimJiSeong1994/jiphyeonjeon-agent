# MCP 유통 플라이휠 — 발행 가이드

> SEO·GEO 전략(`docs/strategy/seo-geo-strategy.md`) 기둥 C "MCP 유통 플라이휠"의 실행 문서.
> 각 등재 = 백링크 + LLM이 읽는 코퍼스 항목 + 발견 채널. UI/UX 무변경, 이 repo에서 즉시 실행 가능.

## 0. 전제조건 (블로커)

1. **PyPI 게시.** MCP Registry는 *메타데이터만* 호스팅하고 실제 패키지는 PyPI에서 검증한다. 따라서 `jiphyeonjeon-mcp`를 PyPI에 먼저 게시해야 한다.
   ```bash
   uv build
   uv publish        # 또는 twine upload dist/*  (PyPI 토큰 필요)
   ```
2. **소유권 검증 마커.** Registry는 PyPI 패키지 설명(=README)에서 `mcp-name: io.github.KimJiSeong1994/jiphyeonjeon-agent` 문자열을 찾아 소유권을 검증한다. → 이미 `README.md` 상단에 HTML 주석으로 추가됨:
   ```html
   <!-- mcp-name: io.github.KimJiSeong1994/jiphyeonjeon-agent -->
   ```
   이 값은 `server.json`의 `name`과 **정확히 일치**해야 한다.
3. **GitHub 네임스페이스.** GitHub 인증을 쓰므로 서버 이름은 반드시 `io.github.<username>/...` 형식. (username = `KimJiSeong1994`)

## 1. 공식 MCP Registry 발행

루트의 [`server.json`](../../server.json)이 준비되어 있다(스키마 `2025-12-11`, `registryType: pypi`, `transport: stdio`).

```bash
# mcp-publisher 설치 (Homebrew)
brew install mcp-publisher

# 스키마/메타데이터 검증 — 발행 전 필수
mcp-publisher validate          # server.json 유효성 확인

# 인증 후 발행
mcp-publisher login github
mcp-publisher publish

# 확인
curl "https://registry.modelcontextprotocol.io/v0.1/servers?search=jiphyeonjeon"
```

> ⚠️ Registry는 preview 단계라 스키마가 바뀔 수 있다. `mcp-publisher init`로 최신 템플릿을 재생성해 `server.json`을 대조하라.
> 발행 자동화는 GitHub Actions로 가능: https://modelcontextprotocol.io/registry/github-actions

## 2. 디렉터리 / awesome 리스트 (수동 등재 — 전부 점유)

공식 Registry에 올리면 Glama 등 일부는 자동 색인되지만, 나머지는 수동 제출이 필요하다.

| 타깃 | URL | 방법 |
|---|---|---|
| 공식 MCP Registry | https://registry.modelcontextprotocol.io/ | `mcp-publisher publish` (위) |
| Glama | https://glama.ai/mcp/servers | 공개 repo 자동 색인 (오픈소스화만 하면 됨) |
| Smithery | https://smithery.ai | `smithery` CLI / 웹 제출 |
| mcp.so | https://mcp.so | 웹 Submit |
| PulseMCP | https://www.pulsemcp.com | 웹 Submit (수동 검수) |
| LobeHub | https://lobehub.com/mcp | 플랫폼 제출 |
| Cline 마켓플레이스 | https://github.com/cline/mcp-marketplace | PR/이슈 (repo URL + 400×400 PNG 로고) |
| awesome-mcp-servers (punkpeye) | https://github.com/punkpeye/awesome-mcp-servers | PR |
| awesome-mcp-servers (wong2) | https://github.com/wong2/awesome-mcp-servers | PR |
| awesome-mcp-servers (appcypher) | https://github.com/appcypher/awesome-mcp-servers | PR |
| mcpservers.org | https://mcpservers.org/submit | 웹 폼 (PR 불가) |

**등재 시 통일 카피(쐐기):** *"Not a paper-fetcher — a paper-reviewer. The only research MCP that covers the full workflow: deep multi-agent review, semantic search across 6 sources, citation-graph exploration, curricula, and figures (6/7 agentic capabilities; nearest competitor covers 2)."*

## 3. Claude Connectors Directory (앤트로픽 "검증" 배지)

⚠️ **블로커: 원격 전송 필요.** 현재 stdio 전용 → 디렉터리는 **원격 HTTPS + Streamable HTTP + OAuth 2.0**를 요구한다(README 로드맵 v1.0.0의 remote connector). 추가로 공개 **개인정보처리방침 URL**이 없으면 즉시 반려.
- 제출: https://clau.de/mcp-directory-submission
- 요구: 모든 툴에 `title` + `readOnlyHint`/`destructiveHint` 어노테이션. ✅ **완료** — 11개 툴 전부 `ToolAnnotations` 적용(읽기전용 6 / 쓰기 5, `remove_bookmark`는 `destructiveHint=True`+`idempotentHint=True`). 런타임 등록 검증됨.

## 4. 학술 인용 객체화

- [`CITATION.cff`](../../CITATION.cff) 추가됨 → GitHub repo에 "Cite this repository" 버튼 노출.
- 다음 단계(별도): GitHub Release ↔ Zenodo 연동으로 **DOI** 발급 → 프리프린트/논문에서 인용 가능.

## 체크리스트

- [ ] PyPI에 `jiphyeonjeon-mcp` 게시
- [x] README에 `mcp-name` 마커
- [x] `server.json` 작성 (스키마 2025-12-11)
- [ ] `mcp-publisher validate` 통과
- [ ] 공식 Registry 발행
- [ ] Glama/Smithery/mcp.so/PulseMCP/LobeHub/Cline 등재
- [ ] awesome-mcp-servers PR ×3 + mcpservers.org
- [x] `CITATION.cff` 추가
- [x] 툴 어노테이션(`title`/`readOnlyHint`/`destructiveHint`) — Connectors Directory 요건 일부 충족
- [ ] Zenodo DOI
- [ ] (원격 전송 출시 후) Claude Connectors Directory
