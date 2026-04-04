# Phase 4 — 정리 & 전략 문서

> **기간**: Week 5 | **상태**: 🔲 대기

---

## 🎯 이 Phase의 목적

Phase 1~3을 통해 "직접 만들고, 측정한 데이터"가 생겼다.
Phase 4는 그 데이터를 바탕으로 **"실무에서 MQ를 어떻게 선택해야 하는가"** 는 결론을 내리는 단계다.

이 Phase의 문서들은 단순한 요약이 아니다.
**"나중에 MQ를 선택해야 하는 상황이 왔을 때 꺼내볼 수 있는 실전 참고 자료"** 가 목표다.

---

## 🧠 배경 지식 — 현업에서 MQ 선택은 어떻게 하는가?

현업에서 MQ를 선택할 때 개발자들이 실제로 고민하는 항목:

1. **트래픽**: 현재 TPS는 얼마인가? 1년 후 예상 TPS는?
2. **유실 허용**: 메시지를 잃으면 얼마나 심각한가? (결제 vs 클릭 로그)
3. **재처리 필요**: 과거 이벤트를 다시 돌려야 하는 상황이 있는가?
4. **팀 역량**: 팀이 Kafka를 운영할 수 있는 역량이 있는가?
5. **기존 인프라**: 이미 Redis를 쓰고 있는가? 추가 인프라 없이 도입 가능한가?
6. **비용**: Kafka 클러스터 운영 비용 vs 기능의 필요성

---

## ✅ Task 목록

---

### 📊 Task 1. Phase 3 실험 결과 분석 및 비교 정리

Phase 3에서 수집한 원시 데이터를 정리하고, 결론을 도출한다.

**처리량(Throughput) 최종 비교**

| MQ | 언어 | 100 TPS | 1,000 TPS | 5,000 TPS | 한계 TPS |
|---|---|---|---|---|---|
| Kafka | Python | - | - | - | - |
| Kafka | Node.js | - | - | - | - |
| RabbitMQ | Python | - | - | - | - |
| RabbitMQ | Node.js | - | - | - | - |
| BullMQ | Python | - | - | - | - |
| BullMQ | Node.js | - | - | - | - |
| MQTT | Python | - | - | - | - |
| MQTT | Node.js | - | - | - | - |

**Latency 최종 비교**

| MQ | 언어 | P50 (ms) | P95 (ms) | P99 (ms) |
|---|---|---|---|---|
| Kafka | Python | - | - | - |
| Kafka | Node.js | - | - | - |
| RabbitMQ | Python | - | - | - |
| RabbitMQ | Node.js | - | - | - |
| BullMQ | Python | - | - | - |
| BullMQ | Node.js | - | - | - |
| MQTT | Python | - | - | - |
| MQTT | Node.js | - | - | - |

**장애 복구 최종 비교**

| MQ | 메시지 유실 | 중복 처리 | Replay 가능 | DLQ 지원 |
|---|---|---|---|---|
| Kafka | ❌/✅ | ✅ (offset commit 전) | ✅ Offset rewind | ✅ (별도 토픽) |
| RabbitMQ | ❌ | ✅ (ack 전) | ❌ | ✅ DLX |
| BullMQ | △ (AOF 설정 의존) | ✅ | ❌ | ✅ Failed Jobs |
| MQTT QoS 0 | ✅ (유실됨) | ❌ | ❌ | ❌ |
| MQTT QoS 1 | ❌ | ✅ (중복 가능) | ❌ | ❌ |

- [ ] 위 표를 실험 결과로 채우기
- [ ] 예상과 다른 결과가 있다면 이유 분석 및 기록

---

### 🏭 Task 2. 현업 사례 & 실전 시나리오 문서 작성

> **`docs/strategy/real-world-cases.md`** 작성

이 문서는 "어떤 상황에서 어떤 MQ를 골라야 하는가"를 실제 비즈니스 시나리오로 설명한다.
추상적인 설명이 아니라 **"이 회사, 이 상황에서 이 MQ를 선택했고 이유는 이것이다"** 형식으로 작성.

---

#### 📌 시나리오 A — 결제 처리 (직접 결제 승인 흐름)

