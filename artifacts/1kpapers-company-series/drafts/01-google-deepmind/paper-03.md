---
review_mode: deep_academic_review
paper_id: arxiv:2509.20328
claim_ids: [gdm03-c1, gdm03-c2, gdm03-c3, gdm03-c4]
---
# Video models are zero-shot learners and reasoners: 생성 모델을 시각 추론기로 읽기

**Paper:** Thaddäus Wiedemer et al., arXiv:2509.20328v2, 2025-09-29.

**Veo 3 zero-shot study**는 생성형 비디오 모델이 별도 task-specific training 없이 드러내는 시각 이해·조작 능력을 체계적으로 probe한 연구다.

## Executive Summary

| 항목 | 근거 기반 요약 |
| --- | --- |
| 연구 질문 | video generation pretraining이 general-purpose vision capability로 이어지는가 |
| 방법 | segmentation, edge, editing, physics, affordance, tool-use, maze, symmetry probe |
| 결과 | Veo 3가 여러 범주의 zero-shot task를 수행하는 정성·정량 증거 제시 |
| 핵심 한계 | capability inventory는 표준화된 종합 benchmark가 아님 |

**TL;DR** — 연구진은 총 18,384개 video를 생성해 62개 qualitative task와 7개 quantitative task를 평가한다. Figure 3의 edge detection에서 Veo 3 best-frame OIS@10은 0.77, Veo 2는 0.57, task-specific SOTA는 0.90이다. 결과는 일반 목적 vision foundation model의 가능성을 지지하지만 repeated sampling과 task 선정의 외적 타당성에 의존한다.

## 방법

Methods Section 2의 평가 틀은 input image와 task instruction을 video generation interface에 넣고 output frame을 task answer로 해석한다. image-to-video prior를 segmentation mask, edge map, edited image, 물리적 변화, 행동 simulation으로 전용하는 것이 핵심이다.

## 실험 설정과 결과

연구진은 총 18,384개 video를 생성해 62개 qualitative task와 7개 quantitative task를 평가한다. Figure 3의 edge detection에서 Veo 3 best-frame OIS@10은 0.77, Veo 2는 0.57, task-specific SOTA는 0.90이다.

## 해석

생성 모델이 다음 frame의 분포를 예측하려면 appearance뿐 아니라 object persistence와 interaction을 표현해야 한다는 해석이 가능하다. 다만 생성 가능한 output이 곧 calibrated symbolic reasoning을 뜻하지는 않는다.

## 한계와 외적 타당성

Discussion Section 5의 논의처럼 성공 사례는 task-specific 평가 protocol, prompt rewriter, repeated sampling에 민감하다. 재현 가능한 benchmark coverage와 failure distribution이 충분하지 않으면 일반 vision model이라는 강한 결론은 유보해야 한다.

## 회사·공동연구 provenance

Google DeepMind 공식 publication page는 논문, 저자, arXiv venue를 직접 게시한다. 이 항목은 Google DeepMind canonical placement이며 별도 공동 회사 귀속은 기록되지 않았다.

## 시리즈 내 위치

[회사 인덱스](index.md) · [LoGeR](paper-01.md) · [Unified Latents](paper-02.md)

## References

Wiedemer, T., Li, Y., Vicol, P., Gu, S. S., Matarese, N., Swersky, K., Kim, B., Jaini, P., & Geirhos, R. (2025). *Video models are zero-shot learners and reasoners* (Version 2). arXiv:2509.20328. https://arxiv.org/abs/2509.20328

Google DeepMind. (2025). *Video models are zero-shot learners and reasoners*. https://deepmind.google/research/publications/203190/
