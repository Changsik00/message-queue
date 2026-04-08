# PR Description: feat: Spec 2-003 RabbitMQ MVP 구현

## 주요 사항 (What's New)
- **Producer 구현**: API 서버(`main.py`)에 RabbitMQ용 프로듀서를 추가하고 `/rabbitmq/orders` 엔드포인트를 노출했습니다.
- **Python Consumer 작성**: `aio-pika` 기반으로 RabbitMQ 이벤트를 수신하고 영속화(`ProcessedEvent`)하는 워커를 추가했습니다.
- **Node.js Consumer 작성**: `amqplib` 기반으로 동일한 `orders.queue`에 바인딩하여 메시지를 처리하는 워커를 완성했습니다.
- **DLQ 및 수동 Ack 구성**: 실패한 메시지가 큐 내에서 자동으로 `dead-letter.exchange`로 전환되어 적재되는 사이클을 구성했습니다. `SIMULATE_FAILURE=true` 모드로 그 작동성을 검증할 수 있습니다.

## 작업 상세 내용 (Details)
1. `api-server/python/main.py`: `RabbitMQQueue` 클래스, `start`, `stop`, `publish_async` 라이프사이클 훅 완성
2. Python, Node.js 양쪽에서 모두 `direct` 라우팅과 `prefetch(1)` 전략 적용
3. `SIMULATE_FAILURE` 환경 변수를 사용한 의도적 에러 → 큐 레벨 Nack (`requeue=False`) → `dead-letter.queue` 흐름 개발
4. Kafka MVP (`spec-2-001`) 대비, Competing Consumers 특성에 따라 하나의 이벤트가 결제/재고 중 어느 한 워커그룹에서만 처리되는 **RabbitMQ Push 철학** 명확화.

## PR 체크리스트
- [x] Python & Node.js 의존성 패키지 명시
- [x] 수동 Ack/Nack 처리 로직
- [x] Dead Letter Queue 선언 및 바인딩
- [x] Agent 로컬 테스트 스크립트 작성 및 반영 내역 기록 완료
