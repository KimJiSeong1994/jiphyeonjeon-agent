# PRD — 1K Papers 기업별 논문 블로그 시리즈 준비 파이프라인

## 1. 목표와 완료 결과

1K Papers를 발견·랭킹 근거로 사용해 Google DeepMind, Anthropic, OpenAI의 연구 흐름을 설명하는 집현전 블로그 파일럿을 준비한다. 완료 결과는 **회사별 인덱스 1편과 논문 심층 리뷰 3편**, 총 12편의 로컬 초안과 이를 뒷받침하는 출처·증거·승인·검증 산출물이다.

이번 실행은 게시가 아니라 게시 준비까지다. 현재 Codex App 표면에는 PaperWiki 게시 커넥터와 집현전 블로그 MCP 커넥터가 없으므로 다음 경계를 지킨다.

- 로컬 초안, 증거 번들, 승인 매니페스트, 사전 검증 보고서는 생성한다.
- PaperWiki 게시를 시도하지 않는다.
- PaperWiki-first 게이트를 우회해 블로그 초안을 만들거나 게시하지 않는다.
- 백엔드, UI, API, 데이터 모델, 공개 라우트는 변경하지 않는다.

## 2. 요구사항 출처와 현재 근거

### 요구사항 소스

- `.omx/specs/deep-interview-1kpapers-company-series.md`
- `.omx/context/1kpapers-company-series-20260823T092635Z.md`
- `.omx/interviews/1kpapers-company-series-20260823T094829Z.md`
- `/Users/jiseong/.codex/skills/jh-paper-review-blog/SKILL.md`
- `/Users/jiseong/.codex/skills/jh-paper-review-blog/references/team-protocol.md`
- `/Users/jiseong/.codex/skills/jh-paper-review-blog/references/format-template.md`
- `/Users/jiseong/.codex/skills/jh-paper-review-blog/references/review-rubric.md`

### 저장소 근거

- `src/jiphyeonjeon_mcp/tools/blog.py`는 `check_blog_draft`, `create_blog_draft`, `update_blog_draft` 계약을 제공한다.
- 생성/수정 도구는 `published=false`를 강제하지만 실제 사용에는 원격 MCP 연결과 관리자 권한이 필요하다.
- `paper-review` 사전 검증은 엔티티 중심 정의 리드와 `TL;DR`을 요구하며, 경고 우회는 명시적 승인 없이는 허용되지 않는다.
- 현재 계약에는 회사/시리즈 전용 엔티티나 카테고리가 없다.
- JH 논문 리뷰 규칙은 새 리뷰를 PaperWiki에 먼저 게시·검토한 뒤 그 버전을 블로그의 소스로 사용하도록 요구한다. PaperWiki 게시가 불가능하면 블로그 게시 전에 중단해야 한다.

### 외부 소스 사용 원칙

- 시작점: `https://www.1kpapers.com/most-trending-papers`
- 회사별 후보 보강: 1K Papers의 Google DeepMind, Anthropic, OpenAI lab catalog.
- 1K Papers는 발견·트렌드 근거일 뿐 기술 주장이나 회사 귀속의 단독 근거가 아니다.
- 논문 PDF/arXiv, 공식 프로젝트·코드, 저자/회사 연구 페이지를 우선 근거로 사용한다.
- 페이지 전문을 복제하지 않고 URL, 검색 시각, 최소 메타데이터와 요약된 근거만 보존한다.

## 3. 범위

### 포함

1. 1K Papers와 1차 자료의 후보·출처 인벤토리 작성.
2. 회사 귀속과 논문 식별자 검증, 중복·공동 연구 처리.
3. 세 회사 각각 정확히 3편을 선정하는 편집 지도 작성.
4. 세 회사 각각 인덱스 1편과 논문 리뷰 3편 작성.
5. 논문별 증거 원장, 방법 지도, 결과 표, 비판 로그, APA 참고문헌 준비.
6. 일관된 분류·제목·슬러그·태그·순서·상호 링크 적용.
7. 로컬 사전 검증, 독립 코드리뷰, 아키텍처 불변조건 감사, 비판적 에이전트 검토와 피드백 반영.
8. 사용자 승인 매니페스트와 제안 게시 순서 작성.

### 제외

