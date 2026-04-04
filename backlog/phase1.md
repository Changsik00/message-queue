# Phase 1 — 환경 세팅 & 아키텍처 이해

> **기간**: Week 1 | **상태**: 🔲 대기

---

## 🎯 이 Phase의 목적

코드를 한 줄도 짜기 전에 **"무엇을 비교하려고 하는지"** 를 명확히 구조화한다.

MQ를 처음 배울 때 흔히 하는 실수는 바로 Kafka Tutorial 따라가기, RabbitMQ Quick Start 하기처럼
각각의 기술을 분리해서 학습하는 것이다.
이 프로젝트는 다르다. **하나의 비즈니스 시나리오**를 설정하고,
그 시나리오를 4종의 MQ로 각각 구현해서 **직접 차이를 체감**하는 것이 목표다.

따라서 Phase 1에서 가장 중요한 것은 두 가지다.
1. 비교의 기준이 되는 **공통 시나리오와 이벤트 스키마**를 먼저 정의한다
2. 모든 MQ를 한 번에 실행할 수 있는 **Docker 환경**을 세팅한다

---

## 🧠 배경 지식 — 왜 "이커머스 주문 파이프라인"인가?

이 시나리오를 선택한 이유:

| 이유 | 설명 |
|---|---|
| **현실적** | 실제 서비스에서 가장 흔히 MQ를 사용하는 패턴 |
| **비교 포인트가 잘 드러남** | 결제(유실 불가) vs 로그(재처리 필요) vs 알림(단순 Job) 모두 포함 |
| **복잡도 적당** | 너무 단순하면 차이 안 보이고, 너무 복잡하면 MQ 외 요소가 개입됨 |
| **확장 가능** | 나중에 Saga 패턴, DLQ, Webhook 시나리오로 확장하기 쉬움 |

### 전체 플로우

```
[클라이언트]
    │
    ▼ HTTP POST /orders  (주문 생성 요청)
[API 서버]  ← Python(FastAPI) 또는 Node.js(Express) 둘 다 구현
    │
    ▼ publish(OrderEvent)  (이벤트 발행 — MQ로 전달)
[Message Queue]  ← 여기에 Kafka / RabbitMQ / BullMQ / MQTT 를 각각 교체
    │
    ├──▶ [결제 Worker]    → 결제 승인 처리  (DB에 결제 결과 저장)
    ├──▶ [재고 Worker]    → 재고 차감       (DB에 재고 수량 업데이트)
    └──▶ [알림 Worker]    → 이메일 발송     (외부 알림 시뮬레이션)
              │
              ▼
        [PostgreSQL]
```

**핵심 포인트**: API 서버와 Worker 코드는 동일하고, **MQ 부분만 교체**된다.
이것이 가능하려면 공통 인터페이스 추상화가 필요하다 → Task 4에서 구현.

---

## 🤔 비교할 핵심 질문들 (Phase 2~4에서 답을 찾을 것)

Phase 1을 마친 후, 이 질문들에 대한 답을 데이터로 찾아갈 것이다.

1. **처리량**: 초당 1만 건의 주문 이벤트가 들어올 때 어떤 MQ가 버티는가?
2. **지연시간**: 주문 생성 후 Worker가 이벤트를 받기까지 얼마나 걸리는가?
3. **유실 방어**: Worker가 처리 도중 죽으면 그 주문은 어떻게 되는가?
4. **재처리**: 결제 Worker에 버그가 있었던 걸 발견했다. 과거 이벤트를 다시 처리할 수 있는가?
5. **순서 보장**: 같은 주문에 대한 "생성 → 결제 → 완료" 이벤트가 순서대로 처리되는가?
6. **트랜잭션**: 결제는 성공했는데 재고 차감이 실패하면 어떻게 처리하는가?

---

## ✅ Task 목록

### 🐳 Task 1. Docker Compose 인프라 구성

**왜 Docker 인가?**
4종의 MQ를 로컬에 직접 설치하면 포트 충돌, 버전 이슈, 설정 파일 관리가 복잡해진다.
Docker Compose를 쓰면 `docker-compose up -d` 한 줄로 전체 환경을 띄우고,
실험 후 `docker-compose down`으로 깔끔하게 정리할 수 있다.

- [ ] `docker-compose.yml` 작성
  - [ ] **Kafka** — KRaft 모드 (Zookeeper 없이 단독 실행)
    - 포트: `9092`
    - KRaft 모드를 쓰는 이유: Kafka 3.x부터 Zookeeper 의존성 제거, 운영 단순화
  - [ ] **RabbitMQ** — Management UI 포함
    - AMQP 포트: `5672`, Management UI: `15672`
    - UI에서 Queue/Exchange/Binding 상태를 시각적으로 확인 가능
  - [ ] **Redis** — BullMQ 백엔드
    - 포트: `6379`
    - BullMQ는 Redis를 Job 저장소로 사용
  - [ ] **Mosquitto** — MQTT Broker
    - 포트: `1883` (MQTT), `9001` (WebSocket)
  - [ ] **PostgreSQL** — 이벤트 처리 결과 저장
    - 포트: `5432`

