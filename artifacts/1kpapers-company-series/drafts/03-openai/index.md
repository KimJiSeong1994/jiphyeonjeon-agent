# OpenAI 연구 흐름: 1K Papers에서 고른 세 편의 논문

**OpenAI 연구 시리즈**는 지시 충돌, 실제 업무 평가, 환각의 통계적·평가적 원인을 하나의 신뢰성 문제로 연결한다.

**TL;DR** — OpenAI 묶음은 모델이 무엇을 따라야 하는지, 무엇을 할 수 있는지, 모를 때 어떻게 반응해야 하는지를 차례로 묻는다. 선정은 안정된 arXiv ID와 OpenAI 공식 연구 자료가 함께 있는 항목으로 제한했다. 데이터셋, benchmark, 평가 인센티브 순서로 읽으면 신뢰성의 서로 다른 층을 비교할 수 있다.

## 선정 기준과 읽기 순서

1. [IH-Challenge 리뷰](paper-01.md)는 상충하는 지시의 우선순위를 학습 데이터로 다룬다.
2. [GDPval 리뷰](paper-02.md)는 실제 직업의 산출물을 모델 평가 과제로 옮길 때 생기는 대표성 문제를 보여준다.
3. [Hallucination 리뷰](paper-03.md)는 정확도 중심 평가가 불확실성 표현보다 추측을 보상하는 구조를 분석한다.

1K Papers는 후보 발견에만 사용했고, 기술 주장과 회사 귀속은 arXiv 및 OpenAI 공식 자료로 검증했다.

## References

Guo, C., Ceron Uribe, J. F., Zhu, S., Choquette-Choo, C. A., Lin, S., Kandpal, N., Nasr, M., Pokorny, M., Toyer, S., Wang, M., Yu, Y., Beutel, A., & Xiao, K. (2026). *IH-Challenge: A Training Dataset to Improve Instruction Hierarchy on Frontier LLMs*. arXiv:2603.10521. https://arxiv.org/abs/2603.10521

Patwardhan, T., Dias, R., Proehl, E., Kim, G., Wang, M., Watkins, O., Posada Fishman, S., Aljubeh, M., Thacker, P., Fauconnet, L., Kim, N. S., Chao, P., Miserendino, S., Chabot, G., Li, D., Sharman, M., Barr, A., Glaese, A., & Tworek, J. (2025). *GDPval: Evaluating AI Model Performance on Real-World Economically Valuable Tasks*. arXiv:2510.04374. https://arxiv.org/abs/2510.04374

Kalai, A. T., Nachum, O., Vempala, S. S., & Zhang, E. (2025). *Why Language Models Hallucinate*. arXiv:2509.04664. https://arxiv.org/abs/2509.04664