- PaperWiki 또는 집현전 블로그에 대한 원격 생성·수정·게시.
- `create_blog_draft`, `update_blog_draft` 호출.
- 백엔드/프런트엔드/API/DB/인증/라우트 변경.
- 회사 시리즈 도메인 모델, 신규 카테고리, 자동 수집·동기화·스케줄러.
- 세 회사 이외의 파일럿 확장.
- 회사당 4편 이상 작성.
- 인용 메타데이터, 수치, 귀속 근거의 추정 또는 경고 우회.

## 4. 전달 옵션 비교와 결정

| 옵션 | 방식 | 장점 | 제약/위험 | 판정 |
| --- | --- | --- | --- | --- |
| A. 현재 원격 MCP 콘텐츠 직접 실행 | 조사 후 `check_blog_draft` → `create_blog_draft`로 비공개 블로그 초안을 즉시 생성 | 원격 ID/slug를 바로 확보하고 현재 draft-only 계약을 활용 | 현재 App 표면에 블로그 MCP/PaperWiki 게시 커넥터가 없음; PaperWiki-first를 충족하지 못함; 원격 변경과 권한 실패 가능; 근거·리뷰 산출물이 분산됨 | 기각 |
| B. 저장소 내 준비 산출물 파이프라인 | 출처·편집·증거·초안·승인·검증 파일을 먼저 만들고 로컬에서 검사 | 재현 가능, 검토 가능, 연결 불가 상태에서도 진행 가능, PaperWiki-first 중단점을 명시적으로 보존 | 실제 PaperWiki/블로그 ID와 공개 URL은 나중에만 확정 가능 | **채택** |

### 결정

옵션 B를 채택한다. 로컬 산출물은 게시 준비 상태까지만 만든다. PaperWiki 커넥터가 제공되는 후속 실행에서 승인된 로컬 초안을 PaperWiki에 먼저 반영하고, PaperWiki 검토 완료 후에만 블로그 단계로 넘어갈 수 있다.

## 5. 결정 기록

### RALPLAN-DR

**Principles**

1. 근거 무결성이 초안 수량보다 우선한다.
2. 새 제품 엔티티 없이 콘텐츠 관례로 파일럿을 완성한다.
3. 게시 단계와 준비 단계를 분리하고 PaperWiki-first를 우회하지 않는다.
4. 모든 주요 주장·수치·비판은 추적 가능해야 한다.
5. 독립 검토와 재검증을 통과하기 전 완료로 간주하지 않는다.

**Top drivers**

1. 현재 App 표면에 PaperWiki/블로그 게시 커넥터가 없다는 실행 제약.
2. 정확히 3개 회사 × (인덱스 1 + 리뷰 3)의 고정된 파일럿 범위.
3. 회사 귀속·APA 참고문헌·GEO 인용 가능성에 대한 높은 검증 요구.

**Options**

- 원격 MCP 콘텐츠 직접 실행: 연결성과 PaperWiki-first 조건 때문에 현재 실행 불가.
- 저장소 내 준비 산출물 파이프라인: 현재 조건에서 완결 가능하며 후속 게시의 입력으로 재사용 가능.

### ADR

- **Decision:** 저장소 내 준비 산출물 파이프라인을 구현하고 원격 게시 동작은 수행하지 않는다.
- **Drivers:** 커넥터 부재, PaperWiki-first 게이트, 재현 가능한 검토 패키지 필요.
- **Alternatives considered:** 원격 MCP 비공개 초안 직접 생성, 새 회사 시리즈 모델/API 도입.
- **Why chosen:** 사용자 의도인 콘텐츠 파일럿을 보존하면서 현재 표면에서 안전하고 검증 가능한 최대 범위를 완성한다.
- **Consequences:** 로컬 링크와 제안 slug는 확정할 수 있지만 PaperWiki/blog ID·URL은 비어 있어야 한다. 실제 게시에는 별도 승인과 연결된 후속 실행이 필요하다.
- **Follow-ups:** PaperWiki 연결이 생기면 승인 매니페스트를 입력으로 PaperWiki 반영 → 검토 → 블로그 사전 검증/비공개 초안 생성 순서로 진행한다.

## 6. 고정 산출물 구조

구현은 아래 경로만 추가·수정한다. `src/`, 서버 계약, UI, API 파일은 건드리지 않는다.