- [ ] 각 서비스 헬스체크 추가 (컨테이너가 ready 상태인지 확인)
- [ ] `docker-compose up -d` → 모든 컨테이너 `healthy` 상태 확인

---

### 🗃️ Task 2. DB 스키마 설계

**왜 DB가 필요한가?**
MQ는 메시지를 전달하는 통로일 뿐이다.
"Worker가 실제로 처리했는가"를 확인하려면 처리 결과를 DB에 기록해야 한다.
이 DB가 있어야 "중복 처리됐는가", "유실됐는가"를 나중에 검증할 수 있다.

```sql
-- 주문 테이블 (API 서버에서 생성)
CREATE TABLE orders (
    order_id    UUID PRIMARY KEY,
    user_id     VARCHAR(100) NOT NULL,
    total_price INTEGER NOT NULL,
    status      VARCHAR(20) DEFAULT 'PENDING',  -- PENDING | SUCCESS | FAILED
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 이벤트 처리 로그 (Worker에서 처리할 때마다 기록)
-- → 중복 처리 검증, 유실 검증에 핵심적으로 사용
CREATE TABLE event_logs (
    id           SERIAL PRIMARY KEY,
    order_id     UUID NOT NULL,
    worker_type  VARCHAR(50) NOT NULL,  -- 'payment' | 'inventory' | 'notification'
    mq_type      VARCHAR(50) NOT NULL,  -- 'kafka' | 'rabbitmq' | 'bullmq' | 'mqtt'
    language     VARCHAR(20) NOT NULL,  -- 'python' | 'node'
    published_at TIMESTAMPTZ,           -- 이벤트 발행 시각
    consumed_at  TIMESTAMPTZ,           -- Worker 수신 시각
    latency_ms   INTEGER,               -- consumed_at - published_at (ms)
    status       VARCHAR(20),           -- 'SUCCESS' | 'FAILED'
    created_at   TIMESTAMPTZ DEFAULT NOW()
);
```

- [ ] `db/init.sql` 작성 (위 스키마 포함)
- [ ] Docker Compose에 init 스크립트 마운트 설정
- [ ] PostgreSQL 접속 확인 (`psql` 또는 DBeaver)

---

### 📐 Task 3. 공통 이벤트 스키마 정의

**왜 공통 스키마가 중요한가?**
4종의 MQ가 동일한 데이터로 동일한 처리를 해야 **"공정한 비교"** 가 가능하다.
스키마가 다르면 MQ의 성능 차이인지 데이터 구조 차이인지 알 수 없게 된다.

`publishedAt` 필드가 핵심이다. 이 타임스탬프를 이벤트에 포함해야
나중에 Worker가 수신했을 때 `consumed_at - publishedAt` 로 Latency를 측정할 수 있다.

```json
{
  "orderId": "550e8400-e29b-41d4-a716-446655440000",
  "userId": "user_001",
  "items": [
    { "productId": "SKU-A", "quantity": 2, "price": 5000 }
  ],
  "totalPrice": 10000,
  "status": "PENDING",
  "publishedAt": "2026-04-04T12:00:00.000Z",
  "createdAt": "2026-04-04T11:59:59.000Z"
}
```

- [ ] 위 스키마를 기준으로 Python Pydantic 모델 정의
  ```python
  # schemas/order_event.py
  from pydantic import BaseModel
  from datetime import datetime
  from uuid import UUID

  class OrderItem(BaseModel):
      product_id: str
      quantity: int
      price: int

  class OrderEvent(BaseModel):
      order_id: UUID
      user_id: str
      items: list[OrderItem]
      total_price: int
      status: str = "PENDING"
      published_at: datetime
      created_at: datetime
  ```
- [ ] Node.js TypeScript 인터페이스 정의
  ```typescript
  // types/order-event.ts
  export interface OrderItem {
    productId: string;
    quantity: number;
    price: number;
  }

  export interface OrderEvent {
    orderId: string;
    userId: string;
    items: OrderItem[];
    totalPrice: number;
    status: 'PENDING' | 'SUCCESS' | 'FAILED';
    publishedAt: string; // ISO8601
    createdAt: string;
  }
  ```

---

### 🏗️ Task 4. 공통 인터페이스 추상화 설계

**왜 추상화가 필요한가?**

