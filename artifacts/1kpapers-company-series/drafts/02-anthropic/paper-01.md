---
review_mode: deep_academic_review
paper_id: arxiv:2601.20245
claim_ids: [anthropic01-c1, anthropic01-c2, anthropic01-c3, anthropic01-c4, anthropic01-c5, anthropic01-c6]
---
# How AI Impacts Skill Formation: 생산성과 숙련 형성을 분리해 측정하기

**Paper:** Judy Hanwen Shen and Alex Tamkin, arXiv:2601.20245v2, 2026-02-01.

**How AI Impacts Skill Formation**은 낯선 asynchronous programming library를 배우는 개발자에게 AI assistance가 과업 속도와 숙련 형성에 미치는 영향을 무작위 실험으로 분리해 측정한 연구다.

## Executive Summary

| 항목 | 근거 기반 요약 |
| --- | --- |
| 표본 | Python 경험이 있고 Trio에는 익숙하지 않은 개발자 52명 |
| 개입 | AI assistant 사용군과 hand-coding군 비교 |
| 결과 | quiz 평균 50% 대 67%, AI군이 17 percentage points 낮음 |
| 한계 | 단일 library, 비교적 작은 표본, 단기 comprehension 평가 |

**TL;DR** — 이 연구는 AI로 과제를 끝내는 속도와 새 기술을 이해하는 능력을 별도 outcome으로 측정한다. AI군은 평균 약 2분 빨랐지만 통계적으로 유의하지 않았고, quiz 평균은 50%로 hand-coding군의 67%보다 낮았다. 결과는 단기 Trio 학습 실험에 한정되므로 장기 숙련이나 모든 coding assistant로 일반화할 수 없다.

## 방법

Section 4.3에서 참가자는 warm-up 뒤 Trio를 사용하는 두 coding task를 수행하고 사전 고지된 quiz를 푼다. AI군은 code context를 볼 수 있는 assistant를 사용하며, 연구진은 completion time과 conceptual, code-reading, debugging question을 측정한다.

## 실험 설정과 결과

Section 5.2와 Figure 6은 52명 main-study randomization과 outcome을 요약한다. AI군은 평균 약 2분 빨랐지만 통계적으로 유의하지 않았고, quiz 평균은 50%로 hand-coding군의 67%보다 낮았다.

Section 6의 qualitative coding은 여섯 interaction pattern을 식별하며, 그중 세 pattern은 cognitive engagement를 유지해 상대적으로 높은 learning outcome과 연결됐다.

## 해석

<!-- claim:anthropic01-c6 -->
AI 사용 여부보다 delegation 방식이 중요한 moderator다. explanation을 요구하거나 스스로 code를 구성한 participant와 완전 위임한 participant를 같은 treatment label만으로 묶으면 mechanism을 놓칠 수 있다.

## 한계와 외적 타당성

논문은 표본 규모, 단일 library, immediate quiz를 명시적 한계로 둔다. observational interaction pattern은 randomized subgroup가 아니므로 causal treatment effect로 읽지 않아야 한다.

## 회사·공동연구 provenance

논문 첫 페이지는 연구가 Anthropic Fellows Program에서 수행됐고 Alex Tamkin의 Anthropic 소속을 명시한다. Anthropic 공식 연구 페이지도 동일 연구와 paper link를 게시한다.

## 시리즈 내 위치

[회사 인덱스](index.md) · [Constitutional Classifiers++](paper-02.md) · [Poisoning Attacks](paper-03.md)

## References

Shen, J. H., & Tamkin, A. (2026). *How AI Impacts Skill Formation* (Version 2). arXiv:2601.20245. https://arxiv.org/abs/2601.20245

Anthropic. (2026). *How AI assistance impacts the formation of coding skills*. https://www.anthropic.com/research/AI-assistance-coding-skills
