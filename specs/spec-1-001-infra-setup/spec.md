# Spec: 1-001 - 인프라 기반 구축 (Infra MVP)

## 1. 개요 (Overview)
- **목표**: 4종의 Message Queue (Kafka, RabbitMQ, BullMQ용 Redis, MQTT용 Mosquitto)와 DB (PostgreSQL) 환경을 로컬 Docker Compose 한 번으로 모두 띄워 연동 파이프라인의 뼈대를 준비합니다.
- **영향 범위**: 애플리케이션 코드는 작성하지 않으며, 전적으로 인프라 설정 파일(`.yml`, `.sql`)에 영향을 미칩니다.
- **관련 지표/이슈**: `backlog/phase1.md`의 Spec 1-001 참고

## 2. 상세 요구사항 (Requirements)
- [ ] `docker-compose.yml` 리소스 분배 및 포트 충돌 없이 작성
  - Kafka (Zookeeper 없는 KRaft 모드 우선) / RabbitMQ (Management UI 활성화) / Redis / Mosquitto
  - PostgreSQL 컨테이너 
- [ ] PostgreSQL `init.sql` 마운트를 통한 초기 테이블 자동 생성 (`orders`, `event_logs`)
- [ ] 컴포넌트별 헬스체크(healthcheck) 설정으로 정상 구동 명확화

## 3. 제약사항 및 비기능 요구사항
- 컨테이너 간 통신 및 호스트 PC 포워딩 포트가 명확히 분리되고 충돌이 없어야 함.
- 애플리케이션 프레임워크 뼈대는 이번 Spec에는 포함하지 않음 (Infra Only).

## 4. 인수 조건 (Acceptance Criteria)
> PR이 승인되기 위해 반드시 충족되어야 하는 시나리오를 기술합니다.

- **Scenario 1**: 로컬 개발망 클린 환경 가동
  - **Given**: 아무 Docker 컨테이너도 띄워지지 않은 클린 상태에서
  - **When**: 터미널에 `docker compose up -d` 를 실행하면
  - **Then**: 모든 컨테이너가 `healthy` 상태에 도달하고 로컬 환경(호스트) 포트 매핑으로 PostgreSQL(5432) 및 RabbitMQ UI(15672) 등 접속이 가능해야 한다.

## 5. 참고 자료 (References)
- Kafka 3.x KRaft 실행 설정 가이드
- Docker PostgreSQL 초기 테이블 생성 바인드 마운트 방식 가이드
