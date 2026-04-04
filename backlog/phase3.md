# Phase 3 — 실험 & 측정

> **기간**: Week 4 | **상태**: 🔲 대기

---

## 🎯 이 Phase의 목적

Phase 2에서 "MQ가 돌아가게 만들었다"면,
Phase 3 에서는 **"돌아가는 MQ들이 실제로 얼마나 다른지"** 데이터로 증명한다.

코드가 작동한다고 해서 "좋은 MQ"를 선택한 게 아니다.
현업에서는 **"이 MQ로 우리 트래픽을 감당할 수 있는가?"**, **"장애 시 데이터를 잃지 않는가?"** 가 핵심이다.

이 Phase의 결과물(CSV, 측정 데이터)은 Phase 4에서 "MQ 선택 기준"을 정립하는 근거 데이터가 된다.

---

## 🧠 배경 지식 — 왜 이 항목들을 측정하는가?

### 처리량(Throughput)을 측정하는 이유

> "우리 서비스에 초당 1만 건 주문이 들어오기 시작했다. 현재 MQ가 버틸 수 있는가?"

처리량은 **MQ 선택의 첫 번째 필터**다.
BullMQ가 아무리 쓰기 편해도 초당 1만 건을 처리 못하면 의미없다.
반대로, Kafka가 아무리 강력해도 초당 10건짜리 서비스에 도입하는 건 오버엔지니어링이다.

### 지연시간(Latency)을 측정하는 이유

> "주문 버튼을 눌렀는데 결제 결과가 5초 후에 나온다. 이유가 뭔가?"

API 서버가 MQ에 이벤트를 발행하고, Worker가 그 이벤트를 받기까지의 시간이 Latency다.
**실시간 결제 피드백**이 필요한 서비스라면 Latency가 낮아야 한다.

- **P50 (중앙값)**: 평균적인 사용자 경험
- **P95**: 100명 중 95명이 경험하는 최대 지연
- **P99**: 꼬리 지연 — "가장 느린 1%의 사용자 경험"
  → 뱅킹/결제 서비스는 P99도 KPI로 관리한다.

### 장애 복구(Fault Tolerance)를 테스트하는 이유

> "배포 중에 Worker 프로세스가 죽었다. 처리 중이던 주문은 어떻게 됐는가?"

현업에서 장애는 반드시 발생한다. 문제는 장애가 나느냐가 아니라,
**장애 시 데이터가 유실되는가, 중복 처리되는가** 이다.

- Kafka: Offset을 commit하기 전에 죽으면? → 재처리됨 (At-least-once)
- RabbitMQ: ack 전에 죽으면? → Queue로 돌아감 (At-least-once)
- BullMQ: Active 상태에서 죽으면? → failed로 전환 후 retry
- MQTT: QoS 0에서 Subscriber가 죽으면? → 메시지 유실

### 재처리(Replay)를 테스트하는 이유

> "결제 Worker에 버그가 있어서 지난 1시간 동안 결제 처리가 잘못됐다. 바로잡으려면?"

Kafka만의 결정적 강점이 여기서 드러난다.
Kafka는 이벤트를 로그처럼 보관하기 때문에 **"과거로 돌아가서 다시 처리"** 가 가능하다.
나머지 MQ는 소비된 메시지를 삭제하기 때문에 불가능하다.

---

## ✅ Task 목록

---

### 🔥 Task 1. 부하 테스트 — 처리량(Throughput) 측정

#### 시나리오

```
[k6 부하 발생기]
    │ 초당 N개 요청
    ▼
[API 서버 (POST /orders)]
    │
    ▼ 주문 이벤트 발행
[MQ (교체하면서 테스트)]
    │
    ▼
[Worker (처리 후 DB 기록)]
    │
    ▼
[event_logs 테이블] ← 여기서 실제 처리된 TPS 집계
```

