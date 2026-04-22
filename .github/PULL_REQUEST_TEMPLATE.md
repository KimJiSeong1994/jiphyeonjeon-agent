<!-- 감사합니다. 짧아도 좋으니 아래 항목을 채워 주세요. -->

## 요약

<!-- 무엇을 바꿨고 왜 바꿨는지 1-3 문장 -->

## 관련 이슈

Closes #

## 변경 유형

- [ ] 새 MCP tool 또는 기존 tool 시그니처 변경
- [ ] 새 Claude Code skill
- [ ] 버그 수정 (동작 변화 없음 보장)
- [ ] 문서만 수정
- [ ] 빌드 / CI / 의존성 업데이트
- [ ] 리팩터 (외부 동작 동일)

## 체크리스트

- [ ] `uv run pytest tests/unit -v` — 전 테스트 통과
- [ ] `uv run ruff check src tests` — lint 통과
- [ ] `uv run ruff format --check src tests` — format 통과
- [ ] `uv run mypy src` — strict 타입 통과
- [ ] 새 tool/파라미터 추가 시 `tests/unit/test_tools_contract.py` 에 계약 테스트 추가
- [ ] 사용자 가시적 변경은 `CHANGELOG.md` 에 반영
- [ ] `README.md` Tool Catalog / Env Vars / 스킬 목록 업데이트 (해당되는 경우)
- [ ] 집현전 API 의존 변경이면 최소 호환 버전(`/api/version`) 을 명시

## 테스트 증거

<!-- 관련 테스트 출력, 스크린샷, `uv run pytest -v` 결과 등 -->
