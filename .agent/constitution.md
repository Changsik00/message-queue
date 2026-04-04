# Agent Constitution (에이전트 절대 행동 규칙)

이 문서는 프로젝트 진행 시 AI Agent가 **반드시 복종**해야 하는 핵심 원칙을 담고 있습니다. 환경이나 Context Window의 상태와 무관하게 항상 우선순위 1순위로 지켜져야 합니다.

## 1. 단계 분리의 원칙 (Docs before Code)
스펙주도개발(SDD)의 핵심은 코딩 전 설계입니다.
- **문서화 단계**: `spec.md`, `plan.md`, `task.md`를 작성하고 **사용자의 명시적 허가**를 얻기 전에는 절대 소스 코드를 생성하거나 수정하지 않습니다.
- **코딩 단계**: 사용자의 허가가 떨어지면, 그때부터는 사용자에게 멈춰서 질문하지 않고 `task.md`의 체크리스트를 따라 자율적(Autonomous)으로 끝까지 코딩하고 커밋합니다.

## 2. 1 Checkbox = 1 Commit 원칙 (Micro Committing)
`task.md`의 체크박스 항목 1개가 오롯이 한 번의 commit에 해당하도록 작업합니다.
- 코딩 페이즈에서는 체크박스 하나를 완료할 때마다 커밋을 진행합니다.
- **Commit Message Convention:** `type(spec-XXX): description` 포맷을 따릅니다.
  (예: `feat(spec-001): initialize docker compose for rabbitmq`)

## 3. TDD (Test-Driven Development) 원칙
기능 코드를 작성하기 전에 테스트 구조를 먼저 설계/작성해야 합니다.
1. 유닛(Unit) 단위 테스트 작성 (실패 확인)
2. 기능 구현 (통과 확인)
3. 해당 스펙 완성 후, 마지막으로 통합(Integration) 테스트 시도

## 4. 단일 터미널 원칙
터미널은 충돌 및 병렬 실행 문제를 방지하기 위해 **오직 하나만 사용**합니다.

## 5. 투명한 상태 기록 (Walkthrough) 원칙
작업 도중 마주친 **에러, 추론 과정, 아키텍처 결정 사항**은 즉시 해당 스펙 디렉토리의 `walkthrough.md`에 추가 기록해야 합니다.
복잡한 흐름, 상태 전이, 테스트 시나리오는 반드시 **Mermaid 구문(Graph/Sequence 등)** 으로 시각화하여 사용자가 나중에 문서를 읽었을 때 AI의 생각 경로를 완벽히 이해할 수 있게 하세요.