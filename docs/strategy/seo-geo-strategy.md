# 집현전(集賢殿 / Jiphyeonjeon) — SEO·GEO 심층 성장 전략

> **작성:** 5개 전문 에이전트(GEO · 테크니컬SEO/콘텐츠엔진 · 오프페이지/권위 · 경쟁/포지셔닝 · 한국트랙) 병렬 리서치 → 통합
> **작성일:** 2026-06-18 · **기준 연도:** 2026
> **전략 프레임(확정):** **글로벌 우선**(영어/arXiv + MCP 생태계, 한국은 보조 ~20%), **1차 KPI = 연구 커뮤니티 권위**(가입자 수가 아니라 "신뢰·인용·추천받는 출처"가 되는 것)

> ### ⛔ 하드 제약 (2026-06-18 추가): **웹 UI/UX 무변경**
> 사람 사용자가 보는 화면·동작·디자인은 **일절 바꾸지 않는다.** 따라서:
> - 온사이트 차단요인은 **SSR/Next.js 리라이트가 아니라 "봇 전용 prerendering / dynamic rendering"** 으로 해결 — 사람은 현재 React SPA 그대로, 크롤러 UA만 HTML 스냅샷 수신.
> - 보이지 않는 작업(robots.txt·sitemap.xml·llms.txt·`<head>` 메타/canonical/JSON-LD/hreflang·아이콘 파일 교체·Bing/GSC 등록)은 모두 허용.
> - **새 공개 페이지 타입 신설**(신규 디자인 랜딩·토픽 허브 등)은 UI 변경이므로 보류 → 콘텐츠 색인은 *앱이 이미 공개 라우트에서 보여주는 것*에 한정(§3 기둥 B).

---

## 0. 전략 한 줄 요약 (The Thesis)

> **집현전의 권위 해자(moat)는 "에이전트 네이티브"다. 순수 SEO 경쟁사는 *언급(mention)*만 노릴 수 있지만, 집현전은 에이전트가 직접 *호출(invoke)*한다 — 인용·사용·출처표기가 한 번에 일어난다.**
> 따라서 노력은 **(1) AI가 읽을 수 있는 사이트로 만들기 → (2) 딥리뷰 코퍼스를 색인 자산화 → (3) MCP 유통 플라이휠 → (4) 권위·GEO 측정**의 순서로 집중한다. 이 네 가지 중 (3)만 지금 당장 비용 거의 0으로 시작 가능하고, (1)이 나머지 전부의 전제다.

---

## 1. 정정된 핵심 쐐기 (Reframed Wedge) — 반드시 이걸로 통일

리서치 중 가장 중요한 사실 정정:

- ❌ **"집현전은 유일하게 MCP 서버가 있다"** → **틀림.** 2026년 현재 Consensus·Elicit·scite·SciSummary 모두 MCP 서버 운영.
- ✅ **검증된 진짜 우위:** 경쟁사 MCP는 전부 **검색/조회 전용**. 집현전만 **연구 워크플로우 전체**를 에이전트 툴로 노출.

| MCP를 통한 역량 | Consensus | Elicit | scite | SciSummary | **집현전** |
|---|---|---|---|---|---|
| 검색(search) | ✅ | ✅ | ✅ | – | ✅ |
| 딥 구조화 리뷰 | – | – | – | – | **✅** |
| 인용 그래프 탐색 | – | – | 부분 | – | **✅** |
| 학습 커리큘럼 | – | – | – | – | **✅** |
| 피겨 생성 | – | – | – | – | **✅** |
| 블로그/초안 생성 | – | – | – | – | **✅** |
| 사용자별 북마크 | – | – | – | – | **✅** |

**→ 집현전은 7개 중 6개를 커버하는 유일한 MCP. 최근접 경쟁사는 2개.** 검증 가능하다는 점이 곧 권위가 된다.

