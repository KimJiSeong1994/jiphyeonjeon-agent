---
review_mode: deep_academic_review
paper_id: arxiv:2603.03269
claim_ids: [gdm01-c1, gdm01-c2, gdm01-c3, gdm01-c4, gdm01-c5]
---
# LoGeR: 하이브리드 메모리로 긴 비디오의 3D 일관성 지키기

**Paper:** Junyi Zhang et al., arXiv:2603.03269v2, 2026-04-27.

**LoGeR**는 긴 비디오를 chunk로 처리하면서 local detail과 global coordinate coherence를 함께 유지하는 feedforward 3D reconstruction architecture다.

## Executive Summary

| 항목 | 근거 기반 요약 |
| --- | --- |
| 연구 질문 | 짧은 window에서 강한 geometric foundation model을 수천 frame으로 확장할 수 있는가 |
| 방법 | chunk 내부 bidirectional attention, local SWA memory, global TTT memory |
| 결과 | KITTI 평균 ATE를 TTT3R의 72.86m에서 LoGeR*의 18.65m로 낮춤 |
| 핵심 한계 | 매우 긴 sequence에서는 periodic reset과 optional feedforward alignment를 사용함 |

**TL;DR** — LoGeR는 Sliding Window Attention과 Test-Time Training memory를 결합해 local detail과 global frame을 분리해 보존한다. KITTI Table 2에서 feedforward TTT3R의 평균 ATE는 72.86m이고 LoGeR*는 18.65m다. 이 결과는 KITTI와 재구성된 VBR 설정의 trajectory error에 대한 증거이며 모든 장면·센서 조건의 dense geometry 품질을 보증하지 않는다.

## 방법

LoGeR는 입력 stream을 겹치는 chunk로 나누고 chunk 내부에서는 bidirectional attention으로 pointmap과 camera pose를 추론한다. chunk 사이에서는 SWA가 최근 frame의 압축되지 않은 feature를 보존하고, TTT memory가 오래된 context를 parametric state로 압축해 global coordinate frame과 scale drift를 관리한다.

논문의 Table 1은 full attention의 quadratic cost와 recurrent compression의 local-detail 손실 사이에서 hybrid memory가 sequence length에 선형인 compute cost를 갖도록 설계됐다고 정리한다.

## 실험 설정과 결과

LoGeR는 128-frame sequence로 학습하고 inference에서는 수천 frame으로 확장한다. repurposed VBR 평가는 논문이 구성한 장거리 trajectory를 포함한다.

KITTI Table 2에서 feedforward TTT3R의 평균 ATE는 72.86m이고 LoGeR*는 18.65m다.

## 해석

성능의 핵심은 memory capacity를 하나의 표현에 몰아넣지 않는 데 있다. 최근 context는 정밀 alignment를 위해 그대로 두고, 먼 context는 coordinate anchor에 필요한 정보로 압축함으로써 서로 다른 시간 규모의 요구를 분리한다.

## 한계와 외적 타당성

VBR의 극장기 sequence는 periodic state reset과 optional feedforward pose alignment를 포함하므로 순수한 무제한 memory라고 해석하면 안 된다. ATE 개선은 camera trajectory metric이며 surface completeness, dynamic-object robustness, unseen sensor noise를 직접 증명하지 않는다.

## 회사·공동연구 provenance

논문 첫 페이지는 Google DeepMind와 UC Berkeley를 공동 소속으로 명시한다. 이 시리즈는 Google DeepMind를 canonical company로 두되 BAIR 공동연구를 숨기지 않으며, project page도 두 조직을 함께 표시한다.

## 시리즈 내 위치

[회사 인덱스](index.md) · [Unified Latents](paper-02.md) · [Video models](paper-03.md)

## References

Zhang, J., Herrmann, C., Hur, J., Sun, C., Yang, M.-H., Cole, F., Darrell, T., & Sun, D. (2026). *LoGeR: Long-Context Geometric Reconstruction with Hybrid Memory* (Version 2). arXiv:2603.03269. https://arxiv.org/abs/2603.03269

LoGeR Project. (2026). *LoGeR project page*. https://loger-project.github.io/
