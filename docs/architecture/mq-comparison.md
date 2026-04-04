# MQ Comparison: 4종 메시지 큐 기술 특성 및 선택 가이드

본 프로젝트에서는 서로 다른 목적과 고유한 설계 철학을 가진 4종의 MQ 기술을 사용합니다. **"왜 항상 Kafka가 정답이 아닌지"** 운영적 측면과 서비스 가용성 관점에서 심층 분석합니다.

## 1. MQ별 주요 특징 및 차이점

| 특성 | Kafka (Confluent) | RabbitMQ (VMware) | BullMQ (Redis-based) | MQTT (Mosquitto) |
|---|---|---|---|---|
| **설계 철학** | Distributed Commit Log | Advanced Message Broker | Job & Task Queue | IoT Pub/Sub Broker |
| **통신 방식** | Pull-based (Consumer가 가져감) | Push-based (Consumer에게 밀어줌) | Pull-based (Worker가 polling) | Push-based (초경량) |
| **Persistence** | Permanent (Retention 기간 동안) | In-memory / Disk 선택 | In-memory (Redis 캐시 기반) | In-memory (기본) |
| **Throughput** | **Highest** (대용량 로그 처리) | Medium (안정적 라우팅) | High (Redis 성능 종속) | Low ~ Medium (가벼움 위주) |
| **Latency** | Medium (Batch 처리로 인한 지연) | **Lowest** (상태 없는 초고속 전달) | Low | **Lowest** (네트워크 오버헤드 최소) |
| **주요 쓰임새** | 실시간 스트리밍, 로그 분석 | 비즈니스 트래픽, 메일 발송 | 백그라운드 작업, 지연 처리 | 센서 데이터 전송, 알림 |

---

## 2. 왜 무조건 Kafka 하나만 쓰면 안 되나요? (The Trade-offs)

많은 엔지니어가 "Kafka가 대세니까"라고 선택하지만, 실제 서비스 시나리오에 따라 오버헤드가 발생할 수 있습니다.

### A. 운영적 복잡도 (Operational Complexity)
Kafka는 분산 코디네이터(`Zookeeper` 또는 `KRaft`)와 브로커 클러스터 관리가 매우 까다롭습니다. 단순한 웹 애플리케이션의 비동기 처리(예: 회원가입 환영 메일 발송)를 위해 Kafka를 도입하는 것은 **"파리를 잡기 위해 대포를 쏘는 격"**일 수 있습니다.

### B. 순서 보장과 파티셔닝의 함정
Kafka는 파티션 내에서의 순서는 엄격히 보장하지만, 여러 파티션에 걸쳐 전체적인 순서를 보장받기는 어렵습니다. 또한 파티션 수를 늘리면 처리량은 늘지만 관리 코스트가 증가합니다.

### C. 실시간 지연시간 (Real-time Latency)
Kafka는 효율을 위해 메시지를 배치(Batch) 단위로 묶어 처리하는 경향이 있습니다. 만약 데이터 1건 1건이 1ms 단위의 초저지연을 요구한다면, 정교한 라우팅 기능을 제공하는 **RabbitMQ**나 초경량 바이너리 프로토콜인 **MQTT**가 훨씬 유리합니다.

---

## 3. 이럴 때 무엇을 선택해야 할까? (Best Practices)

- **Kafka** : 하루에 수억 건의 로그 대량 데이터 분석, 이벤트 스트리밍, 데이터 파이프라인(ETL) 구축 시.
- **RabbitMQ** : 복잡한 라우팅(Fan-out, Topics)이 필요하거나, 각 메시지의 유실 없이 비즈니스 로직을 비동기로 처리해야 할 때.
- **BullMQ** : Node.js/Python 생태계에서 백그라운드 Job을 스케줄링(10분 뒤 실행)하거나, 우선순위 큐(Vip 전용 큐)가 필요할 때.
- **MQTT** : 수천 개의 모바일 기기나 저전력 센서(IoT)로부터 데이터를 수집하고, 매우 낮은 대역폭에서 통신해야 할 때.