**모든 채널에서 통일할 카피:**
- 카테고리: **"agent-native research workspace"** / "the research agent that lives inside your AI"
- 쐐기 한 줄(택1): *"The research agent your AI plugs into."* / *"Don't summarize papers. Review them — inside Claude."*
- ⚠️ 시간제약: SciSpace가 "deep understanding" 포지션에 가장 근접(아직 MCP 없음). **12개월 내 워크플로우 MCP 출시 가정 → 이 쐐기를 선점할 창은 약 6–12개월.**

---

## 2. 0순위 차단요인 — 이걸 고치기 전엔 아무것도 작동하지 않는다

### 2.1 사이트가 AI에게 "백지"다 (실측)
jiphyeonjeon.kr을 Googlebot으로 페치한 실측 결과:
- 홈 HTML 총 **1,562바이트**, `<body>`는 `<div id="root"></div>`뿐인 **순수 클라이언트 렌더 React SPA(Vite)**.
- **대부분의 AI 크롤러(GPTBot·ClaudeBot·PerplexityBot·OAI-SearchBot)는 JS를 실행하지 않음** → 사이트 전체가 빈 div로 보임. KPI("AI가 인용하는 출처")에 거의 치명적.
- Google은 JS를 렌더하지만 "수 시간~수 주" 지연 + 크롤예산 추가비용.

### 2.2 동반 결함들
| 항목 | 현재 상태 | 문제 |
|---|---|---|
| 라우팅 | 모든 경로가 `200 + 셸` 반환(`/llms.txt`, `/paper/...` 포함) | 대규모 soft-404 → 크롤예산·신뢰 오염 |
| canonical | 모든 경로 static `canonical=/` | 프로그래매틱 페이지 전부가 홈으로 정규화 = 색인 붕괴 |
| sitemap | URL 2개짜리 placeholder | 심층 페이지 발견 불가 |
| /llms.txt | 없음(셸 반환) | 에이전트 네이티브 제품인데 미존재 |
| robots.txt | OAI-SearchBot 허용 / GPTBot 차단(정교함) | 그러나 ClaudeBot·PerplexityBot·**Bingbot** 규칙 누락 |
| 소셜/스키마 | `twitter:image` 없음, JSON-LD 전무, 6.99MB 아이콘 | 프리뷰 깨짐 + 스키마 0 + CWV 부담 |

**결론:** 현재 사이트는 "AI가 인용하지 *않도록*" 거의 완벽하게 설계되어 있음. 이걸 뒤집는 게 1번 — **단, 프론트 리라이트가 아니라 "봇 전용 prerendering"으로**, 사람 UI/UX는 손대지 않고 해결한다(§3 기둥 A).

---

## 3. 네 개의 전략 기둥 (통합)

### 기둥 A — 기반: "기계가 읽는 집현전" 만들기 *(전제, P0)*

1. **봇 전용 prerendering / dynamic rendering (UI/UX 무변경 — 이 제약 하의 확정 방식).** 사람 사용자에게는 **현재 React SPA를 그대로** 서빙하고, 크롤러 UA(Googlebot·Bingbot·GPTBot·ClaudeBot·PerplexityBot·OAI-SearchBot·Claude-SearchBot 등)만 가로채 **완전 렌더된 HTML 스냅샷**을 반환. 구현: nginx/엣지(Cloudflare Worker)에서 UA 분기 → headless-chrome 프리렌더(self-host Rendertron/Prerender 또는 빌드시 SSG 스냅샷 캐시). **봇·사람에게 *같은 콘텐츠*를 다르게 렌더하는 것이라 클로킹 아님**(구글이 명시 허용하는 dynamic rendering). 사람 UI/UX는 바이트 단위로 동일.
   - 이 레이어가 **페이지별 head(title/meta/canonical/og/twitter/hreflang) + JSON-LD를 스냅샷에 주입** → SPA 가시 UI 무변경으로 §2.3 결함 동시 해결.
   - React 앱·FAISS는 손대지 않음. 리뷰 텍스트·그래프는 이미 SQLite에 영속이므로 헤드리스 렌더가 그대로 캡처.
   - ⚠️ 운영주의: AI 봇 UA는 변함 → UA 목록·스냅샷 캐시 유지보수 필요. **SSR/Next.js 전면 이관은 UI 무변경 제약상 제외.**