> **상황**: 고객이 주문 버튼을 누르면 결제 PG API를 호출해서 승인 후 주문을 완료해야 한다.

**MQ가 없을 때의 문제**:
```
[API 서버] → PG API 호출 (3~5초) → 응답 기다림
   ↑
동시 요청 1,000개가 오면?
→ 서버 스레드/커넥션 고갈 → 타임아웃 폭발
```

**MQ를 도입한 흐름**:
```
[API 서버] → 즉시 200 응답 ("접수됐습니다")
     │
     ▼ publish(order.payment.requested)
[RabbitMQ]
     │
     ▼
[결제 Worker] → PG API 호출 → 성공 시 ack
                            → 실패 시 nack → DLQ → 운영팀 알림
```

**왜 RabbitMQ인가?**
- 결제는 **"반드시 처리됐음을 확인"** 이 필요 → manual ack 메커니즘
- 실패 시 DLQ로 이동 → 운영팀이 원인 파악 후 수동 재처리
- 결제 이벤트는 재처리(Replay)가 필요 없음 (이미 PG 상태를 DB에 저장)

**왜 Kafka가 아닌가?**
- Kafka EOS(Exactly-once)는 설정이 복잡하고 성능 저하가 있음
- 결제는 대용량 처리보다 **"정확한 처리"** 가 우선
- Kafka의 Consumer Group 모델은 "결제 1건을 1번만 처리"를 보장하기 어려움

- [ ] 위 내용을 도식과 함께 `docs/strategy/real-world-cases.md` 에 작성

---

#### 📌 시나리오 B — Webhook 수신 후 비동기 처리 (결제 PG → 내 서버 → 클라이언트)

> **상황**: 토스페이먼츠/카카오페이가 결제 결과를 Webhook으로 내 서버에 알려준다.
> 내 서버는 이걸 받아서 고객에게 결과를 알려줘야 한다.

**Webhook의 특성**:
- PG는 내 서버가 Webhook을 받으면 **5초 이내에 200 응답**을 기대한다
- 5초 안에 응답 못하면 PG는 Webhook을 재전송 (중복 처리 위험)
- 하지만 그 5초 안에 "DB 저장 + 이메일 발송 + 앱 푸시"를 모두 처리하기 어렵다

**MQ를 사용한 해결**:
```
[토스/카카오] → POST /webhooks/payment
                    │
                    ▼ (즉시 DB에 webhook raw data 저장 후)
            [즉시 200 응답] ← PG 타임아웃 방지
                    │
                    ▼ publish (비동기)
               [RabbitMQ / BullMQ]
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
     [DB 업데이트] [이메일] [앱 푸시]
          │
          ▼ (모두 완료 후)
  [클라이언트 Callback URL] POST → { status: "SUCCESS" }
```

**중복 처리 방지 (Idempotency)**:
- PG가 같은 Webhook을 2번 보낼 수 있음 (PG 재전송)
- 해결: `webhookId`를 DB에 저장, 이미 처리된 `webhookId`는 무시

**선택: RabbitMQ** (결제 관련이므로 유실 불가)
**또는 BullMQ** (클라이언트 Callback retry 관리가 목적이면 더 간단)

- [ ] 위 내용과 Idempotency 처리 방법을 `docs/strategy/real-world-cases.md` 에 작성

---

#### 📌  시나리오 C — 로그 & 이벤트 파이프라인 (대용량 클릭/조회 이벤트)

> **상황**: 쇼핑몰에서 사용자가 상품을 클릭, 조회, 장바구니 담기, 구매를 한다.
> 이 행동 데이터를 실시간으로 수집해서 추천 시스템과 데이터 분석에 활용한다.

**특성**:
- 초당 수만 건 이벤트 (클릭은 결제보다 훨씬 많음)
- 클릭 이벤트 1건 유실은 허용 가능 (비즈니스 영향 없음)
- **재처리 필요**: 추천 모델을 개선했다면 과거 1주일치 데이터를 다시 처리해야 함
- 여러 팀이 독립적으로 소비: 추천팀 / 분석팀 / 광고팀

