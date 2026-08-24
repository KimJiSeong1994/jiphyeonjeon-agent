# Google DeepMind 연구 흐름: 1K Papers에서 고른 세 편의 논문

**Google DeepMind 연구 시리즈**는 장시간 3D reconstruction, diffusion latent 설계, 생성형 비디오의 zero-shot vision capability라는 세 축으로 공간·표현·세계 모델 연구를 읽는 로컬 편집 묶음이다.

**TL;DR** — Google DeepMind 묶음은 긴 video stream의 geometry, 생성 모델의 latent bottleneck, video generation에서 나타나는 vision capability를 연결한다. 선정은 결정론적 후보 pool에서 직접 Google DeepMind 귀속과 안정된 arXiv 식별자를 확인한 항목으로 제한했다. LoGeR, Unified Latents, Video models 순서로 읽으면 input horizon, representation, emergent capability의 연결이 드러난다.

## 선정 기준과 읽기 순서

1. [LoGeR 리뷰](paper-01.md)는 local SWA와 global TTT memory로 장시간 3D reconstruction을 확장한다.
2. [Unified Latents 리뷰](paper-02.md)는 diffusion prior와 decoder 사이의 latent bitrate trade-off를 설명한다.
3. [Video models 리뷰](paper-03.md)는 생성형 비디오 모델의 zero-shot 시각 과제를 통해 일반 목적 표현 가능성을 살핀다.

1K Papers는 발견 경로일 뿐 기술 주장이나 회사 귀속의 단독 근거로 사용하지 않았다. 각 리뷰의 메타데이터와 주장은 arXiv 및 Google 공식 연구 페이지에 연결했다.

## References

Zhang, J., Herrmann, C., Hur, J., Sun, C., Yang, M.-H., Cole, F., Darrell, T., & Sun, D. (2026). *LoGeR: Long-Context Geometric Reconstruction with Hybrid Memory*. arXiv:2603.03269. https://arxiv.org/abs/2603.03269

Heek, J., Hoogeboom, E., Mensink, T., & Salimans, T. (2026). *Unified Latents (UL): How to train your latents*. arXiv:2602.17270. https://arxiv.org/abs/2602.17270

Wiedemer, T., Li, Y., Vicol, P., Gu, S. S., Matarese, N., Swersky, K., Kim, B., Jaini, P., & Geirhos, R. (2025). *Video models are zero-shot learners and reasoners*. arXiv:2509.20328. https://arxiv.org/abs/2509.20328
