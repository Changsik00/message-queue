# Phase 2 — MQ별 구현 & 특징 이해

> **기간**: Week 2~3 | **상태**: 🔲 대기

---

## 🎯 이 Phase의 목적

4종의 MQ를 **동일한 시나리오로** 각각 구현하면서
각 MQ가 어떻게 동작하는지, 어떤 개념이 핵심인지 직접 체득한다.

단순히 "코드가 돌아가게 만드는 것"이 목적이 아니다.
각 MQ를 구현하면서 **"왜 이렇게 설계되었는가"** 를 이해하는 것이 목적이다.

---

## 🧠 배경 지식 — 4종 MQ가 근본적으로 다른 이유

MQ는 모두 "메시지를 전달한다"는 공통점이 있지만, 내부 철학이 완전히 다르다.
이 철학의 차이가 "어떤 상황에서 어떤 MQ를 쓰느냐"를 결정한다.

| MQ | 핵심 철학 | 비유 |
|---|---|---|
| **Kafka** | 메시지를 **로그**로 영구 저장한다. Consumer가 알아서 읽어간다. | 신문사 — 신문을 찍어두면 독자가 골라서 읽음 |
| **RabbitMQ** | Broker가 Consumer에게 **Push**한다. 소비되면 삭제된다. | 우체부 — 편지를 직접 배달, 수신 확인 받음 |
| **BullMQ** | 처리해야 할 **Job 목록**을 관리한다. 상태(대기/처리중/완료/실패)가 있다. | 작업 티켓 — 처리되면 완료 처리, 실패하면 재시도 |
| **MQTT** | **경량 pub/sub**. 브로커는 메시지를 저장하지 않는다. | 라디오 방송 — 듣고 있는 사람만 받음 |

이 철학 차이 때문에:
- Kafka는 "지난 주 이벤트를 다시 읽고 싶다"가 가능하고,
- RabbitMQ는 "이 메시지가 반드시 처리됐음을 확인하고 싶다"가 쉽고,
- BullMQ는 "이 Job을 3번 재시도하고 실패하면 관리자에게 알림"이 쉽고,
- MQTT는 "배터리 1% 남은 센서에서도 데이터를 보낼 수 있다"가 강점이다.

---

## 🔬 이 Phase에서 확인할 질문들

각 MQ를 구현하면서 아래 질문에 대한 답을 직접 확인할 것이다.

1. **Kafka**: Consumer Group이란 무엇인가? 같은 이벤트를 결제 Worker와 재고 Worker가 각각 독립적으로 처리할 수 있는가?
2. **RabbitMQ**: `ack` 와 `nack` 의 차이는 무엇인가? 처리 실패 시 DLQ로 어떻게 이동하는가?
3. **BullMQ**: Job의 상태 전환(`waiting → active → completed / failed`)은 어떻게 관찰하는가?
4. **MQTT**: QoS 0 / 1 / 2 가 각각 어떻게 다르게 동작하는가?
5. **공통**: Python과 Node.js에서 같은 MQ를 쓸 때 코드 구조가 어떻게 달라지는가?

---

## ✅ Task 목록

---

### ⚡ Task 1. Kafka 구현

#### 핵심 개념 먼저 이해하기

Kafka를 처음 만나면 용어가 낯설다. 구현 전에 아래 개념을 정리한다.

```
[Producer] → [Topic] → [Partition 0] → [Consumer Group A - Worker 1]
                     → [Partition 1] → [Consumer Group A - Worker 2]
                                     → [Consumer Group B - Worker 3] (독립 소비)
```

- **Topic**: 메시지가 쌓이는 카테고리. 우리 시나리오에서는 `orders` 토픽.
- **Partition**: Topic을 병렬 처리하기 위해 나눈 단위. Partition 수 = 최대 병렬 Consumer 수.
- **Offset**: 각 메시지의 위치 번호. Consumer가 "나는 여기까지 읽었다"를 기록.
- **Consumer Group**: 같은 토픽을 독립적으로 소비하는 Worker 집합.
  - `payment-group` (결제 Worker들) 과 `inventory-group` (재고 Worker들)이 **같은 이벤트를 각자** 처리 가능.
  - RabbitMQ와 결정적 차이: RabbitMQ는 하나의 Consumer만 메시지를 받음.

