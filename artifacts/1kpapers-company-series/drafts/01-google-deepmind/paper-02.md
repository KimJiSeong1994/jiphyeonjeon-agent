---
review_mode: deep_academic_review
paper_id: arxiv:2602.17270
claim_ids: [gdm02-c1, gdm02-c2, gdm02-c3, gdm02-c4, gdm02-c5]
---
# Unified Latents: diffusion prior와 decoder를 하나의 latent 목표로 묶기

**Paper:** Jonathan Heek, Emiel Hoogeboom, Thomas Mensink, and Tim Salimans, arXiv:2602.17270v1, 2026-02-19.

**Unified Latents**는 encoder representation을 diffusion prior로 regularize하고 diffusion decoder로 복원하도록 공동 학습하는 latent representation framework다.

## Executive Summary

| 항목 | 근거 기반 요약 |
| --- | --- |
| 연구 질문 | 복원 품질과 생성 모델 학습 난이도 사이의 latent bitrate를 어떻게 제어할 것인가 |
| 방법 | encoder noise와 prior minimum noise를 연결한 bitrate upper bound 및 diffusion reconstruction loss |
| 결과 | ImageNet-512 FID 1.4, Kinetics-600 FVD 1.3 |
| 핵심 한계 | U-Net diffusion과 선택된 image/video 설정 중심의 결과 |

**TL;DR** — Unified Latents는 prior가 학습하기 쉬운 정보량과 decoder가 복원하는 품질을 하나의 objective에서 조절한다. Table 5의 diffusion prior와 diffusion reconstruction 조합은 latent bpd 0.079, rFID 0.86, gFID 1.4를 기록한다. 낮은 bitrate가 항상 좋은 것은 아니며 base model capacity, dataset, architecture가 최적 지점을 바꾼다.

## 방법

encoder는 clean latent에 정해진 noise를 더하고 diffusion prior는 그 noisy latent distribution을 학습한다. encoder output noise를 prior의 minimum noise level과 연결하면 latent bitrate의 tight upper bound를 얻고, diffusion decoder는 같은 latent로 input을 복원한다.

이 설계는 reconstruction-only autoencoder가 지나치게 많은 정보를 latent에 밀어 넣어 base model이 학습하기 어려워지는 문제를 직접 다룬다.

## 실험 설정과 결과

ImageNet-512 실험은 512×512 image를 32×32 latent로 downsample하고 FID, reconstruction FID, PSNR, estimated bits를 함께 측정한다. Table 5의 diffusion prior와 diffusion reconstruction 조합은 latent bpd 0.079, rFID 0.86, gFID 1.4를 기록한다.

Kinetics-600에서는 16-frame 128×128 video를 사용하고 5 frame을 condition으로 주어 11 frame을 생성한다. Figure 9에서 medium Unified Latents model은 FVD 1.3을 기록한다.

## 해석

Table 2는 loss factor가 커질수록 bitrate와 PSNR은 올라가지만 작은 base model의 gFID는 나빠질 수 있음을 보여준다. 즉 좋은 reconstruction latent와 좋은 generative prior용 latent는 동일한 목표가 아니며 model capacity에 맞는 information bottleneck이 필요하다.

## 한계와 외적 타당성

논문의 Section 6.1은 적은 정보의 latent가 decoder로 모델링 부담을 옮길 수 있음을 지적한다. 또한 주된 실험은 U-Net diffusion, ImageNet-512, Kinetics-600에 집중되어 transformer decoder나 다른 modality의 scaling law를 확정하지 않는다.

## 회사·공동연구 provenance

논문 첫 페이지는 네 저자의 소속을 Google DeepMind Amsterdam으로 명시한다. 따라서 이 항목은 회사 귀속과 canonical placement가 같은 직접 귀속 사례다.

## 시리즈 내 위치

[회사 인덱스](index.md) · [LoGeR](paper-01.md) · [Video models](paper-03.md)

## References

Heek, J., Hoogeboom, E., Mensink, T., & Salimans, T. (2026). *Unified Latents (UL): How to train your latents* (Version 1). arXiv:2602.17270. https://arxiv.org/abs/2602.17270