```text
artifacts/1kpapers-company-series/
  README.md
  source-inventory.json
  editorial-map.json
  approval-manifest.json
  evidence/
    01-google-deepmind/paper-01.json
    01-google-deepmind/paper-02.json
    01-google-deepmind/paper-03.json
    02-anthropic/paper-01.json
    02-anthropic/paper-02.json
    02-anthropic/paper-03.json
    03-openai/paper-01.json
    03-openai/paper-02.json
    03-openai/paper-03.json
  drafts/
    01-google-deepmind/index.md
    01-google-deepmind/paper-01.md
    01-google-deepmind/paper-02.md
    01-google-deepmind/paper-03.md
    02-anthropic/index.md
    02-anthropic/paper-01.md
    02-anthropic/paper-02.md
    02-anthropic/paper-03.md
    03-openai/index.md
    03-openai/paper-01.md
    03-openai/paper-02.md
    03-openai/paper-03.md
  reports/
    preflight-report.json
    code-review.json
    architecture-invariant-audit.json
    critical-review.md
    verification-report.md
scripts/validate_1kpapers_company_series.py
tests/unit/test_1kpapers_company_series_artifacts.py
```

## 7. 산출물 계약

### 7.1 `source-inventory.json`

각 후보는 최소 다음 필드를 가진다.

- `candidate_id`, `title`, `stable_id_type`, `stable_id`, `primary_url`
- `company`, `company_attribution_status`, `company_attribution_rationale`, `company_attribution_sources`
- `discovery_sources`, `retrieved_at`, `trend_evidence`
- `selection_score`와 `score_breakdown`
- `selected`, `canonical_company`, `cross_company_affiliations`, `duplicate_of`
- `evidence_availability`, `exclusion_reason`

최종 선정 항목은 회사별 정확히 3개다. 식별자 또는 귀속이 모호한 후보는 선정하지 않는다. 공동 연구는 하나의 canonical company에만 리뷰를 배치하고 다른 회사 인덱스에서 상호 참조한다.

### 7.2 `editorial-map.json`

- `series_id`: `1kpapers-company-series-2026-pilot`
- 회사 순서: `01-google-deepmind`, `02-anthropic`, `03-openai`
- 회사별 정확히 `index` 1개와 `paper_review` 3개.
- 선택 점수 가중치: trend 25, recency 15, significance 25, thematic coherence 20, primary-evidence availability 15.
- 각 항목에 `entry_id`, `company`, `entry_kind`, `local_path`, `proposed_slug`, `title`, `order`, `tags`, `links_to`를 기록한다.

### 7.3 분류와 링크 규칙

- 공통 태그: `1kpapers-company-series`, `company-research`, `paper-review`.
- 회사 태그: `google-deepmind`, `anthropic`, `openai` 중 정확히 하나.
- 인덱스 추가 태그: `company-index`.
- 리뷰 추가 태그: 논문별 주제 태그 1개 이상.
- 인덱스 제목: `{Company} 연구 흐름: 1K Papers에서 고른 세 편의 논문`.
- 리뷰 제목: `{Paper title}: {evidence-grounded Korean angle}`.
- 로컬 상태에서는 상대 Markdown 링크만 사용하며 모두 실제 파일로 해석되어야 한다.
- 제안 blog slug는 매니페스트에 기록하되 PaperWiki/blog URL로 가장하지 않는다.
- 회사 인덱스는 자기 회사 리뷰 3개에 모두 링크한다. 각 리뷰는 자기 회사 인덱스와 같은 회사의 나머지 리뷰 2개에 링크한다.

### 7.4 논문별 증거 번들

9개 JSON은 JH 팀 프로토콜의 다음 구조를 포함한다.

- paper metadata와 정확한 버전/날짜/저자/venue 또는 arXiv ID.
- `evidence_ledger`: claim ID, final draft section, exact claim text, source anchor, evidence type, confidence, notes. `exact_claim_text`는 해당 Markdown 본문에 그대로 존재해야 한다.
- `method_map`: component/step, role, input/output, assumption, source anchor.
- `result_table`: result claim, setup, exact value, comparator, source anchor, caveat.
- `critique_log`: critique, label, action, reason, final prose location.
- `apa_references`: 이용 가능한 메타데이터까지만 채운 APA 항목.

증거가 없는 수치·주장·DOI·venue·코드 URL은 추가하지 않는다. speculative 비판은 최종 본문에 넣지 않는다. 주요 주장과 수치는 evidence ledger/result table의 정확한 본문 문장으로 연결해 자동 trace 검증이 가능해야 한다.

### 7.5 초안