#### 구현할 시나리오

```
주문 이벤트 1,000개 발행
        │
        ▼ Kafka Topic: "orders" (Partition 3개)
        │
   ┌────┴────────────────────┐
   ▼                         ▼
Consumer Group: payment    Consumer Group: inventory
(결제 Workers × 3)          (재고 Workers × 3)
각자 독립적으로 전체 소비
```

→ **확인 포인트**: 결제 Worker와 재고 Worker가 정말 독립적으로 모든 이벤트를 각각 받는가?

#### Python (`workers/python/kafka_worker.py`)

- [ ] `aiokafka` 설치 (`pip install aiokafka`)
- [ ] `KafkaProducer` 구현
  - `orders` 토픽에 `OrderEvent` JSON 발행
  - `publishedAt` 타임스탬프 자동 추가
  - `key` 를 `orderId`로 설정 → 같은 주문은 같은 Partition으로 (순서 보장)
- [ ] `KafkaConsumer` 구현
  - Consumer Group: `payment-group`
  - 소비 후 `consumed_at` 기록 → `event_logs` DB에 저장
  - 처리 완료 후 offset commit (`enable.auto.commit = False` → 수동 commit)
- [ ] 정상 동작 확인: 메시지 10개 발행 → Consumer에서 10개 수신 로그 확인

#### Node.js (`workers/node/kafka.worker.ts`)

- [ ] `kafkajs` 설치 (`npm install kafkajs`)
- [ ] Producer 구현 (Python과 동일한 스키마로 발행)
- [ ] Consumer 구현 (Consumer Group: `payment-group-node`)
- [ ] Python Worker와 Node.js Worker가 **동시에 실행될 때** 처리 분배 방식 관찰

---

### 🐇 Task 2. RabbitMQ 구현

#### 핵심 개념 먼저 이해하기

RabbitMQ의 핵심은 **"메시지가 반드시 처리됐음을 보장하는 메커니즘"** 이다.

```
[Producer]
    │
    ▼ Exchange (라우팅 담당)
[Direct Exchange: order.exchange]
    │
    ├── Routing Key: payment  →  [Queue: payment.queue]  →  [결제 Worker]
    ├── Routing Key: inventory → [Queue: inventory.queue] → [재고 Worker]
    └── Routing Key: notify   →  [Queue: notify.queue]   →  [알림 Worker]
```

- **Exchange**: 메시지를 받아서 어떤 Queue로 보낼지 결정하는 라우터.
- **Queue**: 실제 메시지가 쌓이는 공간. Consumer가 여기서 꺼내감.
- **Binding**: Exchange와 Queue를 연결하는 규칙 (Routing Key 기준).
- **Ack / Nack**: 
  - `ack`: "처리 완료. 메시지 삭제해도 됨"
  - `nack`: "처리 실패. 다시 Queue로 돌려보내줌" → 재시도 또는 DLQ 이동
- **DLQ (Dead Letter Queue)**: 처리 실패한 메시지의 무덤. 운영팀이 원인 파악 후 수동 재처리.

```
정상 흐름:
Worker → [ack] → 브로커가 메시지 삭제

실패 흐름:
Worker → 예외 발생 → [nack] → 재시도 큐 (3회) → DLQ
                                    ↓ 재시도 횟수 초과
                              dead-letter.queue (운영팀 확인)
```

#### 구현할 시나리오

**시나리오 A — 정상 흐름**: 결제 Worker가 성공적으로 처리 → ack → 메시지 삭제

**시나리오 B — 장애 흐름**: 결제 Worker에서 의도적으로 Exception 발생 → nack 3회 → DLQ 이동

→ **확인 포인트**: DLQ에 메시지가 실제로 쌓이는지? RabbitMQ Management UI에서 확인.

#### Python (`workers/python/rabbitmq_worker.py`)