**무엇을 측정하는가?**
- API 서버가 MQ에 이벤트를 발행하는 속도 (Publish TPS)
- Worker가 MQ에서 이벤트를 가져와 처리하는 속도 (Consume TPS)
- 두 속도 차이가 벌어지기 시작하는 지점 (→ MQ가 병목)

#### k6 스크립트 (`load-test/order-test.js`)

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 100 },   // 워밍업: 100 TPS
    { duration: '3m', target: 1000 },  // 부하: 1000 TPS
    { duration: '2m', target: 5000 },  // 고부하: 5000 TPS
    { duration: '1m', target: 0 },     // 쿨다운
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // P95 응답시간 500ms 이하
    http_req_failed: ['rate<0.01'],    // 오류율 1% 이하
  },
};

export default function () {
  const res = http.post(
    'http://localhost:8000/orders',
    JSON.stringify({
      userId: `user_${Math.floor(Math.random() * 1000)}`,
      items: [{ productId: 'SKU-A', quantity: 1, price: 5000 }],
      totalPrice: 5000,
    }),
    { headers: { 'Content-Type': 'application/json' } }
  );

  check(res, {
    '200 OK': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
  });
}
```

- [ ] k6 설치 및 위 스크립트 작성
- [ ] **MQ별 실행** (각 MQ를 단독으로 실행하며 순서대로 측정)
  - [ ] Kafka + Python Worker
  - [ ] Kafka + Node.js Worker
  - [ ] RabbitMQ + Python Worker
  - [ ] RabbitMQ + Node.js Worker
  - [ ] BullMQ + Python Worker (rq)
  - [ ] BullMQ + Node.js Worker
  - [ ] MQTT + Python Worker
  - [ ] MQTT + Node.js Worker
- [ ] 각 측정 결과를 `results/throughput.csv` 에 기록

---

### ⏱️ Task 2. 지연시간(Latency) 측정

#### 측정 방법

이미 Phase 2에서 이벤트에 `publishedAt`을 심어뒀다.
Worker가 이벤트를 수신할 때 `consumed_at - publishedAt` 으로 계산한다.

```
[API 서버]  publishedAt = now()
    │
    ▼ 이벤트 발행
[MQ]
    │
    ▼ 이벤트 수신
[Worker]  consumed_at = now()
          latency_ms = consumed_at - publishedAt
          → event_logs 테이블에 기록
```

그 후 DB에서 집계:
```sql
SELECT
  mq_type, language,
  PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY latency_ms) as p50,
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95,
  PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms) as p99
FROM event_logs
GROUP BY mq_type, language;
```

- [ ] 1,000개 이벤트 발행 후 Latency 분포 측정 (MQ별 8종)
- [ ] P50 / P95 / P99 집계
- [ ] 결과를 `results/latency.csv` 에 저장
- [ ] **예상 결과 (실험 전 가설 세우기)**: 어떤 MQ가 가장 낮은 Latency를 보일 것인가?
  - 가설: BullMQ (Redis) < RabbitMQ < Kafka < MQTT (QoS 2)
  - 실험 후 가설과 실제 결과를 비교해서 차이가 나면 이유를 분석할 것

---

### 💥 Task 3. 장애 복구 테스트 — "데이터를 잃지 않는가?"

#### 시나리오 A — Consumer 강제 종료 (처리 중 죽으면?)

```
[Worker가 100개 메시지 처리 중]
        │ 50번째 처리 중
        X (kill -9 — 강제 종료)

[Worker 재시작]
        │
        ▼
