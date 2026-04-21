---
name: jh-explore
description: 특정 논문에서 관련 논문 그래프를 탐색한다. 인용 트리·유사 논문. 트리거 키워드 — "관련 논문", "citation tree", "more like this", "더 파보자", "탐색".
---

# /jh:explore

## 실행 순서

1. **앵커 선정**
   - 사용자가 북마크 id 를 주면 바로 사용.
   - 논문 제목/URL 만 준 경우: 먼저 `list_bookmarks` 에서 검색, 없으면 `search_papers` → 필요 시 `add_bookmark` 로 북마크 생성 후 그 id 사용.

2. **그래프 탐색**
   - `explore_related({bookmark_id, depth: 2, max_per_direction: 10})` 호출.
   - 반환 트리를 노드/엣지 목록으로 정리 (citing / cited-by / similar 구분).

3. **결과 정리 & 다음 액션 제안**
   - 상위 논문 5-10편을 제목+한 줄 요약으로 제시.
   - 각 항목 옆에 "[리뷰] [북마크] [다시 탐색]" 선택지 제공.
   - 사용자가 선택하면 해당 skill/tool 체이닝.

## 성능 고려
- 첫 호출은 집현전이 Semantic Scholar 로 크롤링 — 2-5 초 소요 안내.
- 같은 북마크 재탐색은 캐시에서 나와 즉시 응답.

## 실패 처리
- 북마크 없음: "먼저 북마크로 등록이 필요합니다. `add_bookmark` 로 등록할까요?"
- Semantic Scholar 429: "외부 그래프 API 한도 초과. 1-2분 뒤 다시 시도하세요."
