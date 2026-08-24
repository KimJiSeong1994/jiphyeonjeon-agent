# Test Spec — 1K Papers 기업별 논문 블로그 시리즈

## 1. 검증 목표

저장소 내 준비 파이프라인이 정확히 3개 회사, 회사별 인덱스 1편과 논문 리뷰 3편을 근거 기반으로 만들었는지 검증한다. 검증은 로컬 산출물과 기존 citability 규칙만 다루며 HTTP, PaperWiki, 집현전 블로그 mutation을 수행하지 않는다.

## 2. 검증 대상

- `artifacts/1kpapers-company-series/`
- `scripts/validate_1kpapers_company_series.py`
- `tests/unit/test_1kpapers_company_series_artifacts.py`
- 기존 회귀 계약: `src/jiphyeonjeon_mcp/tools/blog.py`, `tests/unit/test_tools_contract.py`

## 3. 자동 검증 계약

### A. 파일 구조와 수량

- 허용 회사 디렉터리가 다음 세 개와 정확히 일치한다.
  - `01-google-deepmind`
  - `02-anthropic`
  - `03-openai`
- 회사별 `index.md` 1개와 `paper-01.md`~`paper-03.md` 3개가 존재한다.
- 전체 Markdown 초안은 정확히 12개다.
- 회사별 evidence JSON은 정확히 3개, 전체 정확히 9개다.
- `source-inventory.json`, `editorial-map.json`, `approval-manifest.json`과 다섯 개 보고서가 모두 존재한다.
- `src/`, backend/UI/API/DB 파일은 이 작업의 변경 목록에 없어야 한다.

### B. 소스 인벤토리와 선정

`source-inventory.json`에 대해 다음을 검사한다.

- 모든 후보가 `candidate_id`, title, stable ID, primary URL, company, retrieval timestamp를 가진다.
- `retrieved_at`은 timezone을 포함한 ISO-8601 형식이다.
- 모든 선정 후보에 1K Papers discovery URL과 최소 하나의 primary/authoritative source URL이 있다.
- 모든 선정 후보의 `company_attribution_status`는 `verified`다.
- 회사별 `selected=true`가 정확히 3개다.
- 안정 식별자 또는 귀속이 모호한 항목은 선정되지 않는다.
- `stable_id_type + stable_id` 중복이 없다.
- 공동 연구 항목은 canonical company가 하나이고 cross-company affiliation이 명시된다.
- selection score 총점과 breakdown의 가중치 합이 일치한다.

### C. 편집 지도와 taxonomy

`editorial-map.json`에 대해 다음을 검사한다.

- `series_id == "1kpapers-company-series-2026-pilot"`.
- 회사 배열의 값과 순서가 PRD와 일치한다.
- 각 회사에 `company_index` 1개와 `paper_review` 3개가 있다.
- 모든 항목의 `entry_id`, local path, proposed slug, title, order, tags, links가 유일하고 유효하다.
- 모든 항목에 공통 태그 `1kpapers-company-series`, `company-research`, `paper-review`가 있다.
- 회사 태그는 해당 회사의 태그 하나만 포함한다.
- 인덱스는 `company-index` 태그가 있고 자기 회사 리뷰 3개에 모두 링크한다.
- 각 리뷰는 자기 회사 인덱스와 나머지 두 리뷰에 링크한다.
- 모든 relative Markdown link target이 실제 파일로 해석된다.
- 공동 연구 cross-link가 있으면 canonical review target으로 해석된다.

### D. 증거 무결성

9개 evidence JSON 각각에 대해 다음을 검사한다.

- title, authors, year, version/date, venue 또는 arXiv ID, primary URL이 존재하거나 unavailable 사유가 명시된다.
- `evidence_ledger`, `method_map`, `result_table`, `critique_log`, `apa_references`가 존재한다.
- 주요 claim과 모든 수치에 claim ID, final draft section, exact claim text, 비어 있지 않은 source anchor가 있다.
- 각 exact claim text는 지정된 Markdown 본문에 그대로 존재하고, 본문의 모든 수치 문장은 evidence ledger 또는 result table의 exact text와 일치한다.
- evidence type은 `paper-reported`, `official-artifact`, `user-provided`, `direct-inference` 중 하나다.
- critique label은 `paper-evidenced`, `direct inference from setup`, `speculative` 중 하나다.
- speculative critique의 action은 최종 본문 포함이 아니다.
- DOI, venue, arXiv version, code URL이 없으면 값을 발명하지 않고 unavailable로 남긴다.
- 각 evidence bundle의 stable paper ID가 source inventory와 editorial map의 선택 항목과 정확히 일치한다.