2. **페이지별 self-canonical + head 태그**(SSR로만 신뢰 가능).
3. **soft-404 제거:** 쓰레기 URL은 진짜 404 반환. nginx가 유효 SPA 라우트 vs 가비지 구분.
4. **robots.txt 재정비** — KPI가 "인용되기"이므로 **검색/실시간 리트리벌 봇 전부 허용**:
   - 허용(필수): `Googlebot`, **`Bingbot`(ChatGPT/Copilot 공급원 — 절대 누락 금지)**, `OAI-SearchBot`, `Claude-SearchBot`/`Claude-User`, `PerplexityBot`.
   - 학습 크롤러(`GPTBot`·`ClaudeBot`·`Google-Extended`·`CCBot`)는 **결정 포인트**: 보수적 기본=차단이지만, *권위 KPI* 관점에선 모델 가중치에 브랜드가 들어가 "무프롬프트 추천"을 유도하도록 **허용**하는 것도 타당. → 오너 결정 필요(§6).
5. **Bing Webmaster Tools 등록 + 완전 색인.** ChatGPT 인용의 ~87%가 Bing 인덱스에서 옴 → 인덱스에 없으면 인용 자체가 불가능.
6. **sitemap index + 샤딩**(child당 5만 URL), 실제 `lastmod`. **색인 의도 URL만 포함**(§B 티어링).
7. **사이트 공통 JSON-LD:** `Organization`(+`sameAs`→Wikidata/GitHub/SNS), `WebSite`+`SearchAction`.
8. **hreflang en/ko/x-default**(실제 번역이 있는 ko 페이지만).
9. CWV 위생: 6.99MB 아이콘 압축, 그래프/마크다운 번들 lazy-load.

> ⚠️ **CWV/렌더 검증은 추측 금지** — Claude/Anthropic LLM 작업이 아닌 일반 웹 작업이므로, SSR 적용 후 실제 봇 페치(GSC URL 검사 + `curl`)로 본문 노출을 *관측*해 확인.

### 기둥 B — 콘텐츠 해자: 딥리뷰 코퍼스의 색인 자산화 *(P1, 최대 레버)*

> **UI/UX 무변경 제약 적용:** 새 *공개 페이지 타입 신설*(신규 디자인 랜딩·토픽 허브 등)은 UI 변경이므로 보류. **이미 앱이 공개(비로그인) 라우트에서 보여주는 콘텐츠를 prerender해 색인**하는 데 한정한다. 즉 아래 '원본 가치'(딥리뷰·피겨·관련그래프)는 *현재 SPA가 이미 표시 중인 것*이어야 캡처 가능 — 미표시 콘텐츠를 공개 페이지로 노출하는 것은 별도 의사결정(§6). `/topic` 허브가 현재 앱에 없다면 본 제약 하에선 후순위/보류.

집현전이 리뷰한 논문 1편 = **본질적으로 유용한** 색인 가능 랜딩페이지 1개. arXiv 규모로 수천~수만 페이지. **단, 가드레일이 "권위 엔진"과 "스팸 페널티"를 가른다.**

- **URL:** `/paper/{arxiv_id}`(+가독 슬러그), 토픽 허브 `/topic/{slug}`. `/papers/` vs `/paper/` 중복 → 301 통일.
- **페이지 템플릿(arXiv 초록을 넘는 *원본 가치* 필수, 중복콘텐츠 회피):**
  1. 쉬운 말 해설(자체 산문, 초록 재탕 금지) 2. **딥리뷰 분석**(기여·방법비평·한계·재현성 — *arXiv엔 없는 해자*) 3. 생성 피겨(+`ImageObject` 스키마·alt) 4. 관련논문 그래프(서버 렌더 링크 = 내부링크 엔진) 5. 핵심 takeaway Q&A(LLM이 답변에 떠가는 포맷) 6. 메타(저자·venue·arXiv 원문 링크).
