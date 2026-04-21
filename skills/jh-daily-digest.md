---
name: jh-daily-digest
description: 내 북마크와 관심 주제 기반 일일 논문 브리핑을 만든다. 트리거 키워드 — "오늘 논문", "digest", "브리핑", "daily update".
---

# /jh:daily-digest

## 실행 순서

1. **최근 북마크 확인**
   - `list_bookmarks()` 호출, `created_at` 기준 상위 5-10 개 추출.
   - 각 북마크의 `topic` 필드로 사용자 관심사를 파악.

2. **주제별 신규 논문 검색**
   - 각 고유 `topic` 에 대해 `search_papers({query: topic, limit: 5, year_from: 올해})` 호출.
   - 이미 북마크된 paper_id 는 중복 제거.

3. **요약 제시**
   - 주제별로 2-3문장 TL;DR + 가장 주목할 논문 1편 제시.
   - 사용자가 "이 논문 리뷰해줘" 라 하면 `/jh:review-paper` 흐름으로 연결.
   - "북마크 해둬" 라 하면 `add_bookmark` 호출.

## 빈 북마크 처리
북마크가 0개이면: "아직 북마크가 없네요. 어떤 주제에 관심 있으세요?" 로 search_papers 플로우로 전환.
