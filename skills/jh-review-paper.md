---
name: jh-review-paper
description: 집현전으로 논문을 딥리뷰한다. arxiv URL/ID 또는 검색어를 주면 search → start_review → 폴링 → 리뷰 표시까지 한 흐름으로 처리. 트리거 키워드 — "딥리뷰", "deep review", "리뷰해줘", "review this paper".
---

# /jh:review-paper

집현전 MCP 서버를 이용한 논문 딥리뷰 플로우.

## 사전 조건
- `jiphyeonjeon` MCP 서버가 Claude Code에 등록돼 있어야 한다.
- `JIPHYEONJEON_TOKEN` 이 유효해야 한다 (24h 만료 시 재발급 안내).

## 실행 순서

1. **입력 파싱**
   - 사용자가 arxiv URL (`https://arxiv.org/abs/...`) 이나 ID (`2403.xxxxx`)를 준 경우 → 단계 3으로.
   - 자연어 검색어만 준 경우 → 단계 2.

2. **검색 (필요 시)**
   - `search_papers({query, limit: 5-10})` 호출.
   - 인용 수, 최신성, 관련도를 기준으로 상위 1-3편을 사용자에게 제시.
   - 사용자 선택을 기다린다 (자동 선택 금지 — 엉뚱한 논문 리뷰 방지).

3. **리뷰 시작**
   - `start_review({paper_ids: [선택 id], query: 사용자 원래 질문, fast_mode: false})` 호출.
   - 반환된 `session_id`, 예상 시간을 사용자에게 안내.
   - 사용자에게 질문: "지금 기다리시겠어요, 아니면 다른 작업 진행 후 이어갈까요?"

4. **폴링 (기다리기 선택 시)**
   - `get_review_status({session_id})` 를 exponential backoff 로 호출: 15s → 30s → 60s → 90s (상한).
   - 각 폴링 결과의 `stage` / `progress` 를 사용자에게 한 문장씩 전달 ("방법론 분석 중 60%..." 식).
   - `status == "completed"` 또는 `"failed"` 까지 반복.
   - 총 소요 시간 상한 10분. 초과 시 사용자에게 "아직 진행 중, 나중에 세션 id XXX 로 다시 확인하세요" 안내.

5. **리뷰 표시**
   - 완료되면 응답의 `report` / `report_markdown` 을 TL;DR (3-5 bullet) + 핵심 섹션으로 요약.
   - 전체 마크다운은 너무 길면 길이 제한 후 "전체 보기: /api/deep-review/report/{session_id}" 링크 제공.

## 실패 처리
- `status == "failed"`: reason 을 그대로 보여주고 재시도 제안 (fast_mode 로 전환 가능).
- 401 인증 실패: JWT 갱신 방법을 안내 (`POST /api/auth/login` 예시).
- 429: Retry-After 만큼 대기 후 한 번만 재시도.

## 북마크 제안
리뷰 성공 후 사용자에게 "이 논문 북마크 해둘까요?" 묻고, 동의 시 `add_bookmark({paper_id, topic})` 호출.
