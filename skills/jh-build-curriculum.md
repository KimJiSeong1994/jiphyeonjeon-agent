---
name: jh-build-curriculum
description: 주제와 난이도를 받아 집현전에서 학습 커리큘럼을 생성한다. 트리거 키워드 — "커리큘럼", "study plan", "학습 경로", "study roadmap".
---

# /jh:build-curriculum

## 실행 순서

1. **요구사항 수집**
   주어지지 않은 경우 사용자에게 묻는다:
   - 주제 (예: "GraphRAG", "diffusion model for audio")
   - 난이도: `beginner | intermediate | advanced`
   - 분량: 2-15 주/모듈 (기본 4)

2. **시드 논문 찾기 (선택, 더 좋은 커리큘럼을 위해)**
   - `search_papers({query: 주제, limit: 10})` 호출해 핵심 논문 후보 3-5편 선별.
   - 사용자에게 "이 논문들을 시드로 써도 될까요?" 확인.

3. **커리큘럼 생성**
   - `create_curriculum({topic, difficulty, num_modules})` 호출.
   - 30-90초 소요 — 사용자에게 예상 시간 안내.

4. **결과 표시**
   - 모듈별로 제목/목표/추천 논문/체크포인트를 표로 제시.
   - 사용자가 저장/수정/포크를 원하면 집현전 웹 UI (`/curricula/<id>`) 링크 안내.

## 실패 처리
- 타임아웃: "커리큘럼 생성이 60초 넘게 걸립니다. 집현전 서버에서 진행 중일 수 있으니 웹 UI 에서 확인해주세요."
- 401: 재인증 안내.
