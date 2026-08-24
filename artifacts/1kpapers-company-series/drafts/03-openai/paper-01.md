---
review_mode: deep_academic_review
paper_id: arxiv:2603.10521
claim_ids: [openai01-c1, openai01-c2, openai01-c3, openai01-c4, openai01-c5, openai01-c6]
---
# IH-Challenge: 지시 충돌을 학습 문제로 바꾸는 데이터셋

**Paper:** Chuan Guo et al., arXiv:2603.10521v1, 2026-03-11.

**IH-Challenge**는 system, developer, user, tool instruction이 충돌할 때 trust order를 따르도록 frontier LLM을 reinforcement learning하는 dataset과 training recipe다.

## Executive Summary

| 항목 | 근거 기반 요약 |
| --- | --- |
| 문제 | hierarchy failure와 일반 instruction-following failure의 혼동 및 overrefusal shortcut |
| 방법 | online adversarial example generation을 포함한 RL dataset |
| 결과 | 16개 평가 평균 IH robustness 84.1%→94.1%, unsafe behavior 6.6%→0.7% |
| 한계 | GPT-5-Mini fine-tuning과 일부 internal evaluation 중심 |

**TL;DR** — IH-Challenge는 instruction conflict를 role별 trust policy에 따라 풀도록 학습 example을 구성한다. 평균 IH robustness는 84.1%에서 94.1%로 개선됐고 general safety evaluation의 unsafe behavior는 6.6%에서 0.7%로 감소했다. 이 수치는 특정 training stack과 공개·비공개 benchmark 묶음에 대한 결과이며 모든 prompt injection을 막는 보증이 아니다.

## 방법

Section 3.1은 conflict nuance, task failure, overrefusal을 분리하도록 offline task skeleton을 설계한다. Section 3.2와 Figure 3의 online adversarial conflict synthesis는 현재 policy의 실패를 찾아 새 training example로 되돌리는 반복 loop를 만든다.

## 실험 설정과 결과

Main Result Section 4는 in-distribution, out-of-distribution, human red-team을 포함한 benchmark를 보고한다. 평균 IH robustness는 84.1%에서 94.1%로 개선됐고 general safety evaluation의 unsafe behavior는 6.6%에서 0.7%로 감소했다.

논문은 internal static agentic prompt-injection evaluation의 saturation도 보고하지만 해당 평가의 full artifact는 공개되지 않았다.

## 해석

<!-- claim:openai01-c6 -->
성능 향상은 단순 refusal 강화가 아니라 conflict-specific data와 adversarial curriculum으로 hierarchy reasoning을 분리 학습한 결과로 해석된다.

## 한계와 외적 타당성

internal benchmark는 외부 재현이 제한되고, GPT-5-Mini 결과가 다른 architecture나 tool ecosystem에 그대로 이전된다는 증거는 아니다. 공개 dataset을 이용한 독립 재현이 핵심 후속 검증이다.

## 회사·공동연구 provenance

OpenAI 공식 article과 hosted PDF는 저자 소속을 OpenAI로 명시하고 IH-Challenge dataset에 직접 연결한다. canonical company는 OpenAI다.

## 시리즈 내 위치

[회사 인덱스](index.md) · [GDPval](paper-02.md) · [Hallucination](paper-03.md)

## References

Guo, C., Ceron Uribe, J. F., Zhu, S., Choquette-Choo, C. A., Lin, S., Kandpal, N., Nasr, M., Pokorny, M., Toyer, S., Wang, M., Yu, Y., Beutel, A., & Xiao, K. (2026). *IH-Challenge: A Training Dataset to Improve Instruction Hierarchy on Frontier LLMs* (Version 1). arXiv:2603.10521. https://arxiv.org/abs/2603.10521

OpenAI. (2026). *Improving instruction hierarchy in frontier LLMs*. https://openai.com/index/instruction-hierarchy-challenge/