재처리 결과:
- Kafka: 50번부터 다시 처리 (offset commit 안 됐으므로)
- RabbitMQ: ack 안 된 메시지 Queue로 복귀 → 재처리
- BullMQ: active 상태에서 죽은 Job → failed → retry
- MQTT QoS 0: 유실 (아무도 재전송 안 함)
- MQTT QoS 1: Broker가 재전송 시도
```

- [ ] **공통 절차**:
  1. 100개 메시지 발행
  2. Worker 실행 → 50번째쯤에서 `kill -9 $(pgrep -f worker)`
  3. Worker 재시작
  4. `event_logs` 에서 최종 처리된 메시지 수 확인
  5. 중복 여부 확인 (`SELECT order_id, COUNT(*) FROM event_logs GROUP BY order_id HAVING COUNT(*) > 1`)

- [ ] MQ별 결과 기록:

  | MQ | 유실 여부 | 중복 처리 | 재처리 소요 시간 |
  |---|---|---|---|
  | Kafka | ? | ? | ? |
  | RabbitMQ | ? | ? | ? |
  | BullMQ | ? | ? | ? |
  | MQTT QoS 0 | ? | ? | ? |
  | MQTT QoS 1 | ? | ? | ? |

#### 시나리오 B — 브로커 재시작 (MQ 자체가 죽으면?)

```
[MQ 브로커 실행 중]
    X (docker restart kafka/rabbitmq/redis/mosquitto)

[브로커 재시작 후]
    - 처리 중이던 메시지는 어떻게 됐는가?
    - Durability 설정(durable queue, persistence)이 영향을 주는가?
```

- [ ] `docker restart` 로 각 브로커 재시작
- [ ] 재시작 전 발행한 메시지가 재시작 후에도 남아있는지 확인
- [ ] **특히 확인**: Redis 기반 BullMQ는 Redis가 재시작되면 어떻게 되는가?
  → Redis AOF 설정 여부에 따라 다름 → 두 가지 모두 테스트

---

### 🔁 Task 4. 재처리 테스트 — "과거 이벤트를 다시 처리할 수 있는가?"

#### 시나리오

> "결제 Worker에 버그가 있어서 오늘 오전 10시~11시 사이 결제가 모두 잘못됐다.
> 버그 수정 후 그 1시간치 이벤트를 다시 처리할 수 있는가?"

```
정상 발행:  event1 → event2 → event3 → ... → event100

버그 발견 후:
→ Kafka: offset을 event1로 rewind → 처음부터 재처리 가능
→ RabbitMQ: 이미 ack됐으므로 메시지 없음 → 불가
→ BullMQ: completed Jobs → retry 불가 → DB에서 재발행해야 함
→ MQTT: 브로커에 메시지 없음 → 불가
```

- [ ] **Kafka Replay 실험**
  1. `orders` 토픽에 100개 메시지 발행 후 모두 소비
  2. Consumer Group offset 리셋:
     ```bash
     docker exec kafka kafka-consumer-groups.sh \
       --bootstrap-server localhost:9092 \
       --group payment-group \
       --topic orders \
       --reset-offsets --to-earliest --execute
     ```
  3. Consumer 재시작 → 100개 이벤트 다시 처리되는지 확인
  4. 재처리 소요 시간 측정

- [ ] **RabbitMQ DLQ Replay 실험**
  1. 처리 실패를 의도적으로 발생 → DLQ에 10개 쌓이게 함
  2. DLQ에서 메시지를 원래 Queue로 이동 (RabbitMQ Management UI)
  3. Worker가 DLQ 메시지를 재처리하는 것 확인
  4. DLQ가 Kafka Replay와 어떻게 다른지 정리

- [ ] **BullMQ Failed Job Retry 실험**
  1. 실패 설정으로 Job 10개를 failed 상태로 만듦
  2. Bull Board에서 "Retry All" 실행
  3. Job이 다시 active → completed 전환 확인

---

### 📊 Task 5. 순서 보장 테스트 — "이벤트 순서가 보장되는가?"

#### 왜 중요한가?

결제 시나리오를 생각해보자.
같은 주문에 대한 이벤트가 순서대로 처리되지 않으면:

```
올바른 순서: PENDING → PAYMENT_PROCESSING → PAYMENT_SUCCESS → SHIPPED
잘못된 순서: PENDING → PAYMENT_SUCCESS → PAYMENT_PROCESSING → ...
                        ↑ 순서 역전 시 비즈니스 로직 오류