### E. 초안 구조와 APA

리뷰 9편 각각에 대해 다음을 검사한다.

- 제목과 본문이 비어 있지 않고 한국어 설명을 포함한다.
- 첫 유효 문단에 굵게 표시된 대상 엔티티가 있다.
- `TL;DR`과 `## References`가 있다.
- APA reference가 최소 논문 자체 1개를 포함하고 arXiv 항목에는 ID와 URL이 있다.
- raw `원문`/`출처` 레이블, placeholder, TODO, `리뷰어 추가 비판` 독립 섹션이 없다.
- 표에 사용된 headline 수치는 인접 산문에도 동일하게 존재한다.
- 그림이 있으면 caption에 copied/adapted/reconstructed/original 중 하나와 출처가 있다.
- 본문의 major claim/number가 evidence bundle의 claim 또는 result 항목으로 역추적된다.

인덱스 3편 각각에 대해 다음을 검사한다.

- 회사 연구 흐름과 논문 선정 기준을 설명한다.
- 정확히 3개 리뷰 링크를 포함한다.
- 각 리뷰의 역할과 시리즈 읽기 순서를 설명한다.
- `TL;DR`, `## References`, 회사 귀속/선정 근거가 있다.

### F. 로컬 blog citability preflight

- validator는 `src/jiphyeonjeon_mcp/tools/blog.py`의 기존 citability 판정을 재사용한다.
- 12개 초안을 `category="paper-review"`로 검사한다.
- 각 초안의 결과는 `ready=true`, warnings 빈 배열이어야 한다.
- `allow_citability_warnings` 우회에 해당하는 상태나 플래그를 산출물에 허용하지 않는다.
- 이 검사는 함수 수준 로컬 검증이며 HTTP client, JWT, MCP remote connector를 사용하지 않는다.

### G. 승인·게시 안전성

`approval-manifest.json`에 대해 다음을 검사한다.

- 항목 수가 정확히 12개이고 editorial map과 일대일 대응한다.
- 모든 항목의 `user_approved == false`, `published == false`.
- 모든 항목의 `paperwiki.status == "blocked_unavailable"`, URL은 null.
- 모든 항목의 `blog.status == "not_attempted"`, id와 URL은 null.
- 전역 `publication_gate == "blocked_paperwiki_unavailable"`.
- manifest에 경고 override 또는 publication bypass가 없다.
- 원격 mutation 결과로 오해할 수 있는 post ID, live URL, published timestamp가 없다.

### H. 독립 검토와 피드백 반영

- `reports/code-review.json`에 독립 `code-reviewer` 증거와 `recommendation == "APPROVE"`가 있다.
- `reports/architecture-invariant-audit.json`에 독립 `architect` 증거와 `status == "CLEAR"`가 있다.
- 아키텍처 감사는 다음 불변조건 각각에 implementation, test, review evidence를 연결한다.
  - 정확히 세 회사.
  - 회사별 정확히 인덱스 1 + 리뷰 3.
  - 근거 기반 회사 귀속과 안정 식별자.
  - 백엔드/UI/API 변경 없음.
  - PaperWiki-first 및 no-publication.
- `critical-review.md`에 skeptical critic, verifier, revision owner의 분리된 결과가 있다.
- 모든 finding은 label, severity, action, reason, target, status를 가진다.
- blocking finding은 0개다.
- accepted/softened feedback은 해당 초안/evidence 수정과 재검증 증거를 가진다.
- rejected feedback은 근거 없는 주장 추가, 중복, 범위 이탈 등 명시적 사유가 있다.

### I. 최종 검증 보고서

`verification-report.md`는 다음을 기록한다.

- 검증 실행 시각과 명령.
- 파일 수와 회사/리뷰 선정 수.
- preflight 12/12 통과.
- evidence/APA/cross-link 검증 결과.
- 독립 review 상태와 피드백 반영 후 재실행 결과.
- PaperWiki 단계 `blocked_unavailable`, blog 단계 `not_attempted`.
- 원격 mutation 0회.

## 4. 테스트 구현 요구

### `scripts/validate_1kpapers_company_series.py`