- [ ] `aio-pika` 설치 (`pip install aio-pika`)
- [ ] Exchange 선언: `order.exchange` (type: `direct`)
- [ ] Queue 선언:
  - `payment.queue` (durable: True — 브로커 재시작 시 Queue 유지)
  - `dead-letter.queue` (DLQ)
- [ ] Binding: `payment.queue` ← `payment` routing key
- [ ] Publisher 구현: `OrderEvent` → Exchange 발행
- [ ] Consumer 구현:
  - `manual ack` 모드 (자동 ack 비활성화)
  - 처리 성공 시 `message.ack()`
  - 처리 실패 시 `message.nack(requeue=False)` → DLQ로 이동
- [ ] DLQ 확인: 실패 메시지가 `dead-letter.queue` 에 쌓이는지 RabbitMQ UI에서 확인

#### Node.js (`workers/node/rabbitmq.worker.ts`)

- [ ] `amqplib` 설치 (`npm install amqplib`)
- [ ] Python과 동일한 Exchange / Queue 구조 구현
- [ ] Consumer 구현 (`noAck: false` 설정)

---

### 🔴 Task 3. BullMQ 구현

#### 핵심 개념 먼저 이해하기

BullMQ는 MQ라기보다 **"Job 관리 시스템"** 에 가깝다.
메시지가 아닌 "처리해야 할 작업(Job)"을 관리하며, 각 Job의 상태를 추적한다.

```
Job 상태 전환:

[enqueue]
    │
    ▼
[waiting] ──────→ [active] ──→ [completed]
                     │
                     └──→ [failed] ──→ retry ──→ [active]
                                         │ (maxAttempts 초과)
                                         └──→ [failed] (최종)
```

- **Queue**: Job이 대기하는 공간. Redis에 저장됨.
- **Worker**: Queue에서 Job을 꺼내 처리하는 프로세스.
- **Job Options**: retry 횟수(`attempts`), 지연 시간(`delay`), 우선순위(`priority`) 설정 가능.
- **Bull Dashboard**: Job 상태를 웹 UI로 모니터링 가능 (`bull-board` 패키지).

BullMQ가 결제보다 **이메일 발송, 이미지 처리 같은 Job**에 더 적합한 이유:
- 결제는 "이 메시지가 딱 한 번 처리됐음"(Exactly-once)이 중요 → RabbitMQ가 더 적합
- 이메일은 "처리 안 되면 2번이어도 괜찮으니 재시도해라"(At-least-once) → BullMQ 적합

#### 구현할 시나리오

**시나리오**: 이메일 발송 Job을 큐에 적재하고, 의도적으로 50% 실패율을 만들어 retry 동작 확인

```
[API 서버] → add Job (emailQueue)
                 │
                 ▼
           [BullMQ Queue] (Redis)
                 │
                 ▼
           [Email Worker]
           - 성공: Job → completed
           - 실패: Job → failed → 재시도 (최대 3회)
           - 최종 실패: failed Job 대시보드에서 확인
```

→ **확인 포인트**: Bull Board 대시보드에서 Job 상태 전환이 시각적으로 보이는가?

#### Python (`workers/python/bullmq_worker.py`)

- [ ] `rq` 설치 (`pip install rq`)
  - 참고: Python에는 공식 BullMQ 클라이언트가 없으므로 `rq`가 대안
  - `rq`는 BullMQ와 동일하게 Redis 기반 Job Queue
- [ ] Job 정의: `process_email_job(order_id, user_email)`
- [ ] Enqueue: `queue.enqueue(process_email_job, ...)`
- [ ] Worker 실행: `rq worker email-queue`
- [ ] 실패 시 failed queue 확인

#### Node.js (`workers/node/bullmq.worker.ts`)

- [ ] `bullmq` + `bull-board` 설치
- [ ] Queue 정의: `const emailQueue = new Queue('email-queue')`
- [ ] Worker 정의: 50% 확률로 exception 발생 (`Math.random() > 0.5`)
- [ ] `attempts: 3, backoff: { type: 'exponential', delay: 1000 }` 설정
  - 1차 실패 → 1초 후 재시도
  - 2차 실패 → 2초 후 재시도
  - 3차 실패 → `failed` 상태로 전환