```
[프론트엔드] → 클릭, 조회, 구매 이벤트 → [Kafka Topic: user.events]
                                                  │
                                  ┌───────────────┼───────────────┐
                                  ▼               ▼               ▼
                         Consumer Group:  Consumer Group:  Consumer Group:
                         recommendation  analytics        ads
                         (추천 모델 학습) (BigQuery 저장)  (광고 타겟팅)
```

**왜 Kafka인가?**
- Consumer Group: 추천팀 / 분석팀이 **같은 이벤트를 독립적으로** 처리
- 이벤트 영구 보관 (retention 설정): 추천 모델 재학습 시 과거 이벤트 Replay
- 초당 수만 건 처리 가능 (Partition 수로 수평 확장)

- [ ] 위 내용 + 실제로 LinkedIn, Uber가 Kafka를 이 용도로 쓰는 사례를 추가해서 작성

---

#### 📌  시나리오 D — 백그라운드 Job 처리 (이메일, 이미지 변환, 리포트 생성)

> **상황**: 회원가입 이메일 발송, 프로필 이미지 리사이징, PDF 리포트 생성 같은
> 시간이 걸리지만 즉시 응답이 필요 없는 작업들을 처리해야 한다.

**MQ 없이 하면**:
```
[API 서버] → 이메일 발송 (2초) → 이미지 리사이징 (3초) → 응답 (5초 후)
→ 사용자는 5초를 기다린다
```

**BullMQ를 쓰면**:
```
[API 서버] → Job 적재 (즉시) → 즉시 응답
                │
         [BullMQ + Redis]
                │
         ┌──────┼──────┐
         ▼      ▼      ▼
    [이메일  [이미지  [PDF
    Worker]  Worker]  Worker]

Job 옵션 활용:
- priority: VIP 회원 이메일은 priority 1 (먼저 처리)
- delay: 10분 후 발송 (쿠폰 이메일)
- attempts: 3회 실패 시 failed
- backoff: 지수적 재시도 (1초 → 2초 → 4초)
```

**왜 RabbitMQ가 아닌 BullMQ인가?**
- 이미 Redis를 쓰고 있다면 추가 인프라 없음
- Bull Board로 Job 상태를 웹 UI에서 실시간 모니터링
- Job 예약 스케줄링 (`cron` 표현식 지원)
- 이메일 정도는 유실돼도 재시도로 충분 → At-least-once 허용

- [ ] priority / delay / cron 옵션 예제 코드 포함해서 작성

---

#### 📌 시나리오 E — IoT 엣지 디바이스 (Jetson + MQTT + Kafka 조합)

> **상황**: 공장이나 CCTV에 Jetson Nano가 설치되어 있다.
> 실시간으로 감지 이벤트(사람 감지, 이상 온도 등)를 서버로 보내야 한다.

**제약 조건**:
- Jetson은 산업 현장에 있어 네트워크가 불안정할 수 있음
- 배터리 기반 센서는 전력 소비 최소화 필요
- 초당 30fps 카메라 데이터는 용량이 크므로 이벤트만 전송

```
[Jetson Nano (Edge)]
    │ MQTT (QoS 1) — 경량, 저전력, 불안정 네트워크에서도 OK
    ▼
[Mosquitto Broker (Backend)]
    │
    ▼ 이벤트 수신 후 변환
[Backend Gateway]
    │ Kafka (대용량 데이터 파이프라인)
    ▼
[Kafka Topic: device.events]
    │
    ├──▶ [InfluxDB Worker] → 시계열 데이터 저장
    ├──▶ [알림 Worker]     → 이상 감지 시 SMS/Email
    └──▶ [AI 분석 Worker]  → 모델 추론 결과 저장
```

**MQTT와 Kafka를 나누는 이유**:
- MQTT는 "디바이스 ↔ Backend" 구간에 최적: 저전력, 재연결 처리, 소규모 페이로드
- Kafka는 "Backend 내부" 구간에 최적: 대용량, 여러 Consumer, 데이터 영구 보관
- 두 기술은 경쟁 관계가 아니라 **역할이 다른 보완 관계**

- [ ] MQTT QoS 선택 가이드 포함 (Jetson에서 감지 이벤트는 QoS 1 권장 이유)

