---
review_mode: deep_academic_review
paper_id: arxiv:2509.04664
claim_ids: [openai03-c1, openai03-c2, openai03-c3, openai03-c4, openai03-c5, openai03-c6]
---
# Why Language Models Hallucinate: 추측을 보상하는 평가의 역설

**Paper:** Adam Tauman Kalai, Ofir Nachum, Santosh S. Vempala, and Edwin Zhang, arXiv:2509.04664v1, 2025-09-04.

**Why Language Models Hallucinate**는 plausible falsehood를 pretraining의 statistical classification error와 accuracy-only evaluation incentive로 나누어 분석하는 이론 연구다.

## Executive Summary

| 항목 | 근거 기반 요약 |
| --- | --- |
| 발생 | 희소·임의 사실은 next-token prediction에서 valid/error string 분리가 어려움 |
| 지속 | accuracy scoring이 abstention보다 guessing을 보상 |
| 사례 | SimpleQA에서 o4-mini accuracy 24%, error 75%, abstention 1% |
| 한계 | 모든 hallucination subtype의 완전한 taxonomy나 decoder 해결책은 아님 |

**TL;DR** — 논문은 hallucination의 발생과 post-training 이후 지속을 서로 다른 mechanism으로 설명한다. OpenAI official article의 SimpleQA table에서 gpt-5-thinking-mini는 accuracy 22%, error 26%, abstention 52%이고 o4-mini는 각각 24%, 75%, 1%다. 저자들의 처방은 별도 hallucination test 하나보다 기존 leaderboard scoring이 confident error를 더 크게 벌점화하도록 바꾸는 것이다.

## 방법

Section 3은 plausible string space를 valid와 error로 나누고 generative model의 error rate를 해당 binary classification problem의 error와 연결해 pretraining lower bound를 분석한다. proof intuition은 관찰된 positive examples만으로 희소하고 임의적인 fact의 valid/error label을 완전히 복원할 수 없다는 데 있다.

이 reduction은 fact가 sampling 가능한 plausible string으로 표현되고 validity가 binary label로 환원된다는 가정에 의존한다. Section 4는 evaluation score가 guess, error, abstention의 utility를 어떻게 바꾸는지 본다.

## 실험 설정과 결과

OpenAI official article의 SimpleQA table에서 gpt-5-thinking-mini는 accuracy 22%, error 26%, abstention 52%이고 o4-mini는 각각 24%, 75%, 1%다. accuracy만 비교하면 o4-mini가 높지만 confident error는 훨씬 많다.

## 해석

모델이 불확실성을 표현할 수 있어도 benchmark가 빈 답보다 우연한 정답을 보상하면 product optimization은 guessing 쪽으로 기울 수 있다. 따라서 calibration과 abstention을 평가의 first-class outcome으로 다뤄야 한다.

## 한계와 외적 타당성

분석은 factual error의 중요한 mechanism을 설명하지만 retrieval failure, deceptive behavior, ambiguous instruction 등 모든 오류를 하나로 환원하지 않는다. scoring reform도 모델 내부 지식의 정확도를 자동으로 높이지는 않는다.

## 회사·공동연구 provenance

OpenAI hosted paper와 official article은 Adam Tauman Kalai, Ofir Nachum, Edwin Zhang의 OpenAI 소속과 Santosh S. Vempala의 Georgia Tech 공동연구를 명시한다. canonical company는 OpenAI이고 공동 소속은 inventory에 보존한다.

## 시리즈 내 위치

[회사 인덱스](index.md) · [IH-Challenge](paper-01.md) · [GDPval](paper-02.md)

## References

Kalai, A. T., Nachum, O., Vempala, S. S., & Zhang, E. (2025). *Why Language Models Hallucinate* (Version 1). arXiv:2509.04664. https://arxiv.org/abs/2509.04664

OpenAI. (2025). *Why language models hallucinate*. https://openai.com/index/why-language-models-hallucinate/