- Python 3.12 표준 라이브러리와 현재 프로젝트 의존성만 사용한다.
- `--root`와 `--report` 인자를 받고 성공 시 0, 계약 위반 시 non-zero를 반환한다.
- JSON parse/schema, 파일 수, link resolution, taxonomy, evidence, APA/References, approval state를 검사한다.
- preflight는 기존 blog citability 구현을 호출하되 네트워크 client를 만들지 않는다.
- 결과는 결정론적인 JSON으로 `reports/preflight-report.json`에 기록한다.
- 원격 connector, JWT, `create_blog_draft`, `update_blog_draft`는 호출하지 않는다.

### `tests/unit/test_1kpapers_company_series_artifacts.py`

- validator 성공 경로를 검증한다.
- 잘못된 회사 수, 네 번째 리뷰, 누락 evidence, 중복 stable ID, broken link, APA 누락, preflight warning, published=true를 각각 실패시키는 negative test를 둔다.
- fixture는 임시 디렉터리에서 수행하고 실제 산출물을 훼손하지 않는다.

## 5. 검증 명령

구현 후 아래 순서로 실행한다.

```bash
uv run python scripts/validate_1kpapers_company_series.py \
  --root artifacts/1kpapers-company-series \
  --report artifacts/1kpapers-company-series/reports/preflight-report.json

uv run pytest tests/unit/test_1kpapers_company_series_artifacts.py -q
uv run pytest tests/unit/test_tools_contract.py -q
uv run ruff check scripts/validate_1kpapers_company_series.py \
  tests/unit/test_1kpapers_company_series_artifacts.py
uv run mypy scripts/validate_1kpapers_company_series.py
uv run pytest -q
```

피드백 반영 뒤 첫 두 명령과 전체 `pytest -q`를 다시 실행하고 `verification-report.md`에 두 번째 실행 증거를 기록한다.

## 6. 수동·독립 검토 시나리오

### 시나리오 1 — 귀속 오판

현재 저자 소속만 있고 출판 시점 affiliation 또는 공식 회사 연구 페이지가 없는 후보를 넣는다. 기대 결과는 미선정과 명시적 exclusion reason이다.

### 시나리오 2 — 공동 연구 중복

같은 stable ID를 두 회사 리뷰로 배치한다. 기대 결과는 validator 실패다. 한 회사 canonical placement와 다른 인덱스의 cross-link로 바꾸면 통과해야 한다.

### 시나리오 3 — 근거 없는 수치

본문에 evidence result table에 없는 수치를 추가한다. verifier와 자동 trace 검사 모두 실패해야 한다.

### 시나리오 4 — preflight 우회

정의 리드 또는 TL;DR을 제거하거나 warning override를 추가한다. 기대 결과는 실패이며 override로 통과할 수 없다.

### 시나리오 5 — 게시 상태 오염

manifest에 PaperWiki/blog URL, post ID, `published=true` 중 하나를 넣는다. 기대 결과는 실패다.

### 시나리오 6 — PaperWiki 없이 블로그 진행

blog 상태를 `draft_created`로 바꾸고 PaperWiki 상태를 `blocked_unavailable`로 둔다. 기대 결과는 PaperWiki-first 위반 실패다.

### 시나리오 7 — 비판 피드백 반영 누락

accepted finding을 반영 증거 없이 closed 처리한다. 기대 결과는 review gate 실패다.

## 7. 통과 기준

- 모든 자동 검증 명령이 성공한다.
- 정확히 12개 초안과 9개 증거 번들이 검증된다.
- preflight는 12/12 ready이고 warning override는 0개다.
- source attribution, stable ID, APA, claim traceability, cross-link 검사가 모두 통과한다.
- code-reviewer는 APPROVE, architect는 CLEAR, blocking critical finding은 0개다.
- accepted feedback 반영 뒤 재검증이 성공한다.
- 원격 mutation은 0회이고 PaperWiki/blog 게시 단계는 시작되지 않는다.

## 8. 실패·중단 규칙

다음 중 하나라도 발생하면 완료로 표시하지 않는다.

- 한 회사에서 귀속과 1차 증거가 검증된 논문 3편을 확보하지 못함.
- 안정 식별자 중복 또는 unresolved attribution이 선정 목록에 남음.
- APA/claim trace/preflight/link 검증 실패.
- 독립 review 증거 부재, REQUEST CHANGES/BLOCK, architect non-CLEAR.
- accepted feedback 미반영.
- 원격 mutation 또는 PaperWiki-first 우회 흔적.

이 경우 게시 시도 대신 blocker를 `verification-report.md`와 `approval-manifest.json`에 기록하고, 근거/초안/검증 문제를 해소한 뒤 같은 테스트를 재실행한다.
