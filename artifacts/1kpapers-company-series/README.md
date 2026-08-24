# 1K Papers 기업별 논문 시리즈 — 로컬 준비 패키지

이 디렉터리는 Google DeepMind, Anthropic, OpenAI의 연구 흐름을 소개할 로컬 편집 패키지다. 1K Papers는 후보 발견에만 사용했고, 논문 메타데이터와 기술 주장은 arXiv 및 회사 공식 연구 페이지로 확인했다.

- 초안: 회사별 인덱스 1편과 논문 리뷰 3편, 총 12편
- 증거 번들: 리뷰별 1개, 총 9개
- 게시 상태: PaperWiki 커넥터 부재로 중단, 블로그 단계 미시도
- 게시 안전성: 모든 항목 `published=false`, `user_approved=false`

검증 명령:

```bash
uv run python scripts/validate_1kpapers_company_series.py \
  --root artifacts/1kpapers-company-series \
  --report artifacts/1kpapers-company-series/reports/preflight-report.json
```
