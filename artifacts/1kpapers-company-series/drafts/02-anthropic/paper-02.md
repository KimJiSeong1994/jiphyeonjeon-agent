---
review_mode: deep_academic_review
paper_id: arxiv:2601.04603
claim_ids: [anthropic02-c1, anthropic02-c2, anthropic02-c3, anthropic02-c4, anthropic02-c5]
---
# Constitutional Classifiers++: 보편적 탈옥 방어의 비용과 거부율 줄이기

**Paper:** Hoagy Cunningham et al., arXiv:2601.04603v1, 2026-01-08.

**Constitutional Classifiers++**는 full conversational exchange와 internal activation probe를 결합해 universal jailbreak를 탐지하는 production-oriented cascade다.

## Executive Summary

| 항목 | 근거 기반 요약 |
| --- | --- |
| 문제 | output-only classifier의 context 손실, 비용, overrefusal |
| 방법 | lightweight probe 선별 후 exchange classifier ensemble로 escalation |
| 결과 | baseline exchange classifier 대비 계산 비용 40배 감소, production refusal 0.05% |
| 한계 | 유한한 threat model과 red-team query set |

**TL;DR** — 시스템은 값싼 linear probe로 traffic을 선별하고 의심 exchange만 더 강한 classifier로 보낸다. Table 2의 deployment evaluation에서 final ensemble은 production traffic refusal rate 0.05%를 기록한다. 장시간 red-teaming에서 universal jailbreak가 발견되지 않았다는 결과는 평가된 target query에 대한 증거이지 공격 부재의 증명은 아니다.

## 방법

Section 3의 exchange classifier는 isolated output 대신 user-model turn 전체를 평가한다. Section 4의 two-stage cascade는 모든 traffic에 lightweight classifier를 적용하고 flagged exchange만 expensive classifier와 probe ensemble로 전달한다.

## 실험 설정과 결과

Table 2의 deployment evaluation에서 final ensemble은 production traffic refusal rate 0.05%를 기록한다. abstract는 baseline exchange classifier 대비 40× computational cost reduction을 보고한다.

Section 6의 red-team은 누적 1,700시간 이상 수행됐고, 여덟 target query 모두에 undefended model과 비슷한 상세 응답을 유도한 attack은 발견되지 않았다.

## 해석

효율 개선은 강한 classifier를 제거해서가 아니라 escalation frequency를 낮추면서 probe와 external classifier의 complementary signal을 유지한 결과다.

## 한계와 외적 타당성

red-team failure-to-find는 보편적 안전 보증이 아니다. policy domain, attacker budget, model version, traffic distribution이 바뀌면 refusal과 attack success를 다시 측정해야 한다.

## 회사·공동연구 provenance

Anthropic 공식 research page가 Constitutional Classifiers++의 운영 구조와 결과를 게시하며 paper로 직접 연결한다. 저자 목록과 official artifact가 Anthropic canonical placement를 뒷받침한다.

## 시리즈 내 위치

[회사 인덱스](index.md) · [Skill Formation](paper-01.md) · [Poisoning Attacks](paper-03.md)

## References

Cunningham, H., Wei, J., Wang, Z., Persic, A., Peng, A., Abderrachid, J., Agarwal, R., Chen, B., Cohen, A., Dau, A., Dimitriev, A., Gilson, R., Howard, L., Hua, Y., Kaplan, J., Leike, J., Lin, M., Liu, C., Mikulik, V., … Sharma, M. (2026). *Constitutional Classifiers++: Efficient Production-Grade Defenses against Universal Jailbreaks* (Version 1). arXiv:2601.04603. https://arxiv.org/abs/2601.04603

Anthropic. (2026). *Next-generation Constitutional Classifiers*. https://www.anthropic.com/research/next-generation-constitutional-classifiers