- **JSON-LD:** `ScholarlyArticle` + 중첩 `Review`(`itemReviewed`→arXiv DOI) + `BreadcrumbList`. → "원본 리뷰 객체"로 기계가 인식.
- **canonical:** **항상 self-canonical. arXiv로 정규화 금지**(랭킹 전부 헌납하게 됨). arXiv는 `sameAs`+가시 링크로 정직하게 연결.
- **티어드 색인(arXiv 규모에서 필수):** Tier1=완성 딥리뷰+피겨+그래프 → `index`, sitemap 포함 / Tier2=부분/자동데이터 → `noindex,follow` / Tier3=제목뿐 → URL 미발행. **페이지 존재가 가치에 게이팅됨을 구글에 증명** = scaled-content-abuse 최대 방어.
- **품질 가드레일(2024–2026 helpful-content/scaled-content-abuse/site-reputation 통과):** 페이지별 고유 분석 레이어 + 고유 미디어 + 초록 재작성·무검수 자동번역 금지 + **E-E-A-T**(방법론 공개, 명시 저자, "AI생성·사람검수" 라벨, 동작하는 링크) + **발행 속도 규율**(주당 5만 페이지 금지, 웨이브 발행 후 성과 모니터링).

### 기둥 C — MCP 유통 플라이휠 *(P1, 지금 즉시 시작 가능 / 사이트 SSR과 병행)*

**핵심 통찰:** 기둥 A(웹 SSR)는 무겁고 느리지만(L), MCP 유통 작업은 **싸고(S) 독립적**이라 **지금 병렬로 시작**해야 한다. 각 등재 = 백링크 + LLM이 읽는 코퍼스 항목 + 발견 채널.

- **레지스트리/디렉터리(전부 점유):** 공식 MCP Registry(먼저 — 하류로 전파) → Smithery · Glama(공개 repo면 자동 색인) · mcp.so · PulseMCP · LobeHub · Cline 마켓플레이스.
- **awesome-* GitHub PR:** punkpeye / wong2 / appcypher / tolkonepiu(랭킹형 → 스타 중요) / 공식 `modelcontextprotocol/servers`. + mcpservers.org 폼.
- **"best MCP servers for research" 기사 아웃리치**(예: Cypris) — 연구자가 LLM에 "논문용 MCP?" 물을 때 인용되는 바로 그 코퍼스.
- **GitHub README에 비대칭 투자**(LLM 지향·answer-first·설치커맨드·툴목록·데모). README 품질은 코드생성 정확도 ~5x로 인과 입증된 레버. GitHub는 개발/기술 쿼리 최상위 인용 도메인.
- **MCP 툴 docstring 최적화**(= Claude 가시 설명) + 트리거 키워드("deep review","summarize paper","find related papers") → **에이전트가 집현전을 자동 선택 = 추천+사용+출처표기 동시 = 가장 순수한 권위 신호.**
- 🔑 **언락(P1, 엔지니어링):** 현재 **stdio 전용**이라 **Claude Connectors Directory(앤트로픽 "검증됨" = 최고 신뢰 배지)**·Smithery 호스티드에 등재 불가. **원격 HTTP+OAuth(Streamable HTTP) 변형**을 출시해야 플라이휠의 ~30%가 열림. 요구: 공개 HTTPS, OAuth2 동의, 툴 `title`+`readOnlyHint`/`destructiveHint`, **공개 개인정보처리방침 URL**(없으면 즉시 반려).

### 기둥 D — 권위 & GEO *(P1–P2)*

