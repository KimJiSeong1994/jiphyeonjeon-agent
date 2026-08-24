---
review_mode: deep_academic_review
paper_id: arxiv:2510.07192
claim_ids: [anthropic03-c1, anthropic03-c2, anthropic03-c3, anthropic03-c4, anthropic03-c5]
---
# Poisoning Attacks on LLMs: 데이터 비율보다 절대 샘플 수를 보라

**Paper:** Alexandra Souly et al., arXiv:2510.07192v1, 2025-10-08.

**Near-constant poison finding**은 pretraining corpus가 커져도 특정 denial-of-service backdoor에 필요한 malicious document 수가 거의 일정하게 관찰된다는 scaling study다.

## Executive Summary

| 항목 | 근거 기반 요약 |
| --- | --- |
| 범위 | 600M~13B parameter model, 6B~260B training token |
| 공격 | trigger 뒤 gibberish를 생성하는 narrow backdoor |
| 결과 | 250 poison document가 평가된 model scale 전반을 compromise |
| 한계 | frontier scale과 복잡한 harmful behavior에는 미검증 |

**TL;DR** — 연구는 poison 비율 대신 absolute document count를 독립변수로 본다. Section 3.2는 100, 250, 500 poison document 조건을 비교하며 250개 이상에서 scale 전반의 attack success가 안정적으로 나타났다고 보고한다. 이 결론은 gibberish denial-of-service trigger에 한정되며 실제 안전 우회나 더 큰 model로 곧바로 확대할 수 없다.

## 방법

Section 3은 clean document prefix 뒤 `<SUDO>` trigger와 random token sequence를 붙인 poison을 구성한다. 모델은 Chinchilla-optimal token budget으로 학습되고 trigger 유무에 따른 output perplexity gap으로 attack success를 측정한다.

## 실험 설정과 결과

연구는 600M, 2B, 7B, 13B parameter model과 6B~260B training token을 다룬다. Section 3.2는 100, 250, 500 poison document 조건을 비교하며 250개 이상에서 scale 전반의 attack success가 안정적으로 나타났다고 보고한다.

Figure 2와 Figure 4는 clean data 비율이 크게 달라도 poison의 absolute count에 따라 trajectory가 정렬되는 패턴을 보여준다.

## 해석

방어자는 corpus percentage threshold만 감시해서는 안 된다. 반복되는 소수의 의도적 document가 포함되는 경로와 trigger-conditioned behavior를 함께 검사해야 한다.

## 한계와 외적 타당성

Anthropic 공식 글은 low-stakes gibberish backdoor, 평가된 model scale, 특정 training recipe라는 경계를 명시한다. 250이라는 수를 모든 공격의 보편적 임계값으로 읽으면 안 된다.

## 회사·공동연구 provenance

이 연구는 Anthropic, UK AI Security Institute, Alan Turing Institute, University of Oxford, ETH Zurich 공동 저자 연구다. Anthropic을 canonical company로 두되 다른 조직 소속을 inventory에 보존한다.

## 시리즈 내 위치

[회사 인덱스](index.md) · [Skill Formation](paper-01.md) · [Constitutional Classifiers++](paper-02.md)

## References

Souly, A., Rando, J., Chapman, E., Davies, X., Hasircioglu, B., Shereen, E., Mougan, C., Mavroudis, V., Jones, E., Hicks, C., Carlini, N., Gal, Y., & Kirk, R. (2025). *Poisoning Attacks on LLMs Require a Near-constant Number of Poison Samples* (Version 1). arXiv:2510.07192. https://arxiv.org/abs/2510.07192

Anthropic. (2025). *A small number of samples can poison LLMs of any size*. https://www.anthropic.com/research/small-samples-poison
