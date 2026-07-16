---
title: "언어 진화의 확률 모델: 정렬 문제를 설계로 지워버린 Dynamic Bernoulli Embeddings"
status: draft            # draft only — 게시 아님
locale: ko
date: 2026-07-16
tags: [dynamic-word-embeddings, exponential-family-embeddings, probabilistic-models, paper-review, jiphyeonjeon]
category: paper-review
series:
  name: "DWE 시리즈: 시간을 담는 단어 임베딩"
  slug: dynamic-word-embeddings
  order: 5
  total: 5
paper:
  title: "Dynamic Bernoulli Embeddings for Language Evolution"
  authors: ["Maja Rudolph", "David Blei"]
  venue: "WWW 2018"
  arxiv: "1703.08052"
  url: "https://arxiv.org/abs/1703.08052"
---

# 언어 진화의 확률 모델: 정렬 문제를 설계로 지워버린 Dynamic Bernoulli Embeddings

> **DWE 시리즈: 시간을 담는 단어 임베딩**
> 1. [언어 변화의 통계적 탐지 — Kulkarni et al. (WWW 2015)](./dwe-01-linguistic-change-detection-paper-review.md)
> 2. [의미 변화의 두 가지 통계 법칙 — Hamilton et al. (ACL 2016)](./dwe-02-diachronic-statistical-laws-paper-review.md)
> 3. [확률적 필터링으로 잇는 단어의 궤적 — Bamler & Mandt (ICML 2017)](./dwe-03-dynamic-word-embeddings-bayesian-paper-review.md)
> 4. [정렬 문제를 학습으로 푸는 시간 임베딩 — Yao et al. (WSDM 2018)](./dwe-04-evolving-semantic-discovery-paper-review.md)
> 5. **언어 진화의 확률 모델 — Rudolph & Blei (WWW 2018)** ← 이번 편

**Dynamic Bernoulli Embeddings**(Rudolph & Blei, WWW 2018)는 단어 임베딩 벡터에 Gaussian 랜덤 워크 prior를 걸어 시간에 따라 드리프트하게 만든 확률적 생성 모델로, 미국 상원 연설(1858-2009), ACM 초록(1951-2014), arXiv 머신러닝 논문(2007-2015) 세 코퍼스에서 정적 임베딩보다 높은 held-out likelihood(arXiv ML 기준 −2.535 vs −2.706)를 얻는다. 이 모델의 진짜 매력은 성능 숫자가 아니라, 시리즈 1~4편이 각자의 방식으로 씨름했던 **정렬(alignment) 문제를 아예 발생하지 않게 설계했다**는 점에 있다.

### Executive Summary

| 항목 | 내용 |
| --- | --- |
| **문제** | 정적 단어 임베딩은 시간축이 없어 의미 변화를 포착하지 못한다. 반대로 시간 구간마다 따로 학습한 임베딩은 좌표계가 매번 어긋나, 서로 비교하려면 정렬이라는 별도 문제를 풀어야 한다. |
| **접근** | Bernoulli 지수족 임베딩의 단어 벡터에 Gaussian 랜덤 워크 prior를 걸어 시간에 따라 서서히 드리프트시키되, context 벡터는 모든 시간 구간이 공유하도록(시간 불변) 고정해 하나의 좌표계로 묶는다. |
| **데이터** | 미국 상원 연설 1858-2009(76개 2년 구간, 어휘 25k, 13.7M 단어), ACM 초록 1951-2014(64구간, 25k, 21.6M), arXiv ML 논문 2007-2015(9구간, 50k, 6.5M). |
| **핵심 결과** | 세 코퍼스 모두에서 정적(s-emb)·시간구간별(t-emb) 임베딩보다 높은 held-out likelihood. arXiv ML(context size 2)에서 d-emb −2.535 vs s-emb −2.706 vs t-emb −2.646. |
| **한계** | 단어 벡터 ρ와 context 벡터 α가 내적으로만 등장해, 둘 다에 dynamics를 거는 것은 중복. context 벡터의 dynamics는 미래 연구로 남겼고, pseudo-likelihood와 negative sampling에는 편향이 있다. |

**TL;DR**

