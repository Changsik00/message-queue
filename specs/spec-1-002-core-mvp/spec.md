# Spec: 1-002 - 애플리케이션 코어 및 공통 인터페이스 설계 (Core MVP)

## 1. 개요 (Overview)
- **목표**: 향후 4가지 MQ 구현 시 비즈니스 로직 수정을 최소화하기 위한 '공통 뼈대(Interface)'와 데이터 규격(Schema)을 확정. 실제 Message Queue 대신 기초적인 API 서버가 주문을 처리할 뼈대를 마련.
- **영향 범위**: Python FastAPI, Node.js Express API 서버 및 Worker 추상화
- **관련 지표/이슈**: [Phase 1 Backlog](../../backlog/phase1.md)

## 2. 상세 요구사항 (Requirements)
- [ ] **이벤트 스키마 정의**: Latency 측정을 위해 `publishedAt`을 포함한 `OrderEvent` 데이터 모델 작성 (Python Pydantic, TS Interface)
- [ ] **추상화 인터페이스**: `base_queue` 기초 설계 (`connect`, `publish`, `consume` 등)
- [ ] **API 서버 & Worker 뼈대**: HTTP POST `/orders`를 받아 이벤트를 생성하고, Worker가 수신하는 Mock 파이프라인 작성
- [ ] **검증**: 기본 API 서버 구동 및 HTTP 요청 처리에 대한 기초 확인

## 3. 제약사항 및 비기능 요구사항
- Python(FastAPI) 및 Node.js(Express) 환경 모두 구현
- 향후 어떤 MQ (Kafka, RabbitMQ, BullMQ, MQTT) 모듈을 장착해도 어댑터 패턴으로 호환되도록 설계

## 4. 인수 조건 (Acceptance Criteria)
- **Scenario 1**: API를 통해 주문 데이터 수신 및 Mock 처리 확인
  - **Given**: FastAPI/Express 서버가 실행 중이다
  - **When**: 클라이언트가 `POST /orders` 요청을 보낸다
  - **Then**: 서버는 `OrderEvent` 객체를 생성하고 타임스탬프(`publishedAt`)를 포함하여 Mock Worker로 전달, 콘솔에서 양측 출력이 확인된다.

## 5. 참고 자료 (References)
- `db/init.sql` (이전 스펙에서 작성)
