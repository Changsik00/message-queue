## Summary

- **pnpm workspace 모노레포 구성**: 루트 `pnpm-workspace.yaml` + `tsconfig.base.json` 추가, `packages/shared-node(@mq/shared-node)`로 `OrderEvent`, `ProcessedEvent`, `BaseQueue` 공통 타입 추출 — `api-server/node`와 `workers/node`가 `workspace:*`로 의존
- **Python 공통 모델 통합**: `packages/shared_python/`에 `models.py`(SQLModel `ProcessedEvent`)와 `schemas.py`(Pydantic `OrderEvent` + `BaseQueue` ABC)를 배치, `api-server/python`·`workers/python` import 경로 전환
- **Alembic DB 마이그레이션 도입**: `db/alembic/` 환경 구성, `init.sql` → `001_initial_schema.py` 변환(`CREATE TABLE IF NOT EXISTS`로 멱등성 보장), `docker-compose.yml` init.sql 볼륨 제거
- **Node.js DB 접근 개선**: `insertProcessedEvent()` 타입화 헬퍼 함수 도입으로 `ProcessedEvent` 타입 기반 파라미터 바인딩
- **ADR 3종 추가**: adr-004(pnpm workspace), adr-005(Node.js DB 접근), adr-006(Alembic)

## Test plan

- [x] `pnpm install` — 4개 workspace 패키지 정상 인식 (`pnpm -r ls`)
- [x] TypeScript 빌드 — `shared-node`, `api-server/node`, `workers/node` 모두 `--noEmit` 에러 없음
- [x] Python OrderEvent 직렬화 — `shared_python.schemas.OrderEvent` 모델 검증 통과
- [x] Alembic 마이그레이션 — `alembic upgrade head` → `001 (head)`, `orders` / `event_logs` / `processed_events` 테이블 생성 확인 (`\dt` 검증)

## Breaking Changes

- `docker-compose.yml`에서 init.sql 볼륨 마운트 제거: 기존 빈 DB는 `alembic upgrade head` 실행 필요 (기존 데이터가 있는 DB는 IF NOT EXISTS로 안전하게 skip)
- `workers/node/src/base-queue.interface.ts`의 직접 import → `@mq/shared-node` import로 전환

🤖 Generated with [Claude Code](https://claude.com/claude-code)