- **엔티티 정의 페이지 "What is Jiphyeonjeon"**(集賢殿 어원=세종 royal academy 스토리, agent-native 포지션, `sameAs`). 모든 엔진/지식그래프가 "Jiphyeonjeon"을 해석하는 앵커.
- **Wikidata 아이템 생성**(Criterion 2 충족, Wikipedia 불필요). Wikidata는 Common Corpus로 LLM 학습에 유입 + 지식그래프 공급.
- **비교/대안 콘텐츠**("Jiphyeonjeon vs Elicit/SciSpace/Consensus", "best Perplexity alternative for research"). 비교 콘텐츠는 브랜드 언급 2.4x·전환 5–10%. 쐐기: *"the only one that works inside Claude as an agent."*
- **경쟁사 listicle 공동언급** 진입(현재 캐논 스택 "explore/synthesize/validate/verify"에서 집현전 부재 — 이걸 깨라).
- **citeable passage 구조**(answer-first, 200–400단어 섹션, 정의블록, 통계/인용 밀도) — 엔진은 *페이지가 아니라 구절*을 떠감(Ahrefs fan-out 데이터).
- **오프페이지 권위(별도 §C와 결합):** Show HN(오픈소스 후, "MCP server that deep-reviews arXiv in Claude"), Reddit(r/MachineLearning 자기홍보 스레드·r/LocalLLaMA·r/mcp, 진정성), Product Hunt, **자체 데이터 리포트 "State of AI Research 2026"**(코퍼스 기반 = 최강 링크베이트), 뉴스레터(Latent Space·The Batch·TLDR AI·Import AI), arXiv 툴 프리프린트(cs.DL/cs.IR — 도구 자체를 인용가능 객체로), CITATION.cff + Zenodo DOI.
- **llms.txt / llms-full.txt**(MCP 엔드포인트 + `claude mcp add` 설치커맨드 + 툴목록). SEO 효과는 약하지만 **Claude가 유일 확인 소비자**이고 타깃이 에이전트라 *온브랜드*.

---

## 4. 한국 보조 트랙 (~20% 노력)

- **원칙:** Naver 조직 SERP에서 .kr SaaS 웹문서를 랭크시키려 하지 말 것(Naver는 자사 UGC를 구조적으로 우대). 대신 **연구·개발 권위 표면**과 **Naver AI 인용**을 노린다.
- **Naver:** Search Advisor 등록(table-stakes, S) + **AI 브리핑** 겨냥(⚠️ Cue:는 2026-04-09 종료). AI 브리핑은 정의형 쿼리에서 Top10 밖도 인용(겹침 ~28.6%) → **구조화 한국어 포스트**(FAQ/방법/이유, H2/H3, 불릿, 6–8k자)로 `arxiv 한글 요약`·`논문 딥리뷰란`·`인용 그래프` 공략(공식 Naver Blog).
- **Google KR:** `논문 요약`(레드오션, 포기)이 아니라 **`논문 딥리뷰`·`arxiv 한글 요약`·`인용 그래프 한글`·`논문 커리큘럼`**(차별·저경쟁) 공략. hreflang ko/en.
- **커뮤니티(권위 적합순):** **GeekNews "Show GN"**(MCP 앵글, 최고 레버) · **PyTorchKR 정보공유**(연구자 = 1차 KPI 타깃) · **velog**(영문 슬러그, Google-KR SEO) · 김박사넷(대학원생, 진정성) · 가짜연구소(스터디그룹 장기전) · 디스콰이엇(메이커로그). OKKY/클리앙/TF-KR = 스킵.

---

## 5. 통합 로드맵 (2-트랙 병행)

> 웹 기반(트랙1, 무겁다)과 MCP/오프페이지(트랙2, 싸고 독립)를 **동시에** 굴린다. 트랙2의 즉시 착수가 핵심.

**스프린트 1 (Wk1–2) — 기반 + 수동 백링크**
- 트랙1: **봇 prerender 레이어 도입(UI 무변경)** — 기존 공개 라우트(`/paper` 등) 스냅샷 + head/JSON-LD 주입, robots.txt 재정비, Bing Webmaster 등록, soft-404 수정, sitemap index.
- 트랙2: **MCP 서버 오픈소스화**(키워드 README) → Glama 자동색인 + Show HN 검수가능 + awesome PR 전제. CITATION.cff+Zenodo DOI. 공식 MCP Registry 발행. 공개 개인정보처리방침 URL.

**스프린트 2 (Wk3–4) — MCP 표면 포화 + 콘텐츠 골격**
- 트랙2: Smithery·mcp.so·PulseMCP·LobeHub·Cline 등재, awesome-* PR ×4 + mcpservers.org. **원격 HTTP+OAuth 변형** 결정·착수 → Claude Connectors Directory 제출.
- 트랙1: `/paper/{id}` 템플릿 + JSON-LD(`ScholarlyArticle`+`Review`) + 티어드 색인 + HITL QA 게이트. 엔티티 페이지 + Wikidata.

