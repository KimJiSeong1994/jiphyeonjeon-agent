---
name: jh-draft-blog
description: 하나 이상의 논문을 바탕으로 블로그 초안을 작성한다. admin 권한 필요. 트리거 키워드 — "블로그 초안", "blog draft", "post draft", "블로그로 정리".
---

# /jh:draft-blog

## 사전 조건
- 집현전 admin 권한 (403 시 권한 안내).
- 대상 논문 1편 이상.

## 실행 순서

1. **입력 정리**
   - 주어진 논문이 없으면: 최근 북마크(`list_bookmarks`) 중 선택 or 새로 검색.
   - 스타일: `explainer` (기본) | `critical` | `digest`.
   - 로캘: `ko` (기본) | `en`.

2. **초안 작성**
   - Claude 가 자체적으로 마크다운 초안 작성 (제목 + 2-5 섹션).
   - 각 섹션: 해당 논문의 핵심을 사용자가 지정한 스타일로 요약.
   - 인용·그림 플레이스홀더 표시 — 서버가 자동 채우지 않음을 명시.

3. **사용자 확인 단계 (destructive-adjacent)**
   - 생성 전 반드시 초안을 사용자에게 보여주고 승인 구한다.
   - "게시(publish) 말고 draft 로만 저장합니다. 승인하시겠어요?"
   - 거절 시 저장하지 않고 종료.

4. **저장**
   - 승인 후 `create_blog_draft({title, content, tags, style})` 호출.
   - 반환된 post id / slug / 관리 URL 을 표시.

## 실패 처리
- 403: "admin 권한이 필요합니다. 관리자에게 권한 승격을 요청하세요."
- 422: 제목/본문 길이 등 검증 실패 사유 표시 후 재시도 요청.
