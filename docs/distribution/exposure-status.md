# 노출 상태 트래커 (Exposure / Keyword Tracker)

> SEO·GEO 전략(`../strategy/seo-geo-strategy.md`) 실행의 **라이브 상태**.
> 범례: 🟢 live · 🟡 트리거 대기(곧 켜짐) · 🔴 미작동(작업 필요)
> **최종 업데이트: 2026-06-19**

## 요약
현재 실노출은 **브랜드/GitHub 직검색 수준**. "research/MCP 키워드"는 **Glama 자동색인 + MCP 디렉터리 웹폼 제출(mcp.so·PulseMCP·mcpservers.org)** 이 반영되면 노출 시작된다. (**punkpeye awesome 리스트는 제외**, 2026-06-19 — PR #8291 closed.) 논문·비교·한국·브랜드 키워드는 각각 별도 작업이 선행돼야 한다.

## 🟢 오늘 라이브
- **브랜드 직검색**: `jiphyeonjeon`, `집현전 mcp` → GitHub repo / 사이트
- **GitHub 검색·코드검색**: repo public + README 영어 정의·키워드 → `paper review mcp`, `arxiv mcp` 류로 repo 자체 노출

## 🟡 곧 켜질 것 (트리거 대기 — 이번 작업의 결과)
| 트리거 | 상태(2026-06-19) | 켜지면 노출되는 키워드군 | 확인 방법 |
|---|---|---|---|
| **MCP 디렉터리 등재** (mcp.so · PulseMCP · mcpservers.org) | 🔴 미제출 | `best MCP server for research` · `academic MCP server` · `arxiv MCP` · `research MCP` — LLM이 인용하는 디렉터리 코퍼스 진입 | 각 사이트 검색 |
| **Glama 자동색인** | 🟡 미색인 | glama.ai `research / paper` 디렉터리 검색 | https://glama.ai/mcp/servers?query=jiphyeonjeon |

> 보조 채널(웹폼 제출 시 추가 노출): **wong2(=mcpservers.org/submit)**, **appcypher** — 현재 메인테이너 PR 제한으로 fork PR 차단. 제출용 엔트리 내용은 [`awesome-pr-entries.md`](./awesome-pr-entries.md). 추가로 mcp.so / PulseMCP / Smithery 웹 제출.

## 🔴 미작동 (다음 단계 필요)
| 키워드군 | 예시 | 필요한 작업 |
|---|---|---|
| 특정 논문 이해 | `explain this paper`, `{논문} summary`, `{paper} explained` | 봇 prerender + 공개 리뷰 페이지 (기둥 A·B) |
| 비교 | `Elicit vs SciSpace`, `Perplexity alternative for research` | 비교 페이지 (기둥 D) |
| 한국 | `논문 딥리뷰`, `arxiv 한글 요약`, `인용 그래프`, `논문 커리큘럼` | 한국어 콘텐츠 + Naver 등록 (한국 트랙) |
| 공식 MCP Registry 검색 | registry.modelcontextprotocol.io | `.mcpb` 번들 발행 (PyPI 제외 → mcpb 경로) |
| 브랜드 엔티티(지식그래프) | Knowledge Graph / disambiguation | Wikidata 아이템 생성 |

## 점검 루틴 (월간 권장)
1. MCP 디렉터리(Glama / mcp.so / PulseMCP / mcpservers.org) 등재 여부 → 등재되면 해당 행을 🟢로 이동, 키워드군을 "오늘 라이브"로 승격. (punkpeye는 제외.)
2. Glama 색인 여부(위 URL).
3. 코퍼스 진입 후 — 고정 쿼리셋(`best AI tool to review a paper`, `MCP server for research`, `summarize an arXiv paper`, `Elicit alternative`)을 ChatGPT/Perplexity/Claude/AI Overviews에 질의 → 집현전 인용/추천 여부 기록 (전략 §7 Share-of-Voice).