**스프린트 3 (Wk5–6) — 링크베이트 생산**
- "State of AI Research 2026" 데이터 리포트(코퍼스 기반) 착수, 무로그인 미니툴, citeable-passage 리구조화, AI-가시성 추적(Otterly/Peec) 셋업 + SoV 쿼리셋 정의.

**스프린트 4 (Wk7–8) — 코디네이트 런치**
- Show HN(화/수 AM PT, 오픈소스 라이브) + Product Hunt(30일 사전준비 완료) + Lobsters + r/LocalLLaMA·r/ML. 한국: GeekNews Show GN + PyTorchKR.

**스프린트 5 (Wk9–10) — PR 증폭**
- 데이터 리포트를 뉴스레터/팟캐스트에 피칭. "best MCP servers for research" 기사 저자에 집현전 추가 요청. 비교 페이지 발행.

**스프린트 6 (Wk11–13) — 학술 내구성**
- arXiv 툴 프리프린트(cs.DL/cs.IR), 대학 강의/리딩그룹 페이지 ×10–20 아웃리치, 가짜연구소 스터디그룹.

---

## 6. 오너 결정 필요 (블로커/오픈 퀘스천)

1. **원격 MCP 전송 출시?** stdio 전용 → Claude Connectors Directory(최고 신뢰 배지)·Smithery 호스티드 불가. **플라이휠 ~30%를 게이트.** (가장 큰 구조적 갭)
2. **공개 개인정보처리방침 URL** 현존 여부? — 앤트로픽 디렉터리 하드 전제 + 모든 학술 아웃리치 신뢰 신호.
3. **MCP 서버 소스 공개?** — Glama 자동색인·Show HN/Lobsters 검수·awesome PR 전부의 전제.
4. **학습 크롤러(GPTBot/ClaudeBot/CCBot) 차단 vs 허용** — 권위 KPI상 "허용해 모델 가중치 진입"이 타당할 수 있음. 전략적 결정.
5. **딥리뷰 *출력 품질*이 인용 등급인가?** — 기둥 B 전체가 여기 의존. 툴 존재는 확인됨, 품질은 미감사 → 공개 코퍼스 발행 전 SciSpace "Deep Review"와 head-to-head 품질 감사 필요(architect/scientist 핸드오프).
6. **arXiv 콘텐츠 권리** — 딥리뷰 대량 공개 색인 + "State of arXiv" 집계 리포트의 ToS/재현 한계 확인.
7. **브랜드 콜사인** — "Jiphyeonjeon"은 글로벌 회상/철자 난도 높음. 권장: **개명 X, 콜사인 "Jip" + 설명어 페어링("the research agent for Claude") + 로마자 1개로 고정**(GEO에서 철자 변형은 인용그래프를 분산시킴) + 발음 가이드 스키마.
8. **타깃 학문 분야 비중**(CS/ML vs bio/med vs 일반) — RRID·Papers with Code·서브레딧/강의 선택을 좌우.

---

## 7. 권위 KPI 측정 (정의)

- **AI Share-of-Voice:** 고정 쿼리셋(예: "best AI tool to review a paper", "summarize an arXiv paper", "MCP server for research", "Elicit alternative", "literature review AI")에 대해 ChatGPT·Perplexity·Gemini·AI Overviews·Claude가 집현전을 인용/추천하는 비율 — 엔진별 월간.
- **도구:** Otterly.AI / Peec AI / Profound 중 택1. "ghost citation"(인용은 됐는데 브랜드 미언급 ~62%) 때문에 **링크 인용 + 비링크 브랜드 언급 둘 다** 추적.
- **백링크/언급:** Reddit·GitHub·HN·listicle 모니터링(인용의 선행지표).
- **AI 봇 로그 분석:** GPTBot·ClaudeBot·PerplexityBot·OAI-SearchBot·Google-Extended 크롤 여부 확인 — 리트리벌 봇이 차단돼 있으면 인용에서 사라짐.
- 한국: Naver "AI 브리핑 인용수"(2026-01부터 누적 추적, ⚠️ 단일 출처) 모니터.