- 한국어를 기본으로 하고 표준 기술 용어는 필요할 때 영어를 유지한다.
- 리뷰 9편은 논문 유형에 맞게 deep academic review 또는 축약 모드를 명시한다.
- 모든 리뷰는 엔티티 중심 정의 리드, Executive Summary 또는 명시적 축약 사유, 자기완결 `TL;DR`, `## References`, APA 참고문헌을 갖는다.
- 표의 핵심 수치는 인접 산문에도 동일하게 기재한다.
- 논문 한계를 저자 보고, 설정에서의 직접 추론, speculation으로 구분한다.
- 기본 `리뷰어 추가 비판` 독립 섹션을 만들지 않는다.
- 라이선스가 확인되지 않은 원본 그림은 재사용하지 않는다. 그림이 필요하면 original/reconstructed/adapted 상태와 출처를 캡션에 표시한다.
- 회사 인덱스도 `category=paper-review` 준비 관례를 따르되 `entry_kind=company-index`로 구분한다. 신규 카테고리는 만들지 않는다.

### 7.6 `approval-manifest.json`

총 12개 항목 각각에 다음을 기록한다.

- local path, proposed slug, company, entry kind, paper ID(인덱스는 null), proposed order.
- evidence status, local preflight status/warnings, independent review status, revision status.
- `paperwiki.status = "blocked_unavailable"`, `paperwiki.url = null`.
- `blog.status = "not_attempted"`, `blog.id = null`, `blog.url = null`, `published = false`.
- `user_approved = false`.

전역 게이트는 `publication_gate = "blocked_paperwiki_unavailable"`로 끝나야 한다. 이는 실패가 아니라 이번 실행의 의도된 정지 상태다.

## 8. 실행 계획

1. **소스 인벤토리 고정**
   - 1K Papers trending과 세 lab catalog에서 후보를 수집하고 검색 시각을 기록한다.
   - arXiv/PDF와 공식 회사 페이지로 식별자·귀속을 검증한다.
   - 후보가 부족하면 관련 1차 자료를 추가하되 1K Papers 발견 경로와 분리해 기록한다.

2. **선정과 편집 지도 작성**
   - 점수 기준과 증거 가용성으로 회사별 정확히 3편을 선정한다.
   - 중복·공동 연구 canonical placement를 확정한다.
   - 고정 taxonomy, 제목, slug, 순서, 로컬 cross-link graph를 작성한다.

3. **독립 근거 분석**
   - evidence analyst가 9개 evidence ledger/result table을 작성한다.
   - method architect가 9개 method map과 설명 순서를 검증한다.
   - context researcher가 비교 축과 1차 참고문헌을 보강한다.

4. **초안 작성**
   - writer가 편집 지도와 증거 번들만을 근거로 3개 인덱스와 9개 리뷰를 작성한다.
   - 링크와 APA 참고문헌을 적용한다.

5. **로컬 사전 검증**
   - validator와 unit test를 추가해 파일 수, JSON 스키마, 선정 수, 귀속, taxonomy, 링크, APA/References, 로컬 citability preflight를 검사한다.
   - `src/jiphyeonjeon_mcp/tools/blog.py`의 기존 citability 판정을 재사용하고 HTTP 호출은 하지 않는다.

6. **독립 리뷰와 비판적 검토**
   - code-reviewer가 산출물/validator/test의 정확성과 회귀 위험을 검토한다.
   - architect가 고정 불변조건을 독립적으로 감사한다.
   - skeptical critic과 verifier가 과장, cherry-picking, 숫자·인용·제목·링크를 검토한다.
   - revision owner가 수용/완화/거절 결정을 `critical-review.md`에 기록하고 피드백을 반영한다.

7. **재검증과 승인 패키지 확정**
   - 피드백 반영 뒤 전체 로컬 검증을 다시 실행한다.
   - `approval-manifest.json`과 `verification-report.md`를 최신 결과로 고정한다.
   - PaperWiki 미연결 상태를 기록하고 게시 전에 중단한다.

## 9. 독립 리뷰 책임 분리

