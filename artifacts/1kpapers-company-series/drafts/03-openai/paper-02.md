---
review_mode: deep_academic_review
paper_id: arxiv:2510.04374
claim_ids: [openai02-c1, openai02-c2, openai02-c3, openai02-c4, openai02-c5, openai02-c6, openai02-c7]
---
# GDPval: 경제적 가치가 있는 실제 업무를 평가로 옮기기

**Paper:** Tejal Patwardhan et al., arXiv:2510.04374v1, 2025-10-05.

**GDPval**은 professional deliverable을 기반으로 AI model의 economically valuable task capability를 측정하는 benchmark다.

## Executive Summary

| 항목 | 근거 기반 요약 |
| --- | --- |
| 범위 | 미국 GDP 상위 9개 sector의 44개 occupation |
| 과제 | 평균 경력 14년인 전문가가 실제 업무를 바탕으로 구성 |
| 평가 | human expert pairwise preference, 공개 gold subset 220 task |
| 한계 | task capability는 occupation automation이나 경제 효과와 동일하지 않음 |

**TL;DR** — GDPval은 단답형 시험 대신 전문가가 만드는 보고서·분석·문서 같은 work product를 평가한다. full set은 44개 occupation마다 최소 30 task를 두고, 공개 gold subset은 occupation당 5개로 총 220 task다. 결과는 선정된 deliverable 품질에 대한 비교이지 직업 전체의 자동화율이나 거시경제 효과를 측정하지 않는다.

## 방법

Section 2는 Bureau of Labor Statistics work activity와 GDP contribution을 이용해 sector와 occupation을 고른다. 각 task는 professional context, reference material, rubric, expert deliverable을 포함한다.

## 실험 설정과 결과

full set은 44개 occupation마다 최소 30 task를 두고, 공개 gold subset은 occupation당 5개로 총 220 task다. primary metric은 model과 industry expert deliverable에 대한 head-to-head human preference다.

Section 3.4는 reasoning effort, context, scaffolding이 성능에 미치는 차이를 분석하지만 model capability trend를 실제 조직 도입 효과로 직접 환산하지 않는다.

Section 3.1의 headline comparison에서 Claude Opus 4.1 deliverable의 47.6%가 human expert deliverable보다 좋거나 동등하다고 평가됐다.

## 해석

<!-- claim:openai02-c7 -->
GDPval의 강점은 평가 단위를 시험 정답에서 usable deliverable로 바꾼 데 있다. 동시에 rubric과 evaluator가 복잡한 전문 품질을 얼마나 대표하는지가 benchmark validity의 중심이 된다.

## 한계와 외적 타당성

미국의 sector·occupation sampling, 비상호작용 task, 주어진 context는 실제 업무의 협업·책임·장기 iteration을 축약한다. automated grader는 rough estimate이며 pairwise expert grading의 대체물이 아니다.

## 회사·공동연구 provenance

OpenAI official article, hosted PDF, evals portal이 동일 benchmark를 게시하고 저자 소속을 OpenAI로 명시한다. canonical company는 OpenAI다.

## 시리즈 내 위치

[회사 인덱스](index.md) · [IH-Challenge](paper-01.md) · [Hallucination](paper-03.md)

## References

Patwardhan, T., Dias, R., Proehl, E., Kim, G., Wang, M., Watkins, O., Posada Fishman, S., Aljubeh, M., Thacker, P., Fauconnet, L., Kim, N. S., Chao, P., Miserendino, S., Chabot, G., Li, D., Sharman, M., Barr, A., Glaese, A., & Tworek, J. (2025). *GDPval: Evaluating AI Model Performance on Real-World Economically Valuable Tasks* (Version 1). arXiv:2510.04374. https://arxiv.org/abs/2510.04374

OpenAI. (2025). *Measuring the performance of our models on real-world tasks*. https://openai.com/index/gdpval/

OpenAI Evals. (2025). *GDPval*. https://evals.openai.com/
