# Task: 2-003 - RabbitMQ 구현 (RabbitMQ MVP)

> 이 문서는 구현을 위한 워크로드입니다.
> **문서화 단계(Phase A)** 에서 이 문서가 확정되고 사용자의 승인이 떨어지면, **코딩 단계(Phase B)** 로 넘어갑니다.
> 코딩 단계 진입 후에는 **사용자의 허락을 구하지 말고 자율적으로 끝까지 진행**하며, `[ ]` 항목 하나를 `[x]`로 완료할 때마다 **반드시 1번의 git commit**을 수행하세요.

## 1. 사전 준비 (Setup)
- [x] 브랜치 생성 (`git checkout -b spec-2-003/rabbitmq-impl`)
- [x] Python 의존성 추가 (`aio-pika` → `api-server/python/requirements.txt`, `workers/python/requirements.txt`)
- [x] Node.js 의존성 추가 (`amqplib`, `@types/amqplib` → `workers/node/package.json`, `pnpm install`)

## 2. Producer 구현 (API Server)
- [x] `api-server/python/main.py` — `RabbitMQQueue` 클래스 구현 및 `POST /rabbitmq/orders` 엔드포인트 추가
  - `orders` Exchange (`direct` 타입) 선언
  - `orders.queue` + DLQ 설정 (`x-dead-letter-exchange`) 선언
  - `order.created` Routing Key로 메시지 발행

## 3. Python Worker 구현
- [x] `workers/python/rabbitmq_worker.py` 파일 생성
  - `aio-pika` 기반 비동기 Consumer 구현
  - Prefetch count=1, 수동 ack/nack 로직
  - `SIMULATE_FAILURE` 환경변수 기반 50% 강제 실패 로직 추가
  - 정상 처리 시 `processed_events` DB 저장 (`mq_type='rabbitmq'`, `group_id='payment-group'`)

## 4. Node.js Worker 구현
- [x] `workers/node/src/rabbitmq.worker.ts` 파일 생성
  - `amqplib` 기반 Consumer 구현
  - Prefetch count=1, 수동 ack/nack 로직
  - 정상 처리 시 `processed_events` DB 저장 (`mq_type='rabbitmq'`, `group_id='inventory-group'`)

## 5. 통합 및 검증 (Integration & Verification)
- [ ] `docker compose up postgres rabbitmq -d` 로 인프라 기동 확인
- [ ] Python Worker, Node.js Worker 동시 실행 후 `POST /rabbitmq/orders` 5회 호출
- [ ] DB에서 `mq_type='rabbitmq'` 레코드 조회 — 각 메시지가 하나의 워커에만 처리됐는지 확인
- [ ] `SIMULATE_FAILURE=true` Python 워커 실행 후 메시지 발행 → RabbitMQ UI `dead-letter.queue` 적재 확인

## 6. 리뷰 및 마무리 (Review & Wrap-up)
- [ ] 개발된 내용이 정상 동작하는지 Agent 차원의 자체 로컬 테스트 및 검증 (필수)
- [ ] 전체 기능 동작 확인 및 린팅(Linting) / 포맷팅(Formatting)
- [ ] `walkthrough.md` 작성 (아키텍처 다이어그램, 검증 결과 포함)
- [ ] `pr_description.md` 파일 작성
- [ ] `git push` 후, `gh pr create --title "feat: Spec 2-003 RabbitMQ MVP 구현" --body-file pr_description.md` 로 PR 생성