MQ를 교체할 때마다 비즈니스 로직(Worker 처리 코드)을 바꾸면 안 된다.
MQ 교체 시 바뀌는 것은 **연결 방법**뿐이고, "이벤트 받으면 결제 처리한다"는 로직은 동일해야 한다.

이것이 현업에서도 중요한 설계 원칙이다.
인터페이스를 잘 설계해두면 나중에 "Kafka → SQS로 바꾸자"가 됐을 때 Worker 로직 수정 없이 연결 부분만 교체할 수 있다.

```
[Worker 비즈니스 로직]
        │ (인터페이스만 알면 됨)
        ▼
[IMessageQueue 추상 인터페이스]
        │
   ┌────┼────┬────┐
   ▼    ▼    ▼    ▼
Kafka RabbitMQ BullMQ MQTT
(각각의 구체 구현체)
```

- [ ] Python 추상 클래스 작성 (`workers/python/base_queue.py`)
  ```python
  from abc import ABC, abstractmethod
  from typing import Callable, Awaitable

  class BaseMessageQueue(ABC):

      @abstractmethod
      async def connect(self) -> None:
          """MQ 브로커에 연결"""

      @abstractmethod
      async def publish(self, topic: str, event: dict) -> None:
          """이벤트를 MQ에 발행 (publishedAt 자동 추가)"""

      @abstractmethod
      async def consume(self, topic: str, handler: Callable[[dict], Awaitable[None]]) -> None:
          """이벤트 수신 후 handler 실행 (consumed_at 자동 기록)"""

      @abstractmethod
      async def disconnect(self) -> None:
          """연결 종료"""
  ```

- [ ] Node.js TypeScript 인터페이스 작성 (`workers/node/base-queue.interface.ts`)
- [ ] Python API 서버 뼈대 (`api-server/python/main.py`)
  - `POST /orders` → OrderEvent 생성 → `queue.publish()` 호출
  - 어떤 MQ를 쓸지는 환경변수 `MQ_TYPE` 으로 결정
- [ ] Node.js API 서버 뼈대 (`api-server/node/src/main.ts`)

---

### 📚 Task 5. 아키텍처 문서 초안 작성

이 Task는 코드 작성이 아니라 **"내가 만드는 시스템을 문서로 설명하는 연습"** 이다.
문서를 쓰다 보면 내가 모호하게 이해하던 부분이 드러난다.

- [ ] **`docs/architecture/overview.md`**
  - 전체 시스템 플로우 ASCII 다이어그램
  - 각 컴포넌트(API, MQ, Worker, DB)의 역할 설명
  - "MQ를 왜 여기 두는가?" — API에서 직접 처리하면 안 되는 이유 설명
    > 예: `POST /orders`에서 결제 API까지 동기 호출하면?
    > → 결제 PG 응답 시간 3초 × 동시 요청 1000개 = 서버 폭발

- [ ] **`docs/architecture/event-schema.md`**
  - 이벤트 필드별 설명과 존재 이유
  - `publishedAt`이 왜 필요한지 (Latency 측정 목적)
  - Python / Node 타입 정의 코드 포함

- [ ] **`docs/architecture/infrastructure.md`**
  - Docker Compose 서비스별 설명
  - 포트 매핑표 (어느 포트로 어디에 접속하는지)
  - 각 MQ UI 접속 방법 (RabbitMQ Management, Kafka UI 등)

---

## 🔗 산출물 (Output)

| 파일 | 설명 |
|---|---|
| `docker-compose.yml` | 전체 MQ + DB 인프라 |
| `db/init.sql` | PostgreSQL 초기 스키마 |
| `api-server/python/main.py` | FastAPI 주문 API 뼈대 |
| `api-server/node/src/main.ts` | Node.js 주문 API 뼈대 |
| `workers/python/base_queue.py` | Python 공통 인터페이스 |
| `workers/node/base-queue.interface.ts` | Node.js 공통 인터페이스 |
| `docs/architecture/overview.md` | 시스템 아키텍처 개요 |
| `docs/architecture/event-schema.md` | 이벤트 스키마 설명 |
| `docs/architecture/infrastructure.md` | 인프라 구성 가이드 |

---

## 📝 이 Phase를 마치면 알 수 있는 것

- [ ] MQ가 없으면 이 구조가 왜 문제인지 설명할 수 있다
- [ ] 이벤트 스키마에서 `publishedAt`이 왜 필요한지 설명할 수 있다
- [ ] 공통 인터페이스 추상화가 왜 MQ 교체를 쉽게 만드는지 설명할 수 있다
- [ ] `docker-compose up -d`로 4종 MQ 모두 로컬에서 실행할 수 있다

---

*[← backlog 목록으로](./queue.md) | [Phase 2 →](./phase2.md)*
