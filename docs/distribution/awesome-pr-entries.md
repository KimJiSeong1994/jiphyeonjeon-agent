# awesome-mcp-servers PR 엔트리 (붙여넣기용)

> 기둥 C "MCP 유통 플라이휠"용. 각 리스트 포맷에 맞춘 ready-to-paste 엔트리.
> **전제:** 공개 GitHub repo(오픈소스화). PR 전 README에 데모/설치가 명확해야 머지율이 높다.

## 통일 포지셔닝 (쐐기)
> 검색만 하는 다른 research MCP와 달리, 집현전은 **연구 워크플로우 전체**(딥 멀티에이전트 리뷰 · 6개 소스 시맨틱 검색 · 인용 그래프 · 커리큘럼 · 피겨)를 에이전트 네이티브 툴로 제공.

---

## 1. punkpeye/awesome-mcp-servers
**Repo:** https://github.com/punkpeye/awesome-mcp-servers
**레전드:** 🐍 = Python, 🏠 = Local Service. (집현전은 stdio 로컬 서비스 + Python → `🐍 🏠`)
**카테고리:** 검색/연구 성격 → "Search" 또는 "Knowledge & Memory" 섹션. (메인테이너가 재분류할 수 있음 — PR 설명에 의견 제시)

붙여넣기 라인:
```markdown
- [KimJiSeong1994/jiphyeonjeon-agent](https://github.com/KimJiSeong1994/jiphyeonjeon-agent) 🐍 🏠 - Agent-native research workspace for academic papers: deep multi-agent arXiv review, multi-source semantic search, citation-graph exploration, learning curricula, and figure generation (wraps 집현전 / PaperReviewAgent).
```

## 2. wong2/awesome-mcp-servers
**Repo:** https://github.com/wong2/awesome-mcp-servers
**포맷:** 이모지 없이 간결. (Community Servers 섹션, 알파벳 순)
```markdown
- [jiphyeonjeon-agent](https://github.com/KimJiSeong1994/jiphyeonjeon-agent) - Deep paper review, multi-source search, citation graphs, and learning curricula for arXiv papers as MCP tools.
```

## 3. appcypher/awesome-mcp-servers
**Repo:** https://github.com/appcypher/awesome-mcp-servers
**포맷:** `**Name** - description` (Bold 이름 + 링크)
```markdown
- **[Jiphyeonjeon](https://github.com/KimJiSeong1994/jiphyeonjeon-agent)** - An MCP server that turns Claude into a full research agent: deep multi-agent paper review, semantic search across 6 sources, citation-graph exploration, curricula, and figure generation.
```

## 4. mcpservers.org
**제출:** https://mcpservers.org/submit (웹 폼, PR 불가)
- Name: `Jiphyeonjeon (집현전)`
- Repo: `https://github.com/KimJiSeong1994/jiphyeonjeon-agent`
- Description: 위 통일 포지셔닝 1–2문장.

---

## PR 제목/본문 템플릿 (punkpeye/wong2/appcypher 공통)

**제목:**
```
Add jiphyeonjeon-agent (academic paper deep-review MCP server)
```

**본문:**
```markdown
Adds **jiphyeonjeon-agent**, an open-source Python MCP server (stdio) that exposes
집현전 (PaperReviewAgent) as native tools for Claude and other MCP clients.

Unlike search/fetch-only research servers, it covers the full research workflow:
- `search_papers` — semantic search across arXiv, Google Scholar, OpenAlex, DBLP, Connected Papers, OpenAlex Korean
- `start_review` / `get_review_status` — deep multi-agent paper review (contributions, method, limitations)
- `explore_related` — citation-graph exploration (cites / cited-by)
- `create_curriculum` — structured learning roadmaps
- `generate_figure` — methodology → SVG diagram
- bookmarks, blog drafts

Repo: https://github.com/KimJiSeong1994/jiphyeonjeon-agent
License: Apache-2.0 · Tools annotated with readOnly/destructive hints.

I placed it under <CATEGORY>; happy to move it if a better section fits.
```

> ⚠️ 각 리스트의 CONTRIBUTING 규칙(알파벳 순 정렬, 1 PR=1 추가, 설명 길이)을 PR 전 확인할 것. 자기 프로젝트 추가는 대부분 허용되나 "왜 유용한지"가 분명해야 머지된다.
