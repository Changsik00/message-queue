# ADR-004: pnpm workspace 모노레포 구성

- **Status**: Accepted
- **Date**: 2026-04-06
- **Deciders**: 개발팀

## Context

`api-server/node`와 `workers/node`는 `OrderEvent`, `BaseQueue` 같은 공통 타입/인터페이스를 각자 정의하거나 상대 경로로 직접 참조하고 있었다. RabbitMQ, BullMQ, MQTT 등 후속 MQ 구현이 추가될수록 타입 불일치와 경로 관리 부담이 증가할 수밖에 없는 구조였다.

## Decision

프로젝트 루트에 `pnpm-workspace.yaml`을 추가하여 `api-server/node`, `workers/node`, `packages/*`를 단일 workspace로 묶는다. 공통 타입과 인터페이스는 `packages/shared-node`(`@mq/shared-node`)로 추출하고, 각 패키지는 `workspace:*` 프로토콜로 이 패키지에 의존한다. TypeScript 컴파일러 옵션은 루트 `tsconfig.base.json`으로 통합하여 각 패키지에서 `extends`로 상속한다.

## Consequences

**긍정:**
- 공통 타입이 단일 소스에서 관리되므로 타입 불일치 위험이 제거됨
- 새 MQ 구현 패키지 추가 시 `pnpm-workspace.yaml`에 경로만 등록하면 공통 타입을 즉시 사용 가능
- `pnpm install`이 루트에서 한 번으로 모든 패키지 의존성을 관리

**부정/트레이드오프:**
- 루트 `package.json` 추가로 기존 단독 실행 방식을 쓰던 개발자는 workspace 개념을 숙지해야 함
- Node.js ESM(`"type": "module"`)과 TypeScript `moduleResolution: nodenext`의 엄격한 조합에서 `.js` 확장자 관리를 주의해야 함

## Alternatives Considered

- **npm workspaces**: pnpm 대비 hoist 동작 차이로 인해 기존 pnpm 사용 이력(ADR-001)과 일관성을 위해 기각
- **경로 별칭(tsconfig paths)**: 실제 심링크 없이 컴파일 타임만 해결되어 런타임 import 오류 위험이 있어 기각