---

## 8. 마스터 우선순위 표 (통합)

| 우선 | 액션 | 권위 KPI에 기여하는 이유 | 노력 | 임팩트 |
|---|---|---|---|---|
| **P0** | **봇 prerender/dynamic rendering**(UI 무변경, 기존 라우트 스냅샷+head/JSON-LD 주입) | AI 봇은 JS 미실행 — 안 하면 코퍼스 전체가 비가시. 사람 UI는 그대로 | M | High |
| **P0** | robots.txt: Bingbot·Claude-SearchBot·PerplexityBot 허용 | Bing→ChatGPT/Copilot; 명시 허용 = AI 답변 등장 | S | High |
| **P0** | **Bing Webmaster 등록 + 완전 색인** | ChatGPT 인용 87%가 Bing 인덱스 출처 | S | High |
| **P0** | soft-404 제거 + 페이지별 self-canonical | 크롤예산·신뢰 보호; 코퍼스의 홈-정규화 붕괴 방지 | S–M | High |
| **P1** | **MCP 서버 오픈소스화**(키워드 README) | Glama 자동색인·Show HN 검수·awesome PR 전제; README는 LLM 코퍼스 | S | High |
| **P1** | 공식 MCP Registry 발행 | 캐논 상류 피드 → 하류 전파 | S | High |
| **P1** | 쐐기 재정의("워크플로우 6/7 MCP") + 역량 스코어카드 전파 | 검증가능·고유 = 인용되는 바로 그 주장 | S | High |
| **P1** | **딥리뷰 코퍼스 색인 자산화**(원본가치 템플릿+JSON-LD+티어드 색인+HITL) | 문자 그대로 "AI가 인용하는 출처"; 제품 데모 겸 GEO 자산 | L | High |
| **P1** | MCP 툴 docstring + 트리거 키워드 최적화 | 직접 호출 = 추천+사용+출처표기; MCP 고유 최순수 신호 | S | High |
| **P1** | 엔티티 페이지 + Wikidata | 엔티티 정의 통제 + 지식그래프/학습코퍼스 진입 | S–M | High |
| **P1** | citeable passage 리구조화(answer-first/정의/통계) | 엔진은 구절을 떠감 → 추출가능 출처화 | M | High |
| **P1** | 비교 페이지("vs Elicit/SciSpace/Consensus") | 브랜드언급 2.4x·전환 5–10%; 경쟁 공동언급 진입 | M | High |
| **P1** | awesome-* PR + 디렉터리(Smithery/mcp.so/PulseMCP/LobeHub/Cline) | 영구 백링크 + 코퍼스 항목; 복리 | M | High |
| **P1** | E-E-A-T 레이어(Org 스키마·명시저자·방법론·"AI생성/사람검수" 라벨) | 권위 KPI 직결; 엔진·구글 보상 | M | High |
| **P1** | "Cluster E" 선점("academic MCP server" 등 미개척) | 무경쟁·최고복리 권위 표면; 개발/AI 커뮤니티 = KPI 청중 | M | High |
| **P2** | 원격 HTTP+OAuth MCP → Claude Connectors Directory | 무료 "앤트로픽 검증" 배지; stdio 탈피 필요 | L | Med–High |
| **P2** | "State of AI Research 2026" 데이터 리포트 | 원본 1차 데이터 = 최강 링크베이트 | L | High |
| **P2** | Show HN(오픈소스 후) + Product Hunt + Lobsters | 개발 커뮤니티 백링크·스타·버즈 | M | High/Med |
| **P2** | 뉴스레터/팟캐스트 피칭(Latent Space·The Batch·TLDR AI…) | 언급 = 백링크+GEO+ICP 도달 | M | High |
| **P2** | sitemap index + 샤딩(`lastmod`) | 심층 페이지 발견·재크롤 제어 | S | High |
| **P2** | 인용그래프 내부링크(서버렌더) | 진짜(가짜 아님) 링크 구조; 권위 분배·고아 방지 | M | Med |
| **P2** | arXiv 툴 프리프린트(cs.DL/IR) + CITATION.cff+Zenodo DOI | 도구를 인용가능 학술 객체화; Semantic Scholar 색인 | M | High |
| **P2** | AI-가시성 추적(Otterly/Peec) + SoV 쿼리셋 | 권위 KPI는 측정해야 관리됨; 베이스라인 | S–M | Med–High |
| **P2** | 한국: GeekNews Show GN + PyTorchKR + velog | 국내 연구/개발 권위 표면(1차 KPI 청중) | S–M | High(KR) |
| **P3** | llms.txt/llms-full.txt(MCP 엔드포인트+설치커맨드) | 온브랜드(Claude가 유일 확인 소비자); SEO ROI는 약함 | S | Med |
| **P3** | hreflang ko/en/x-default + KO 롱테일(딥리뷰/arxiv 한글) | KR 보조 + 번역남용 회피; 깊이=권위 신호 | M | Med |
| **P3** | 한국 Naver Blog 구조화 포스트(AI 브리핑 인용용) | Naver AI 표면 포착(블로그 SERP 안 싸우고) | M | Med |
| **P3** | og:image/twitter:image 추가·아이콘 압축 | 소셜/AI 프리뷰 카드; CWV 위생 | S | Med |
| **P3** | G2/Capterra 프로필, 데모 유튜브 영상 | 리뷰플랫폼·유튜브는 AI 인용 채널(상승세) | S–M | Low–Med |
| **P3** | schema.org(SoftwareApplication 등) | 기계 파싱 도움(근거는 mixed) | M | Low–Med |

