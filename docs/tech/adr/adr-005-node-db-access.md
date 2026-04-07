# ADR-005: Node.js DB 접근 전략

- **Status**: Accepted
- **Date**: 2026-04-06
- **Deciders**: 개발팀

## Context

`workers/node/src/kafka.worker.ts`는 `pg` 클라이언트를 이용한 raw SQL로 `processed_events`에 이벤트를 저장하고 있었다. 컬럼 이름이 문자열로 하드코딩되어 타입 안전성이 없었고, Python 측의 `ProcessedEvent` SQLModel과 스키마 불일치가 생겨도 컴파일 시점에 감지할 수 없었다.

## Decision

Prisma, Drizzle 같은 별도 ORM/쿼리빌더를 도입하는 대신, `@mq/shared-node`에 정의된 `ProcessedEvent` 타입을 활용한 **타입화된 쿼리 헬퍼 함수** 패턴을 적용한다. `insertProcessedEvent(client, event: Omit<ProcessedEvent, 'id' | 'processedAt'>)` 함수가 파라미터 바인딩을 담당하며, 호출부는 타입이 보장된 객체 리터럴만 전달한다.

이 결정은 현재 단계(Kafka 단일 MQ)에서의 최소 복잡도를 유지하기 위한 것으로, 후속 MQ 구현에서 DB 접근 복잡도가 증가하면 Drizzle ORM 도입을 재검토한다.

## Consequences

**긍정:**
- `ProcessedEvent` 타입과 실제 SQL 파라미터 매핑이 함수 내부에 캡슐화되어 변경 시 단일 지점만 수정
- Prisma, Drizzle 대비 추가 의존성 없음 — 현재 `pg` 클라이언트만으로 충분
- TypeScript strict 모드에서 컴파일 타임 타입 검사 적용

**부정/트레이드오프:**
- raw SQL이 완전히 제거되지 않으므로 스키마 변경 시 SQL과 타입을 동시에 수정해야 함
- migration 시 column 추가/제거가 발생하면 헬퍼 함수도 함께 업데이트 필요

## Alternatives Considered

- **Prisma**: 자동 타입 생성과 강력한 migration 도구를 제공하지만 CLI 기반 schema-first 워크플로가 현재 프로젝트 규모 대비 오버스펙
- **Drizzle ORM**: TypeScript-first이고 경량이지만 지금 단계에서 새 의존성을 추가하는 것은 표준화 스펙의 범위를 벗어남