```

#### 실험 설계

```
발행 순서: [1번], [2번], [3번], ... [100번]

수신 순서 확인:
→ 수신 시 순번 기록 → 순서대로 왔는지 검증
→ 순서 역전이 발생하면 어느 조건에서 발생하는지 기록
```

- [ ] **Kafka — Partition 수에 따른 차이**
  - Partition 1개: 순서 보장 가능 (전체 순서)
  - Partition 3개 + 동일 key: 같은 Partition → 순서 보장
  - Partition 3개 + 랜덤 key: 다른 Partition 가능 → 순서 역전 발생할 수 있음
  - → **결론**: Kafka에서 순서 보장이 필요하면 같은 `orderId`를 key로 사용해야 함

- [ ] **RabbitMQ — Consumer 수에 따른 차이**
  - Consumer 1개: Queue에서 순서대로 꺼내므로 순서 보장
  - Consumer 3개: 각 Consumer가 병렬 처리 → 처리 완료 순서는 불규칙
  - → **결론**: RabbitMQ에서 순서 보장이 필요하면 단일 Consumer로 제한

- [ ] **BullMQ — Priority Queue 테스트**
  - 기본 FIFO 순서 확인
  - `priority` 옵션으로 중요 Job 먼저 처리되는지 확인
  - → **활용**: 긴급 알림은 priority 1, 일반 알림은 priority 10

- [ ] **MQTT — 순서 보장 없음 확인**
  - QoS 1으로 100개 발행 → 수신 순서 기록 → 순서 역전 여부 확인

---

### 📈 Task 6. 결과 정리 & 시각화

측정한 데이터를 보기 좋게 정리한다.
이 결과가 Phase 4의 "MQ 선택 전략 문서"의 근거 데이터가 된다.

- [ ] `results/throughput.csv` 정리
- [ ] `results/latency.csv` 정리
- [ ] `results/fault-tolerance.md` — 장애 복구 테스트 결과 (표 형식)
- [ ] `results/ordering.md` — 순서 보장 테스트 결과 및 조건별 분석

- [ ] **시각화** (Python `matplotlib` 또는 `plotly`)
  ```python
  # 예: MQ별 P95 Latency 막대 그래프
  import pandas as pd
  import matplotlib.pyplot as plt

  df = pd.read_csv('results/latency.csv')
  df.pivot(index='mq_type', columns='language', values='p95') \
    .plot(kind='bar', title='P95 Latency by MQ (ms)')
  plt.savefig('results/latency-p95-chart.png')
  ```

---

## 🔗 산출물 (Output)

| 파일 | 설명 |
|---|---|
| `load-test/order-test.js` | k6 부하 테스트 스크립트 |
| `results/throughput.csv` | MQ별 TPS 측정 결과 |
| `results/latency.csv` | P50/P95/P99 Latency 측정 결과 |
| `results/fault-tolerance.md` | 장애 복구 테스트 결과 |
| `results/ordering.md` | 순서 보장 테스트 결과 |
| `results/latency-p95-chart.png` | Latency 시각화 차트 |

---

## 📝 이 Phase를 마치면 알 수 있는 것

- [ ] 어떤 MQ가 높은 처리량에서 먼저 병목을 보이는지 데이터로 설명할 수 있다
- [ ] "P95 Latency"가 무엇이고 왜 P50보다 중요한 경우가 있는지 설명할 수 있다
- [ ] Worker가 죽었을 때 MQ별로 다르게 대응하는 이유를 설명할 수 있다
- [ ] Kafka의 Replay가 왜 다른 MQ에서는 불가능한지 내부 구조로 설명할 수 있다
- [ ] Kafka에서 순서 보장을 위해 key 설계가 왜 중요한지 설명할 수 있다

---

*[← Phase 2](./phase2.md) | [backlog 목록](./queue.md) | [Phase 4 →](./phase4.md)*