| lane | 책임 | 필수 증거 |
| --- | --- | --- |
| Evidence analyst | 메타데이터·주장·수치·한계 추출 | 9개 evidence bundle |
| Method architect | 방법 구조·가정·설명 순서 재구성 | 9개 method map |
| Context researcher | 비교축과 1차 자료 확인 | source inventory와 APA entries |
| Writer | 근거 기반 초안 작성 | 12개 draft |
| Skeptical critic | 과장·대표성·공정성·재현성 공격 검토 | critical review findings |
| Verifier | 숫자·명칭·인용·링크·섹션 검증 | verification note |
| Revision owner | 피드백 수용/완화/거절 및 반영 | critique log와 revision status |
| Code reviewer | validator/test/산출물 계약 검토 | `code-review.json`의 APPROVE |
| Architect | 범위·PaperWiki-first·불변조건 독립 감사 | `architecture-invariant-audit.json`의 CLEAR |

작성자와 최종 code-reviewer/architect는 동일 lane으로 취급하지 않는다. 독립 검토 증거가 없으면 완료할 수 없다.

## 10. 수용 기준

1. `source-inventory.json`의 모든 선정 논문에 검색 시각, 1K Papers 발견 URL, 안정 식별자, 1차 자료 URL, 회사 귀속 근거가 있다.
2. 회사는 Google DeepMind, Anthropic, OpenAI 정확히 3개이며 다른 회사 시리즈가 없다.
3. 회사별 정확히 인덱스 1편과 리뷰 3편, 전체 정확히 12개 초안과 9개 증거 번들이 존재한다.
4. 한 논문은 하나의 canonical company에만 리뷰로 배치되며 공동 연구는 명시적으로 상호 참조된다.
5. 모든 주요 기술 주장과 수치가 evidence ledger의 source anchor로 추적된다.
6. 모든 리뷰에 `## References`와 가능한 범위의 APA 참고문헌이 있고 메타데이터를 조작하지 않는다.
7. taxonomy, 제목, slug, 순서, 태그, 상호 링크가 `editorial-map.json`과 일치하고 모든 로컬 링크가 해석된다.
8. 12개 초안 모두 로컬 preflight를 경고 우회 없이 통과한다.
9. code reviewer는 APPROVE, architect는 CLEAR, 비판적 검토의 blocking finding은 0이며 모든 accepted feedback이 반영·재검증된다.
10. 승인 매니페스트의 12개 항목은 `user_approved=false`, `published=false`; PaperWiki는 `blocked_unavailable`, blog는 `not_attempted`다.
11. `src/`, 백엔드/UI/API/DB 파일에는 변경이 없다.
12. `test-spec-1kpapers-company-series.md`의 명령이 모두 통과한다.

## 11. 위험과 대응

- **Trending 목록만으로 회사별 후보 부족:** lab catalog와 1차 자료로 후보를 보강하되 발견 경로를 분리 기록한다.
- **잘못된 회사 귀속:** 출판 시점 저자 affiliation 또는 공식 연구 페이지가 없으면 제외한다. 현재/후속 고용만으로 귀속하지 않는다.
- **공동 연구 중복:** canonical placement 1개와 cross-link만 허용한다.
- **근거 없는 장문 리뷰:** evidence bundle이 준비되지 않은 논문은 전체 리뷰를 쓰지 않는다.
- **APA 메타데이터 공백:** partial APA를 허용하되 추정하지 않는다.
- **로컬 링크와 향후 URL 불일치:** 로컬 relative link와 proposed slug를 분리하고 실제 PaperWiki URL은 후속 단계에서만 기록한다.
- **게시 게이트 우회:** connector 부재를 blocker로 명시하고 원격 mutation을 테스트에서 금지한다.
- **범위 팽창:** validator가 회사 수, 리뷰 수, 변경 경로를 고정한다.

## 12. 중단 조건과 후속 인계

다음이 모두 충족되면 이번 실행은 완료한다.

- 12개 초안, 9개 증거 번들, 인벤토리, 편집 지도, 승인 매니페스트, 리뷰/검증 보고서가 존재한다.
- 피드백 반영 후 로컬 검증이 모두 통과한다.
- 독립 code review가 APPROVE이고 architect audit이 CLEAR다.
- `publication_gate = "blocked_paperwiki_unavailable"`가 기록되어 있다.
- 원격 생성·수정·게시 시도가 없었다.

후속 게시 실행은 사용자가 승인하고 PaperWiki 커넥터가 사용 가능할 때만 시작한다. 순서는 승인된 로컬 초안 → PaperWiki draft 생성/검토 → PaperWiki 버전 기준 블로그 preflight → 비공개 blog draft 생성 → 별도 게시 승인이다.
