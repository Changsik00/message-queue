# ADR-006: Alembic DB 마이그레이션 도입

- **Status**: Accepted
- **Date**: 2026-04-06
- **Deciders**: 개발팀

## Context

초기 DB 스키마는 `db/init.sql`로 관리되었다. Docker가 컨테이너를 처음 시작할 때 이 파일을 실행하는 방식으로, 스키마 변경이 필요할 때마다 컨테이너를 재생성하거나 수동 ALTER를 실행해야 했다. Spec 2-001에서 `processed_events` 테이블이 추가되면서 이 방식의 한계가 명확해졌다. 후속 MQ 구현에서도 스키마 변경이 반복될 것이 예상되어 코드로 관리되는 마이그레이션 시스템이 필요했다.

## Decision

Python 생태계의 표준 마이그레이션 도구인 **Alembic**을 `db/alembic/` 경로에 도입한다. `env.py`는 `packages/shared_python`의 `SQLModel` 메타데이터를 바인딩하여 autogenerate를 지원하도록 구성한다. `db/init.sql` 내용은 `001_initial_schema.py`로 변환되고, docker-compose에서 init.sql 볼륨 마운트를 제거한다. DB 초기화 절차는 `docker-compose up -d && alembic upgrade head`로 통일한다.

## Consequences

**긍정:**
- 스키마 변경이 버전 관리되는 Python 파일로 기록되어 히스토리 추적 가능
- `alembic downgrade` 로 롤백 가능
- `--autogenerate` 옵션으로 SQLModel 모델 변경을 자동으로 감지하여 마이그레이션 파일 초안 생성
- `DATABASE_URL` 환경변수로 local/staging/prod 연결을 동적으로 전환 가능

**부정/트레이드오프:**
- DB 초기화 시 컨테이너 기동 후 별도로 `alembic upgrade head`를 실행해야 함 (자동 실행 아님)
- Alembic 의존성(`alembic`, `SQLAlchemy`)이 `api-server/python/requirements.txt`에 추가됨

## Alternatives Considered

- **init.sql 유지**: 단순하지만 변경 이력 관리가 불가능하고 롤백이 없어 기각
- **SQLModel `create_all()`**: 개발 환경에서 편리하지만 운영 환경에서 스키마 변경을 추적할 수 없어 기각
- **Flyway**: JVM 기반으로 Python 프로젝트와 생태계가 맞지 않아 기각
