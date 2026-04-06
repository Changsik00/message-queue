# Task: 2-001 - Kafka 구현 (Kafka MVP)

## 1. 사전 준비 (Setup & TDD Draft)
- [x] 브랜치 생성 완료 (`git checkout -b spec-2-001/kafka-impl`)
- [x] Python 의존성 추가 (`aiokafka`)
- [x] Node.js 의존성 추가 (`kafkajs`)

## 2. 세부 구현 (Implementation)
- [x] API Server (Python) `KafkaProducer` 구현 및 `orders` 토픽 발행 연동
- [x] Python Kafka Worker (`kafka_worker.py`) 구현
    - [x] `payment-group` 설정 및 메시지 핸들러 작성
    - [x] PostgreSQL DB 저장 로직 추가
- [x] Node.js Kafka Worker (`kafka.worker.ts`) 구현
    - [x] `inventory-group` 설정 및 메시지 핸들러 작성
    - [x] PostgreSQL DB 저장 로직 추가

## 3. 통합 및 검증 (Integration & Verification)
- [x] Docker Compose로 Kafka & PostgreSQL 환경 기동
- [x] `processed_events` 테이블 생성 (`schema.sql` 등 활용)
- [x] API 호출을 통해 `orders` 이벤트 발행
- [x] DB에 `payment-group`과 `inventory-group` 처리 로그가 각각 잘 쌓였는지 쿼리로 확인
- [x] 두 워커가 동시에 같은 메시지를 수신했는지 최종 검증

## 4. 리뷰 및 마무리 (Review & Wrap-up)
- [ ] 개발된 내용이 정상 동작하는지 Agent 차원의 자체 로컬 테스트 및 검증 (필수)
- [ ] 전체 기능 동작 확인 및 린팅(Linting) / 포맷팅(Formatting)
- [ ] `walkthrough.md` 업데이트
- [ ] `pr_description.md` 파일 작성
- [ ] `gh pr create`를 통한 PR 생성