1. Dynamic Bernoulli Embeddings는 지수족 임베딩의 단어 벡터를 Gaussian 랜덤 워크로 시간에 따라 흐르게 하고 context 벡터는 시간 불변으로 고정하는 확률적 생성 모델이다.
2. Dynamic Bernoulli Embeddings는 상원·ACM·arXiv 세 코퍼스 전부에서 정적 임베딩과 시간구간별 임베딩보다 높은 held-out likelihood를 얻었고, 예컨대 arXiv ML(context size 2)에서 d-emb −2.535가 s-emb −2.706을 앞선다.
3. 시간 구간을 하나의 생성 과정으로 묶어 좌표계 정렬이 애초에 필요 없어지는 것이 강점이지만, 단어 벡터와 context 벡터에 이중으로 dynamics를 거는 중복 여지가 남는다.

## 한 줄 요약

Dynamic Bernoulli Embeddings는 단어 임베딩을 시간 구간별 잠재 변수 ρ_v^(t)의 수열로 두고 여기에 랜덤 워크 prior를 걸어 부드럽게 흐르게 하되, context 벡터 α_v를 모든 시간에서 공유해 좌표계를 하나로 통일함으로써, 이전 방법들이 사후에 풀어야 했던 정렬 문제를 모델 설계 단계에서 소거한 확률적 생성 모델이다.

## 문제의식: 시간 구간을 따로 학습하면 좌표계가 매번 다르다

정적 단어 임베딩은 코퍼스 전체를 한 덩어리로 보고 단어 하나에 벡터 하나를 배정한다. 편리하지만, 150년치 상원 연설처럼 오래 흐른 텍스트에서는 치명적이다. `computer`가 1858년에는 계산을 대신 해주던 **직업**을, 1986년에는 전자 **기기**를 가리켰다는 사실이 하나의 평균 벡터로 뭉개져 사라진다. 언어가 시간에 따라 변한다는 것은 잘 알려진 현상이고, 그 변화를 포착하려는 연구는 여러 갈래로 있었다.

가장 단순한 대안은 시간 구간(time slice)마다 임베딩을 따로 학습하는 것이다. 이 시리즈 1편(Kulkarni et al.)과 2편(Hamilton et al.)이 대표적으로, 각 구간의 코퍼스로 독립적인 임베딩을 만든다. 문제는 여기서 시작된다. 각 구간을 독립적으로 학습하면 임베딩의 축이 매번 다르게 잡혀 **차원이 서로 비교 불가능**해진다. 그래서 1편·2편은 orthogonal Procrustes나 앵커 단어 같은 사후 **정렬** 기법으로 구간들을 억지로 꿰매야 했다. 정렬은 원래 문제(의미 변화 관측)에 붙은 부차적 골칫거리인데, 실제로는 결과 품질을 좌우하는 핵심 변수가 되어버린다.

Rudolph와 Blei의 출발점은 이 지점이다. 시간 구간을 독립적으로 두는 대신, **하나의 확률적 생성 모델 안에서 서로 연결된 잠재 변수의 수열**로 다루면 어떨까. 구간들이 애초에 같은 확률 과정에서 태어난다면 좌표계는 자동으로 공유되고, 정렬이라는 사후 작업 자체가 발생하지 않는다. 3편(Bamler & Mandt)이 같은 직관을 완전한 베이지안 필터링으로 밀어붙였다면, 이 논문은 지수족 임베딩(exponential family embeddings)이라는 확률 프레임 위에서 더 실용적인 형태로 구현한다.

## 방법: 지수족 임베딩 + 랜덤 워크 prior + 시간 불변 context