---

#### 📌 시나리오 F — MSA 분산 트랜잭션 (Saga 패턴)

> **상황**: 주문 서비스 / 결제 서비스 / 재고 서비스 / 배송 서비스가 각각 별개의 마이크로서비스로 분리되어 있다.
> 주문 1건 처리 시 4개 서비스의 작업이 모두 성공해야 한다. 중간에 하나라도 실패하면 롤백해야 한다.

**분산 트랜잭션의 핵심 문제**:
- 4개 서비스가 각자 DB를 가지고 있음 → ACID 트랜잭션 불가
- 어떻게 "모두 성공하거나 모두 롤백"을 구현하는가?

**Saga 패턴 (Choreography 방식)**:
```
[주문 서비스] → 이벤트: OrderCreated → [Kafka]
                                           │
                                           ▼
                                    [결제 서비스]
                                    결제 성공 시 → PaymentCompleted → [Kafka]
                                    결제 실패 시 → PaymentFailed → [Kafka]
                                           │
                             ┌─────────────┤
                             ▼             ▼
                    [재고 서비스]    [주문 서비스]
                    재고 차감         보상 트랜잭션
                                     OrderCancelled → 이메일 발송
```

**왜 Kafka인가?**
- 각 서비스가 독립적으로 이벤트를 발행 / 구독 (Choreography)
- 이벤트 로그가 남아 있으므로 보상 트랜잭션(Compensating Transaction)의 근거 데이터
- 이벤트를 재처리해서 "어느 단계에서 실패했는지" 추적 가능

**언제 RabbitMQ를 쓰는가?**
- Orchestration-based Saga: 중앙 조정자(Saga Orchestrator)가 각 서비스에 명령
- Saga Orchestrator → RabbitMQ → 각 서비스 (push 방식이 더 직관적)

- [ ] Choreography vs Orchestration 차이 설명 포함해서 작성

---

### 🧭 Task 3. MQ 선택 가이드 문서 (`docs/strategy/selection-guide.md`)

#### Phase 3 데이터 기반 결정 트리

```
                    ┌─────────────────────────────────┐
                    │  어떤 MQ를 선택해야 하는가?     │
                    └─────────────────┬───────────────┘
                                      │
                    ┌─────────────────▼───────────────┐
                    │ Q1. 처리량이 초당 수천 건 이상   │
                    │     이거나 이벤트 Replay가 필요? │
                    └──────┬──────────────────┬───────┘
                         YES                  NO
                           │                  │
               ┌───────────▼──┐    ┌──────────▼──────────┐
               │   → Kafka    │    │ Q2. 메시지 유실이    │
               └──────────────┘    │  절대 안 되는가?    │
                                   │  (결제, 금융 등)    │
                                   └──────┬───────┬──────┘
                                        YES       NO
                                          │        │
                              ┌───────────▼──┐  ┌──▼──────────────────┐
                              │ → RabbitMQ   │  │ Q3. IoT/디바이스    │
                              └──────────────┘  │  통신인가?          │
                                                └──────┬───────┬──────┘
                                                     YES       NO
                                                       │        │
                                           ┌───────────▼──┐  ┌──▼───────────┐
                                           │ → MQTT       │  │ → BullMQ     │
                                           │ (Edge 구간)  │  │ (백그라운드  │
                                           └──────────────┘  │  Job 처리)   │
                                                             └──────────────┘
```

**용도별 현업 선택 요약표**

