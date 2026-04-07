# Task: 2-002 - 아키텍처 표준화 및 기록 (Standardization)

> 이 문서는 구현을 위한 워크로드입니다.
> **문서화 단계(Phase A)** 에서 이 문서가 확정되고 사용자의 승인이 떨어지면, **코딩 단계(Phase B)** 로 넘어갑니다.
> 코딩 단계 진입 후에는 **사용자의 허락을 구하지 말고 자율적으로 끝까지 진행**하며, `[ ]` 항목 하나를 `[x]`로 완료할 때마다 **반드시 1번의 git commit**을 수행하세요.

## 1. 사전 준비 (Setup)
- [x] 브랜치 생성 (`git checkout -b spec-2-002/standardization`)
- [x] `.gitignore` 업데이트 (alembic 캐시, __pycache__ 등 누락 항목 확인)

## 2. pnpm workspace 모노레포 구성
- [x] 루트에 `pnpm-workspace.yaml` 생성 및 `tsconfig.base.json` 배치
- [x] `packages/shared-node/` 패키지 생성 (`package.json`, `tsconfig.json`, `src/types.ts`, `src/base-queue.interface.ts`, `src/index.ts`)
- [x] `api-server/node`와 `workers/node`에서 `shared-node`를 workspace 의존성으로 연결 및 import 경로 변경
- [x] `pnpm install` 후 전체 TypeScript 빌드 성공 확인

## 3. Python 공통 모델 통합
- [x] `packages/shared-python/` 생성 및 `models.py`(SQLModel), `schemas.py`(Pydantic OrderEvent) 배치
- [x] `api-server/python`과 `workers/python`의 import를 공통 패키지로 전환
- [x] Python import 경로 변경 후 기존 코드 정상 동작 확인

## 4. Alembic DB 마이그레이션 도입
- [x] `db/alembic/` 에 Alembic 환경 구성 (`alembic.ini`, `env.py`)
- [x] `init.sql` 내용을 초기 마이그레이션(`001_initial_schema`)으로 변환
- [x] `processed_events` 테이블 포함한 마이그레이션 반영
- [x] `docker-compose.yml` DB 초기화 방식 전환 및 `alembic upgrade head` 동작 확인

## 5. Node.js DB 접근 개선
- [x] Node.js DB 접근 전략 결정 및 적용 (타입화된 쿼리 헬퍼 패턴)
- [x] `workers/node/src/kafka.worker.ts`의 raw SQL을 새 패턴으로 리팩토링

## 6. ADR 문서 작성
- [x] `adr-004-pnpm-workspace.md` 작성
- [x] `adr-005-node-db-access.md` 작성
- [x] `adr-006-alembic-migration.md` 작성

## 7. 리뷰 및 마무리 (Review & Wrap-up)
- [x] 개발된 내용이 정상 동작하는지 Agent 차원의 자체 로컬 테스트 및 검증 (필수)
- [x] 전체 기능 동작 확인 및 린팅(Linting) / 포맷팅(Formatting)
- [x] `walkthrough.md` 구조, 에러 로그 및 아키텍처 다이어그램(Mermaid) 최종 점검 및 업데이트
- [x] `pr_description.md` 파일 작성 (해당 스펙 폴더 내)
- [x] `git push` 후, `gh pr create --title ... --body-file pr_description.md` 로 PR 생성