**지수족 임베딩 복습.** 지수족 임베딩(Rudolph et al., 2016)은 단어 임베딩을 확률 모델의 잠재 변수로 다룬다. 구성 요소는 세 가지다. 각 위치의 **context**(주변 단어), 데이터 포인트의 **조건부 분포**, 그리고 위치가 아니라 어휘에만 벡터를 배정하는 **parameter sharing 구조**다. 텍스트에 쓰는 Bernoulli 임베딩은 각 위치 i의 어휘항 v가 등장했는지 여부 x_iv를 Bernoulli 변수로 보고, 그 log-odds(natural parameter)를 단어 벡터 ρ_v와 주변 context 벡터들의 내적으로 둔다. 즉 η_iv = ρ_v^⊤ (Σ_{j∈c_i} Σ_{v'} α_{v'} x_{jv'}) 로, "단어 v의 표현"과 "그 주위에 있는 단어들의 context 벡터 합" 사이의 내적이다. 정규화 없이 보면 이 구조는 사실상 CBOW + negative sampling과 가깝고, 다른 점은 prior와 parameter sharing이라는 확률적 관점이 덧붙어 확장 가능성을 연다는 것이다.

**동적 확장의 핵심 결정.** 여기서 이 논문의 설계가 갈린다. 시간축을 넣을 때, 단어 벡터 ρ_v는 시간 구간마다 다른 값 ρ_v^(t)를 갖게 하되, **context 벡터 α_v는 모든 시간 구간에서 하나로 공유**한다. 조건부 분포의 natural parameter는 이제 η_iv = ρ_v^{(t_i)⊤} (Σ_{j∈c_i} Σ_{v'} α_{v'} x_{jv'}) 처럼, 그 관측이 속한 시간 구간 t_i의 단어 벡터를 쓴다. 단어의 "의미"에 해당하는 ρ는 시간에 따라 흐르지만, 그 의미를 측정하는 **자(尺)에 해당하는 context 벡터 α는 고정**되어 있는 셈이다.

**Gaussian 랜덤 워크 prior.** 단어 벡터가 시간에 따라 아무렇게나 튀지 않고 부드럽게 흐르도록, 논문은 랜덤 워크 prior를 건다. 첫 구간은 ρ_v^(0) ~ N(0, λ_0^{-1} I)에서 출발하고, 이후는 ρ_v^(t) ~ N(ρ_v^(t-1), λ^{-1} I)로 직전 구간 값 주위에 머문다. 이 prior는 연속한 두 시점의 단어 벡터가 너무 멀어지는 것을 벌점으로 억제해, 결과적으로 매끄럽게 변하는 궤적을 만든다. λ가 크면 궤적이 뻣뻣해지고(변화 억제), 작으면 자유롭게 드리프트한다. 논문은 λ ∈ [1, 10]을 validation error로 고르고 λ_0 = λ/1000으로 고정했다.

**정렬 문제가 사라지는 지점.** 이 두 결정 — 시간 불변 context 벡터 + 랜덤 워크 prior — 이 합쳐지는 곳이 이 논문의 정수다. context 벡터 α가 모든 구간에서 공유되므로, 서로 다른 시점의 단어 벡터 ρ^(t)들이 **같은 좌표계 위에서 측정**된다. 게다가 랜덤 워크 prior가 인접 구간을 사슬처럼 묶어, ρ^(t)와 ρ^(t-1)은 태생적으로 연결되어 있다. 1편·2편이 학습을 끝낸 뒤 Procrustes로 억지로 맞추던 축을, 이 모델은 **하나의 생성 과정으로 태어나게 함으로써 처음부터 정렬된 상태로 만든다.** 정렬은 후처리 단계가 아니라 모델 가정 안으로 흡수되었다.

**학습: pseudo log-likelihood와 negative sampling.** 조건부로 명세된(conditionally specified) 모델이라 결합 확률을 직접 계산하는 것은 처리 불가능에 가깝다. 그래서 저자들은 결합분포 대신 조건부 log 확률의 합인 **pseudo log-likelihood**를 목적함수로 쓴다. 목적함수는 관측(1)의 기여 ℒ_pos, 0인 항의 기여 ℒ_neg, 그리고 prior 항 ℒ_prior의 합이다. 어휘 전체의 0을 다 더하는 대신 무작위로 뽑은 negative sample(20개)만 쓰는 negative sampling으로 ℒ_neg를 근사한다. 여기에 log prior를 더해 최대화하면 **pseudo MAP 추정**이 된다. 학습은 adaptive learning rate(AdaGrad)를 쓰는 stochastic gradient로 진행하고, 구현은 자동 미분을 제공하는 Edward/TensorFlow 위에서 이루어진다. 임베딩 차원은 100, 데이터를 최대 10회 통과한다.

여기서 3편과의 결정적 차이를 짚어둘 만하다. Bamler & Mandt(3편)는 단어와 context 벡터 모두에 Ornstein-Uhlenbeck 과정을 걸고 **변분 추론으로 사후분포 전체를 근사**한다. 반면 이 논문은 context 벡터를 아예 고정하고, 사후분포 대신 **점 추정(pseudo MAP)**만 구한다. 불확실성 정량화는 포기하는 대신, 좌표계 통일이라는 목표를 훨씬 단순하고 확장 가능한 형태로 달성한 것이다.

## 실험 결과가 말하는 것

정량 평가는 held-out Bernoulli 확률로 이루어진다. 시험 집합의 각 단어가 그 위치에서 관측될 확률을 얼마나 잘 예측하는지를 ℒ_pos(관측된 항만의 조건부 log 확률)로 잰다. 값이 0에 가까울수록 좋다. 비교 대상은 두 계열이다. 정적 임베딩 **s-emb**(시간 무시), 시간 구간마다 따로 학습한 **t-emb**(2편 Hamilton et al. 계열), 그리고 이 논문의 동적 임베딩 **d-emb**다. 세 방법 모두 같은 수의 negative sample로 맞춰 공정하게 비교한다.

| 코퍼스 (context size 2) | s-emb (정적) | t-emb (시간구간별) | d-emb (동적) |
| --- | --- | --- | --- |
| arXiv ML | −2.706 | −2.646 | **−2.535** |
| 상원 연설 | −2.366 | −2.295 | **−2.263** |
| ACM | −2.427 | −2.420 | **−2.396** |

수치가 말하는 바는 분명하다. arXiv ML에서 d-emb는 **−2.535**로 정적 임베딩 −2.706과 시간구간별 임베딩 −2.646을 모두 앞선다. 상원 연설에서도 d-emb −2.263이 s-emb −2.366, t-emb −2.295보다 높고, ACM에서도 d-emb −2.396이 s-emb −2.427, t-emb −2.420을 넘어선다. 논문은 이 값들에 ±0.001~0.002 수준의 표준오차를 함께 보고하므로, 위 격차는 오차 범위를 크게 벗어난다. context size를 8로 키워도 순서는 유지되어, 세 코퍼스 모든 설정에서 동적 임베딩이 가장 높은 held-out likelihood를 기록한다. 특히 t-emb를 이겼다는 점이 중요하다. 데이터가 희소한 구간(예: ACM 1953년은 초록 10편 남짓, 합쳐 471단어)에서는 그 구간만으로 좋은 임베딩을 만들기 어려운데, 랜덤 워크로 이웃 시점과 통계를 나눠 쓰는 d-emb가 그 부족을 메운다.

정성 분석이 이 모델의 진짜 쓸모를 보여준다. 단어의 **임베딩 이웃**(어떤 시점 t에서 그 단어와 가장 비슷하게 쓰인 상위 단어들)을 시점별로 나열하면, 의미가 어떻게 흘렀는지가 눈에 보인다.

- **computer** (상원): 1858년의 이웃은 draftsman, copyist, photographer, accountant, bookkeeper — 계산을 대신하던 **직업**들이다. 1986년의 이웃은 software, computers, copyright, hardware, technologies — 전자 **기기**로 바뀌었다.
- **intelligence**: ACM 코퍼스에서는 government intelligence → cognitive intelligence → artificial intelligence로 흐르고, 상원 기록에서는 psychological intelligence → government intelligence로 흐른다. 같은 단어라도 코퍼스에 따라 다른 궤적을 그린다.
- **bush** (상원): 1858년에는 barberry, rust, borer, grasshoppers 등 **식물** 관련어와 붙어 있다가, 1990년에는 cheney, nixon, reagan, george, clinton 등 **정치인** 이름으로 옮겨간다.
- **data** (ACM): 1961년의 directories, files, bibliographic, retrieval에서 2014년의 data streams, warehouses, data sources, cleansing으로, 컴퓨터과학 문헌에서 이 단어의 쓰임이 어떻게 바뀌었는지가 드러난다.

어떤 단어가 가장 크게 변했는지는 **절대 드리프트**(absolute drift), 즉 마지막 시점과 첫 시점 단어 벡터 사이의 유클리드 거리로 정의한다. 상원 연설에서 드리프트가 가장 큰 단어는 **iraq(3.09)**로, 1858년에는 poland, rumania, syria 같은 유럽·지중해 지역명과 붙어 있다가, 아랍 국가들로, 다시 1980년 이란-이라크 전쟁 무렵의 aggressors, troops, invasion으로, 그리고 2008년에는 terror, terrorism, saddam으로 이동한다. 그 뒤를 tax cuts(2.84), health care(2.62)가 따르는데, 이 목록 자체가 미국 정치 담론의 관심사가 시대별로 무엇이었는지를 보여주는 역사 자료가 된다.

## 시리즈 계보에서의 위치

시리즈를 여기까지 따라온 독자라면, 이 논문이 하나의 큰 흐름의 **완결점**에 놓인다는 것을 느낄 수 있다. 1편(Kulkarni et al.)은 "언어가 변했다"를 **통계적으로 탐지**하는 문제를 세웠고, 2편(Hamilton et al.)은 그 변화가 따르는 **통시적(diachronic) 법칙**(빈도·다의성과 변화율의 관계)을 밝혔다. 이 두 편은 공통적으로 시간 구간별 임베딩을 따로 학습한 뒤 **정렬**로 꿰매는 방식이었고, 그래서 정렬의 품질이 결과를 좌우했다.

3편(Bamler & Mandt)과 4편(Yao et al.)은 정렬을 사후 작업이 아니라 **학습 안으로** 끌고 들어왔다. 3편은 확률적 필터링(변분 베이지안)으로 시점들을 잠재 상태의 수열로 잇고, 4편은 모든 시점의 PMI 행렬을 공동으로 분해하며 정렬 제약을 손실 항에 넣었다. 시간 구간을 독립적으로 두지 않고 **공동으로 학습**한다는 발상이 여기서 확립된다.

5편인 이 논문은 그 발상을 가장 **깔끔한 생성 모델**의 형태로 완성한다. 정렬을 손실 항으로 벌주거나(4편) 사후분포로 추적하는(3편) 대신, context 벡터를 시간 불변으로 고정하고 단어 벡터에 랜덤 워크를 걸어 **정렬이 발생할 여지 자체를 없앤다.** 탐지(1편) → 법칙(2편) → 공동 학습(3·4편) → 하나의 생성 모델로의 통합(5편)이라는 궤적의 마지막 칸이다.

물론 이 통합이 이야기의 끝은 아니다. 이 논문 이후 언어 모델의 무게중심은 정적 벡터에서 **문맥적 임베딩**(BERT류)으로 옮겨갔고, 시간축 연구도 그 위에서 다시 쓰인다. 예컨대 Hofmann et al.(ACL 2021)의 dynamic contextualized word embeddings는 문맥적 표현에 시간(과 사회적 맥락)을 함께 조건화한다. 이 시리즈가 다룬 정적 시대의 마지막 문장이, 문맥적 시대의 첫 문장으로 이어지는 다리인 셈이다.

## 한계와 비판

Dynamic Bernoulli Embeddings의 우아함은 동시에 몇 가지 대가를 치른다.

- **ρ와 α의 중복.** 저자들 스스로 인정하는 가장 큰 한계다. 단어 벡터 ρ와 context 벡터 α는 오직 **내적으로만** natural parameter에 등장하기 때문에, 둘 모두에 dynamics를 거는 것은 표현상 중복이 된다. 이 논문은 ρ에만 시간을 넣고 α는 고정했는데, α의 dynamics를 어떻게 다룰지는 미래 연구로 남겨두었다. 3편이 양쪽 모두를 움직인 것과 대조적인 설계 선택이다.
- **pseudo-likelihood의 이론적 느슨함.** 조건부로 명세된 모델은 일반적으로 일관된 결합분포를 보장하지 않는다. 저자들은 이진 데이터에 한해 유효한 결합이 존재함을 인용으로 정당화하지만, 이는 모델 클래스에 붙는 근본적 제약이다.
- **negative sampling의 편향.** 0인 항 전체를 더하는 대신 표본만 쓰는 negative sampling은 계산을 줄이지만, 그 기댓값이 원래 목적함수와 같지 않아 **편향**이 생긴다. 저자들은 "0을 낮춰 잡는(downweighting the zeros)" 것이 오히려 예측 정확도를 높인다고 방어하지만, 이는 실용적 절충이지 이론적 무결성은 아니다.
- **불확실성의 부재.** 점 추정(pseudo MAP)이라 각 시점 단어 벡터의 사후 불확실성을 내놓지 않는다. "이 단어의 변화가 통계적으로 유의한가"를 묻기에는 3편의 변분 사후분포가 더 적합하다.
- **평가의 대리 지표 성격.** held-out likelihood는 언어 모델링 성능을 재지, "포착된 의미 변화가 언어학적으로 옳은가"를 직접 재지 않는다. 정성 사례(computer, iraq)는 설득력 있지만 체리피킹의 여지가 있고, 대규모 정량 검증(예: 역사 사전과의 대조)은 이 논문의 범위 밖이다.

## 집현전에 주는 힌트

집현전이 다루는 논문 코퍼스는 그 자체로 **시간이 흐르는 텍스트**다. `attention`, `agent`, `alignment` 같은 단어의 의미는 2015년과 2025년 사이에 크게 이동했다. 이 논문은 그런 코퍼스를 다룰 때 두 가지 설계 지침을 준다.

첫째, **좌표계를 통일하라.** 연도별로 논문 임베딩을 따로 만들어 "2018년의 transformer"와 "2024년의 transformer"를 비교하려 들면, 정렬이라는 골칫거리를 스스로 불러온다. 대신 시점들을 하나의 생성 과정으로 묶으면(공유되는 축 + 부드러운 드리프트), "이 개념이 어떻게 흘러왔는가"를 별도 정렬 없이 바로 물을 수 있다. 검색·관련논문·트렌드 분석에서 시간축을 다룰 때 기본으로 삼을 만한 관점이다.

둘째, **드리프트를 제품 기능으로 노출하라.** 절대 드리프트 순위(iraq 3.09처럼)는 "이 분야에서 지난 10년간 가장 의미가 크게 바뀐 개념" 같은 큐레이션을 그대로 만들어낸다. 단어의 임베딩 이웃을 시점별로 나열하는 방식(computer: 직업 → 기기)은, 사용자가 특정 용어의 역사를 한눈에 훑게 하는 훌륭한 탐색 UI가 된다. 집현전의 커리큘럼·다이제스트 에이전트가 "이 개념의 궤적"을 보여줄 때 바로 쓸 수 있는 패턴이다.

## 읽을 때 가져갈 것

Dynamic Bernoulli Embeddings가 남기는 가장 실용적인 교훈은 정렬에 관한 것이다.

> 정렬은 사후에 푸는 문제가 아니라, 모델 가정으로 흡수해 애초에 발생하지 않게 만들 수 있는 문제다.

시간에 따라 변하는 무언가를 표현하려 할 때, 우리는 흔히 "먼저 각 시점을 따로 만든 뒤 맞추자"라고 생각한다. 이 논문은 반대 방향을 가리킨다. 공유되는 축을 하나 정하고(시간 불변 context), 나머지를 그 위에서 부드럽게 흐르게 하면(랜덤 워크), 맞출 것이 남지 않는다. 시간축을 다루는 어떤 표현 학습에서도 이 질문은 유효하다. 나는 지금 정렬을 사후에 풀고 있는가, 아니면 처음부터 필요 없게 설계하고 있는가.

---

### 메타

- 논문: [Dynamic Bernoulli Embeddings for Language Evolution](https://arxiv.org/abs/1703.08052)
- 저자: Maja Rudolph, David Blei (Columbia University)
- 학회: WWW 2018 (arXiv 1703.08052)
- 핵심 키워드: dynamic word embeddings, exponential family embeddings, Bernoulli embedding, Gaussian random walk prior, pseudo log-likelihood, alignment-free, language evolution

#DynamicWordEmbeddings #ExponentialFamilyEmbeddings #ProbabilisticModels #LanguageEvolution #PaperReview #Jiphyeonjeon