| 용도 | 추천 MQ | 이유 | 실제 사례 |
|---|---|---|---|
| 결제 처리 | RabbitMQ | ack + DLQ, 유실 절대 불가 | 토스, 카카오페이 결제 백엔드 |
| Webhook 수신 후 비동기 | RabbitMQ / BullMQ | 즉시 응답 + retry 보장 | 모든 PG 연동 서비스 |
| 대용량 로그/이벤트 수집 | Kafka | 초당 수만 건, Replay, 다중 Consumer | Uber 로그, LinkedIn 피드 |
| 이메일 / SMS / Push 알림 | BullMQ | 단순 Job, Redis 재사용, 빠른 개발 | 대부분의 스타트업 알림 시스템 |
| 실시간 추천/개인화 | Kafka | 이벤트 스트림 → Feature 계산 | 넷플릭스 추천 시스템 |
| IoT 디바이스 통신 | MQTT | 저전력, 불안정 네트워크 | Tesla 텔레메트리, 공장 MES |
| MSA Saga 패턴 | Kafka | 이벤트 기반 보상 트랜잭션 | 마이크로서비스 e-commerce |
| 배치 처리 트리거 | BullMQ | cron 표현식 지원 | 정기 리포트, 데이터 정산 |
| 실시간 채팅 | Redis Pub/Sub | 초저지연, 별도 MQ 불필요 | 간단한 채팅 서비스 |

- [ ] 위 표 + 결정 트리 + 각 MQ "피해야 할 상황(When NOT to Use)" 포함해서 작성

---

### 🏗️ Task 4. 아키텍처 문서 최종 보완

Phase 1에서 코드도 없이 "예상"으로 썼던 아키텍처 문서를 이제 "경험"으로 보완한다.

- [ ] **`docs/architecture/overview.md`** 업데이트
  - Phase 3 결과 기반 권고사항 추가
  - "MQ 교체 시 바꿔야 하는 부분만 교체할 수 있는 이유" — 추상화 계층 설명

- [ ] **`docs/architecture/mq-comparison.md`** 신규 작성
  - 4종 MQ 핵심 개념 비교표 (Phase 2에서 배운 내용 기반)
  - 로그 / 이벤트 / 트랜잭션 관점의 적합도 매트릭스

  **적합도 매트릭스 (예시)**:

  | 요구사항 | Kafka | RabbitMQ | BullMQ | MQTT |
  |---|---|---|---|---|
  | 대용량 처리 (> 10K TPS) | ⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐ |
  | 메시지 유실 방지 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ |
  | 이벤트 Replay | ⭐⭐⭐ | ❌ | ❌ | ❌ |
  | 복잡한 라우팅 | ⭐ | ⭐⭐⭐ | ⭐ | ⭐ |
  | 운영 단순성 | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
  | IoT 디바이스 최적화 | ❌ | ❌ | ❌ | ⭐⭐⭐ |
  | 분산 트랜잭션 (Saga) | ⭐⭐⭐ | ⭐⭐ | ❌ | ❌ |
  | Job 상태 추적 | ❌ | ⭐ | ⭐⭐⭐ | ❌ |

---

### 📝 Task 5. README 최종 업데이트

- [ ] Phase 3 실험 결과 핵심 수치 추가 (링크 포함)
- [ ] 완성된 docs 파일 링크 업데이트
- [ ] Quick Start 가이드 실제 동작 확인 후 보완

---

## 🔗 산출물 (Output)

| 파일 | 설명 |
|---|---|
| `docs/strategy/real-world-cases.md` | 현업 시나리오 6종 (결제, Webhook, 로그, Job, IoT, Saga) |
| `docs/strategy/selection-guide.md` | MQ 선택 가이드 (결정 트리 + 용도별 표) |
| `docs/strategy/edge-to-cloud.md` | MQTT → Kafka 파이프라인 전략 |
| `docs/architecture/mq-comparison.md` | MQ 개념 비교 + 적합도 매트릭스 |
| `results/final-summary.md` | 전체 실험 결과 요약 |

---

## 📝 이 Phase를 마치면 할 수 있는 것

- [ ] 새 프로젝트에서 MQ가 필요한 상황을 만났을 때 결정 트리로 5분 안에 선택 근거를 제시할 수 있다
- [ ] "결제는 왜 Kafka보다 RabbitMQ가 적합한가?"를 3가지 이유로 설명할 수 있다
- [ ] Webhook을 수신할 때 왜 즉시 200 응답 후 MQ에 넣어야 하는지 설명할 수 있다
- [ ] 같은 팀원에게 "우리 서비스에 BullMQ / RabbitMQ / Kafka 중 어느 것이 맞는지"를 데이터와 함께 설득할 수 있다

---

*[← Phase 3](./phase3.md) | [backlog 목록](./queue.md)*
