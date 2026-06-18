# MCP 유통 플라이휠 — 발행 가이드

> SEO·GEO 전략(`docs/strategy/seo-geo-strategy.md`) 기둥 C "MCP 유통 플라이휠"의 실행 문서.
> 각 등재 = 백링크 + LLM이 읽는 코퍼스 항목 + 발견 채널. UI/UX 무변경, 이 repo에서 즉시 실행 가능.

> ### ⛔ 결정(2026-06-18): **PyPI 게시 제외**
> PyPI에 올리지 않는다. 영향:
> - **공식 MCP Registry의 `pypi` 경로는 사용 불가** (레지스트리가 실제 PyPI 패키지로 소유권 검증). → 대안: **`mcpb`**(GitHub 릴리스 아티팩트로 등재, PyPI 불필요) 또는 **`oci`**(ghcr.io 이미지). **권장: `mcpb`** (§1B).
> - **GitHub-repo 기반 채널(Glama·awesome·mcp.so·PulseMCP)은 영향 없음** — PyPI 불필요. 지금 즉시 진행 가능한 주 경로(§2).
> - **설치**도 PyPI 불필요: `uvx --from git+https://github.com/KimJiSeong1994/jiphyeonjeon-agent jiphyeonjeon-mcp` 또는 README의 clone 방식.

## 0. 전제조건

1. **공개 GitHub repo.** Glama 자동색인·awesome PR·Show HN 검수의 전제. (이미 공개)
2. **GitHub 네임스페이스.** 공식 레지스트리 사용 시 서버 이름은 `io.github.<username>/...` 형식. (username = `KimJiSeong1994`, `server.json`의 `name`과 일치)
3. **소유권 검증 마커(레지스트리용).** `README.md` 상단에 추가됨 — `mcpb`에선 불필요하나 무해하므로 유지:
   ```html
   <!-- mcp-name: io.github.KimJiSeong1994/jiphyeonjeon-agent -->
   ```

## 1. 공식 MCP Registry 발행

### 1A. 현재 `server.json` (pypi 변형) — **PyPI 제외 결정으로 보류**
루트의 [`server.json`](../../server.json)은 `registryType: pypi` 변형이다. PyPI에 게시하지 않기로 했으므로 **이 상태로는 발행 불가**(레지스트리가 PyPI에서 패키지를 못 찾음). PyPI를 다시 허용할 때 사용할 참조 템플릿으로 유지.

### 1B. 권장: `mcpb` 변형으로 발행 (PyPI 불필요)
GitHub 릴리스에 `.mcpb` 번들을 올려 그 URL로 등재한다. 검증은 (a) URL에 `mcp` 포함(`.mcpb` 확장자로 충족) + (b) `server.json`의 `fileSha256`로 이뤄진다 — README 마커·PyPI 불필요.

```bash
# 1) .mcpb 번들 생성 (MCPB CLI). Python stdio 서버용 manifest 필요.
npx @anthropic-ai/mcpb init      # manifest.json 생성/편집
npx @anthropic-ai/mcpb pack      # -> jiphyeonjeon-agent.mcpb

# 2) GitHub 릴리스에 첨부
gh release create v0.1.3 --generate-notes
gh release upload v0.1.3 jiphyeonjeon-agent.mcpb

# 3) sha256 계산 → server.json(mcpb 변형)의 fileSha256 에 기입
openssl dgst -sha256 jiphyeonjeon-agent.mcpb

# 4) 발행
brew install mcp-publisher
mcp-publisher validate
mcp-publisher login github
mcp-publisher publish
curl "https://registry.modelcontextprotocol.io/v0.1/servers?search=jiphyeonjeon"
```

`mcpb` 변형 `server.json`의 `packages[]` 예시:
```json
{
  "registryType": "mcpb",
  "identifier": "https://github.com/KimJiSeong1994/jiphyeonjeon-agent/releases/download/v0.1.3/jiphyeonjeon-agent.mcpb",
  "fileSha256": "<openssl 결과>",
  "transport": { "type": "stdio" }
}
```

> ⚠️ Registry는 preview라 스키마가 바뀔 수 있음 — `mcp-publisher init`로 최신 템플릿 대조.
> 대안: `oci`(ghcr.io 이미지 + `io.modelcontextprotocol.server.name` LABEL). stdio Python 서버에는 `mcpb`가 더 자연스러움.
> **이 경로(1B)는 별도 빌드 작업이 필요** — 오너 승인 시 진행.

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
| ~~awesome-mcp-servers (punkpeye)~~ | https://github.com/punkpeye/awesome-mcp-servers | ⛔ **제외**(2026-06-19, PR #8291 closed) |
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

- [x] ~~PyPI에 `jiphyeonjeon-mcp` 게시~~ — **제외 결정**(2026-06-18). 공식 레지스트리는 `mcpb`로 대체
- [x] README에 `mcp-name` 마커 (mcpb에선 불필요하나 유지)
- [x] `server.json` 작성 (스키마 2025-12-11, pypi 변형 — 보류)
- [~] **진행 중 (PyPI 불필요):** punkpeye ⛔**제외**(PR #8291 closed, 2026-06-19) · wong2·appcypher 웹폼 제출 · Glama 자동색인 🟡대기 · mcp.so/PulseMCP/Smithery 제출 예정 → 라이브 상태는 [`exposure-status.md`](./exposure-status.md)
- [ ] (오너 승인 시) `.mcpb` 번들 빌드 → GitHub 릴리스 첨부 → `mcpb` 변형 `server.json` → 공식 Registry 발행
- [x] `CITATION.cff` 추가
- [x] 툴 어노테이션(`title`/`readOnlyHint`/`destructiveHint`) — Connectors Directory 요건 일부 충족
- [ ] Zenodo DOI
- [ ] (원격 전송 출시 후) Claude Connectors Directory