- [ ] Bull Board UI에서 Job 상태 시각적 확인

---

### 📡 Task 4. MQTT 구현

#### 핵심 개념 먼저 이해하기

MQTT는 다른 MQ들과 근본적으로 다르다.
가장 중요한 차이: **Broker는 메시지를 저장하지 않는다** (Retain 메시지 제외).

```
Publisher → [Mosquitto Broker] → Subscriber (현재 접속 중인 경우만 수신)

구독 안 한 상태에서 발행된 메시지는 받을 수 없다!
→ 이것이 MQTT가 결제/주문 처리에 적합하지 않은 근본 이유
```

**QoS (Quality of Service) 란?**

메시지 전달 보장 수준을 설정한다.

| QoS Level | 전달 보장 | 중복 가능 | 사용 예 |
|---|---|---|---|
| **QoS 0** | 최선만 다함 (보장 없음) | 없음 | 실시간 센서 (잃어도 됨) |
| **QoS 1** | 최소 1회 전달 보장 | 가능 (중복 수신 위험) | 일반 알림 |
| **QoS 2** | 정확히 1회 전달 보장 | 없음 | 중요한 커맨드 |

QoS 0이 제일 빠르고, QoS 2가 제일 느리다.
IoT 디바이스(Jetson, 센서 등)는 배터리와 대역폭이 제한적이므로 QoS 0 또는 1을 주로 사용.

#### 구현할 시나리오

**시나리오**: Jetson 엣지 디바이스가 카메라 감지 이벤트를 MQTT로 전송하는 상황 시뮬레이션

```
[Jetson 시뮬레이터 (Publisher)]
    │ MQTT Topic: "devices/jetson-01/events"
    ▼
[Mosquitto Broker]
    │
    └──▶ [Backend Server (Subscriber)] → 이벤트 수신 → PostgreSQL 저장
                                        → Kafka로 forwarding (선택)
```

**QoS 레벨별 실험**:
- QoS 0: Subscriber가 잠깐 오프라인이면 메시지를 어떻게 처리하는가?
- QoS 1: 재연결 후 메시지를 받는가? 중복은 없는가?
- QoS 2: QoS 1보다 느린가? 얼마나?

→ **확인 포인트**: QoS별 Latency 차이와 메시지 유실 여부 비교

#### Python (`workers/python/mqtt_worker.py`)

- [ ] `paho-mqtt` 설치 (`pip install paho-mqtt`)
- [ ] Publisher 구현: QoS 0 / 1 / 2 각각으로 발행 → 각각 별도 테스트
- [ ] Subscriber 구현: 수신 시각 기록 → DB 저장
- [ ] **Subscriber 오프라인 시나리오 실험**:
  - Subscriber 프로세스 종료 → Publisher로 10개 메시지 발행 → Subscriber 재시작
  - QoS 0: 메시지 수신 개수는? (0개 예상)
  - QoS 1: 메시지 수신 개수는? Clean Session 설정에 따라 다름

#### Node.js (`workers/node/mqtt.worker.ts`)

- [ ] `mqtt.js` 설치 (`npm install mqtt`)
- [ ] Publisher / Subscriber 구현
- [ ] `cleanSession: false` 설정 후 오프라인 메시지 수신 동작 확인

---

### 📚 Task 5. MQ별 기술 문서 작성

구현 중에 이해한 내용을 반드시 문서로 남긴다.
나중에 다시 볼 때 "왜 이렇게 했지?"를 기억할 수 없기 때문이다.

- [ ] **`docs/tech/kafka.md`**
  - Topic / Partition / Offset / Consumer Group 개념 설명
  - KRaft 모드란? (Zookeeper가 필요 없어진 이유)
  - 이 프로젝트에서 Partition 3개로 설정한 이유
  - `enable.auto.commit = False` 로 설정한 이유 (수동 commit의 중요성)

