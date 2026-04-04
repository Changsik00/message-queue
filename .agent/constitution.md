# Agent Constitution (에이전트 절대 행동 규칙)

이 문서는 프로젝트 진행 시 AI Agent가 **반드시 복종**해야 하는 핵심 원칙 5가지를 담고 있습니다. 환경이나 Context Window의 상태와 무관하게 항상 우선순위 1순위로 지켜져야 합니다.

## 1. SDD (Specification-Driven Development) 원칙
모든 코드는 정의된 스펙(`specs/spec-XXX/spec.md`)에 근거하여 작성되어야 합니다.
스펙 외의 임의의 피쳐 추가나 과도한 확장은 금지됩니다. (설계나 설명이 필요하다면 반드시 Mermaid Graph를 적극 활용해 디테일하게 설명하세요.)

## 2. TDD (Test-Driven Development) 원칙
기능 코드를 작성하기 전에 테스트 구조를 먼저 설계해야 합니다.
1. 유닛(Unit) 단위 테스트 작성 시도
2. 기능 구현
3. 스펙 전체 완료 전, 통합(Integration) 테스트 시도

## 3. 1 Checkbox = 1 Commit 원칙 (Micro Committing)
`task.md`의 체크박스 항목 1개가 오롯이 한 번의 commit에 해당하도록 작업합니다.
작업을 병합해서 커밋하지 마세요.

**Commit Message Convention:**
반드시 `type(spec-XXX): description` 포맷을 따릅니다.
- 예: `feat(spec-001): initialize docker compose for rabbitmq`
- 예: `test(spec-002): add unit tests for parsing order event`

## 4. 단일 터미널 원칙
**터미널은 오직 하나만 사용합니다.**
`run_command` 도구를 여러 개 병렬로 실행하지 마세요. Background나 async로 넘기더라도 기존 실행 중인 커맨드의 `command_status`를 모두 확인하고 종료/대기 상태가 정리된 후에만 다음 커맨드를 실행하세요.

## 5. 투명한 상태 기록 (Walkthrough) 원칙
작업 도중 마주친 **에러, 추론 과정, 아키텍처 결정 사항(Mermaid Graph 포함)** 은 즉시 해당 스펙 디렉토리의 `walkthrough.md`에 추가로 기록해야 합니다.
사용자가 당신의 의식의 흐름과 발생했던 문제를 모두 추적할 수 있어야 합니다.
복잡한 흐름, 상태 전이, 아키텍처는 말로만 쓰지 말고 반드시 **Mermaid 구문(Graph/Sequence 등)으로 표현**하세요.