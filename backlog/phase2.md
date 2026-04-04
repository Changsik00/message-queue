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

## ✅ Spec 목록 (MVP 분리)

아래 5개의 Spec은 각각 **독립적으로 배포 및 검증(Lean/MVP)**이 가능하도록 나뉘어져 있습니다. 
하나의 Spec 단위로 브랜치를 파고, 각 MQ가 의도한 시나리오대로 동작하는지 확인한 후 PR을 진행합니다.

### 🦅 Spec 2-001. Kafka 구현 (Kafka MVP)
> **동작 목표**: Kafka 브로커 위에서 파이프라인을 구축하고, 두 개 이상의 그룹이 이벤트를 병렬(독립) 소비하는 개념을 검증합니다.
- [ ] **구현**: `aiokafka`, `kafkajs` 패키지를 사용해 공통 인터페이스 맞춤 구현 (Topic: `orders`)
- [ ] **검증**: 결제 그룹(`payment-group`)과 재고 그룹(`inventory-group`) 생성 시, 한 번 발행한 메시지가 두 워커에 각자 로그를 남기는지 확인.

### 🐇 Spec 2-002. RabbitMQ 구현 (RabbitMQ MVP)
> **동작 목표**: RabbitMQ의 라우팅과 "재시도 후 실패 처리(DLQ)"를 집중 검증합니다.
- [ ] **구현**: `aio-pika`, `amqplib` 활용 및 수동(manual) `ack`/`nack` 제어 로직 적용
- [ ] **검증**: 워커 로직에서 인위적으로 예외 처리를 발생시킨 뒤, RabbitMQ 관리자 UI에서 해당 메시지가 Queue에 쌓이거나 `dead-letter.queue`로 이동됨을 눈으로 확인.

### 🔴 Spec 2-003. BullMQ 구현 (BullMQ MVP)
> **동작 목표**: 알림 전송과 같은 "반복 백그라운드 Job"을 돌려보고, "Job 상태 기반 지수적 재시도(Exponential backoff retry)"가 어떻게 도는지 모니터링합니다.
- [ ] **구현**: Python은 `rq`, Node.js는 `bullmq`를 사용하여 큐에 Job 생성
- [ ] **검증**: 50% 실패 확률 로직 추가 후 Job 재시도 타이머 및 이후 failed 큐로 탈락하는 전 과정을 Bull Board UI로 확인.

### 📡 Spec 2-004. MQTT 구현 (MQTT MVP)
> **동작 목표**: 경량 브로커를 활용해 QoS 별 메시지 유실 차이와 오프라인 상태 시 복원력을 테스트합니다.
- [ ] **구현**: `paho-mqtt`, `mqtt.js`를 사용 및 QoS(0, 1, 2) 파라미터 적용
- [ ] **검증**: 워커(구독자)를 강제 종료한 뒤 메시지를 발행하고 다시 워커를 켰을 때(비 clean 세션), QoS 설정 레벨에 따라 누락 여부 차이가 발생하는지 DB 로그로 증명.

### 📚 Spec 2-005. 기술 문서 & 심층 비교 작성 (Docs)
> **동작 목표**: 구현한 4종 MQ의 핵심 차이와 Event Sourcing, Transaction 모델의 관점을 사후 문서화합니다.
- [ ] **구현**: `docs/tech/kafka.md`, `rabbitmq.md`, `bullmq.md`, `mqtt.md` 개별 작성
- [ ] **비교 매트릭스**: `mq-characteristics.md` 에 "어떤 언어/상황에서 MQ 생태계가 나은가"를 기술.

---

## 🔗 산출물 (Output)

| 파일 | 설명 |
|---|---|
| `workers/python/kafka_worker.py` 등 | 각 MQ별 Python Worker |
| `workers/node/kafka.worker.ts` 등 | 각 MQ별 Node.js Worker |
| `docs/tech/` 내 마크다운들 | 각 MQ별 동작 원리와 기술 문서 |
| `docs/tech/mq-characteristics.md` | MQ 4종의 총 정리 비교 문서 |

---

## 📝 이 Phase를 마치면 알 수 있는 것

- [ ] Kafka의 Consumer Group이 RabbitMQ와 왜 다른지 설명할 수 있다
- [ ] RabbitMQ의 ack/nack/DLQ 흐름을 다이어그램으로 그릴 수 있다
- [ ] BullMQ의 Job 상태 전환을 설명하고 retry 설정을 할 수 있다
- [ ] MQTT QoS 0/1/2 중 어떤 상황에서 어떤 걸 쓸지 설명할 수 있다
- [ ] 동일한 시나리오에서 MQ 교체가 왜 어떤 곳에선 쉽고 어떤 곳에선 어려운지 설명할 수 있다

---

*[← Phase 1](./phase1.md) | [backlog 목록](./queue.md) | [Phase 3 →](./phase3.md)*