- [ ] **`docs/tech/rabbitmq.md`**
  - Exchange / Queue / Binding / Routing Key 개념 설명
  - Direct Exchange vs Topic Exchange vs Fanout Exchange 차이
  - `ack` / `nack` / `requeue` 동작 방식
  - DLQ 설정 방법과 운영에서의 활용

- [ ] **`docs/tech/bullmq.md`**
  - Job 상태 전환 (waiting → active → completed / failed)
  - `attempts` + `backoff` 설정으로 exponential retry 구현
  - Python `rq` 와 Node.js `bullmq`의 차이점
  - Bull Board 설치 및 모니터링 방법

- [ ] **`docs/tech/mqtt.md`**
  - QoS 0 / 1 / 2 동작 원리와 차이
  - `cleanSession` 플래그의 역할
  - `Retain` 메시지란? 언제 쓰는가?
  - MQTT가 Kafka보다 IoT에 적합한 이유

---

### 🧩 Task 6. MQ 특징 심층 비교 문서 (`docs/tech/mq-characteristics.md`)

구현을 마친 후 "직접 만들어본 경험"을 바탕으로 작성한다.
이론으로 아는 것과 직접 만지고 느끼는 것은 다르다.

- [ ] **로그(Log) 처리 관점 비교**
  - Kafka만이 "로그의 왕"인 이유: 시간 순서대로 append, offset으로 임의 접근 가능
  - 나머지 MQ에서 로그 재처리가 어려운 이유

- [ ] **이벤트(Event) 관리 관점 비교**
  - 이벤트 소싱(Event Sourcing) 패턴이란?
  - Kafka가 이벤트 소싱에 최적인 이유
  - RabbitMQ에서 이벤트 재처리가 안 되는 이유

- [ ] **트랜잭션(Transaction) 관점 비교**
  - At-most-once / At-least-once / Exactly-once 차이
  - 각 MQ의 전달 보장 수준
  - 결제처럼 Exactly-once가 필요할 때 어떻게 구현하는가? (Idempotency Key 개념)

- [ ] **Python vs Node.js 생태계 비교**
  - 비동기 처리 모델 차이: Python asyncio vs Node.js event loop
  - 각 MQ 라이브러리 성숙도 비교
  - 코드 스타일 차이가 유지보수에 미치는 영향

---

## 🔗 산출물 (Output)

| 파일 | 설명 |
|---|---|
| `workers/python/kafka_worker.py` | Kafka Python Consumer |
| `workers/python/rabbitmq_worker.py` | RabbitMQ Python Consumer |
| `workers/python/bullmq_worker.py` | RQ Python Worker |
| `workers/python/mqtt_worker.py` | MQTT Python Subscriber |
| `workers/node/kafka.worker.ts` | Kafka Node Consumer |
| `workers/node/rabbitmq.worker.ts` | RabbitMQ Node Consumer |
| `workers/node/bullmq.worker.ts` | BullMQ Node Worker |
| `workers/node/mqtt.worker.ts` | MQTT Node Subscriber |
| `docs/tech/kafka.md` | Kafka 기술 문서 |
| `docs/tech/rabbitmq.md` | RabbitMQ 기술 문서 |
| `docs/tech/bullmq.md` | BullMQ 기술 문서 |
| `docs/tech/mqtt.md` | MQTT 기술 문서 |
| `docs/tech/mq-characteristics.md` | MQ 특징 심층 비교 |

---

## 📝 이 Phase를 마치면 알 수 있는 것

- [ ] Kafka의 Consumer Group이 RabbitMQ와 왜 다른지 설명할 수 있다
- [ ] RabbitMQ의 ack/nack/DLQ 흐름을 다이어그램으로 그릴 수 있다
- [ ] BullMQ의 Job 상태 전환을 설명하고 retry 설정을 할 수 있다
- [ ] MQTT QoS 0/1/2 중 어떤 상황에서 어떤 걸 쓸지 설명할 수 있다
- [ ] 동일한 시나리오에서 MQ 교체가 왜 어떤 곳에선 쉽고 어떤 곳에선 어려운지 설명할 수 있다

---

*[← Phase 1](./phase1.md) | [backlog 목록](./queue.md) | [Phase 3 →](./phase3.md)*