---

## 9. 신뢰도/불확실성 (정직하게)

- **GEO 정밀 통계 대부분은 신뢰 불가**(콘텐츠팜 r=0.87, "+156%" 류 폐기). 신뢰 보존: Ahrefs(AI Overview 인용 37.1% top10 / 26.2% 11–100 / 36.7% 100위 밖), Seer(ChatGPT 인용 87% Bing 겹침), Wikidata 정책, 봇 용도. "Perplexity 3-layer", "Reddit 24%", "리뷰플랫폼 3x" 등은 **방향성(MEDIUM–LOW)**.
- **schema·llms.txt는 직접 근거 약함** — 싼 보험이지 결정 레버 아님(표에 그렇게 반영).
- **MCP-인용 효과 크기는 미입증** — 메커니즘(레지스트리=신뢰 GitHub 코퍼스, 직접 호출=추천)은 견고하나 수치화 불가.
- **딥리뷰 출력 품질 미감사** — 기둥 B의 load-bearing 가정. 공개 발행 전 품질 감사 필수.
- **리트리벌 선호는 빠르게 변함**(Reddit 점유 한 달 23% 이동) → GEO는 set-and-forget 아닌 지속 측정·조정.
- **Naver C-Rank/D.I.A. 가중치·"AI 브리핑 인용수"·AI 탭** = 커뮤니티 역공학/단일출처/미문서화 → 방향성으로만.

---

## 10. 한 문단 결론

기반(봇 prerendering으로 — **사람 UI/UX는 그대로 둔 채** — AI에게 보이게)을 트랙1으로 깔되, **비용 거의 0의 MCP 유통 플라이휠(오픈소스화 → 공식 레지스트리 → awesome/디렉터리 → README/docstring)을 트랙2로 지금 즉시 병행**하라. 집현전의 권위 해자는 "에이전트가 직접 호출하는 유일한 *연구 워크플로우* MCP(6/7)"이고, 이는 순수 SEO 경쟁사가 구조적으로 복제 못 한다. 딥리뷰 코퍼스를 색인 자산으로 키우고, 엔티티/Wikidata/비교콘텐츠로 "AI가 인용하는 출처" 지위를 굳히며, 고정 쿼리셋 SoV로 권위를 측정-조정한다. 단, **원격 MCP 전송·개인정보처리방침·리뷰 품질 감사** 세 블로커는 오너 결정이 선행돼야 플라이휠의 30%와 코퍼스 발행이 열린다.
