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

```text
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
이것이 가능하려면 공통 인터페이스 추상화가 필요하다 → Spec 002에서 구현.

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

## ✅ Spec 목록 (MVP 분리)

아래 3개의 Spec은 각각 **독립적으로 배포 및 검증(Lean/MVP)**이 가능하도록 나뉘어져 있습니다. 
하나의 Spec 단위로 브랜치를 파고, 완성 시점마다 정상 동작 여부를 확인한 후 PR을 진행합니다.

### 📦 Spec 1-001. 인프라 기반 구축 (Infra MVP)
> **동작 목표**: 코딩 없이 인프라 계층만 먼저 띄우고(DB, MQ), 접속 가능한 "데이터 파이프라인의 뼈대 환경"이 갖춰진 상태를 검증합니다.
- [x] **Docker Compose 구성**: Kafka, RabbitMQ, Redis, Mosquitto 및 PostgreSQL 구동 (헬스체크 포함)
- [x] **DB 스키마 셋업**: `init.sql`에 주문(`orders`) 및 결과 로그(`event_logs`) 테이블 정의
- [x] **검증**: `docker-compose up -d` 후 포트 충돌 없이 접속 가능한지 확인 (psql 접속 테스트 등)

### ⚙️ Spec 1-002. 애플리케이션 코어 및 공통 인터페이스 설계 (Core MVP)
> **동작 목표**: 향후 4가지 MQ 구현 시 비즈니스 로직 수정을 최소화하기 위한 '공통 뼈대(Interface)'와 데이터 규격(Schema)을 확정합니다. 실제 Message Queue 대신 기초적인 API 서버가 주문을 처리할 뼈대를 마련합니다.
- [ ] **이벤트 스키마 정의**: Latency 측정을 위해 `publishedAt`을 포함한 `OrderEvent` 데이터 모델 작성 (Python Pydantic, TS Interface)
- [ ] **추상화 인터페이스**: `base_queue` 기초 설계 (`connect`, `publish`, `consume` 등)
- [ ] **API 서버 & Worker 뼈대**: HTTP POST `/orders`를 받아 이벤트를 생성하고, Worker가 수신하는 Mock 파이프라인 작성
- [ ] **검증**: 기본 API 서버 구동 및 HTTP 요청 처리에 대한 기초 확인

### 📚 Spec 1-003. 아키텍처 구조 문서화 (Docs)
> **동작 목표**: 구축된 인프라 및 코어 뼈대를 기반으로 전체 시스템의 기술 문서를 확립하여 향후 Phase 2 구현 시 가이드라인으로 활용합니다.
- [x] `docs/architecture/overview.md`: 플로우 다이어그램과 동작 설명
- [x] `docs/architecture/event-schema.md`: 각 이벤트 필드 정의 및 타임스탬프 목적 설명
- [x] `docs/architecture/infrastructure.md`: 각 MQ별 동작 포트 번호 명세 문서 
- [x] `docs/architecture/mq-comparison.md`: 4종 MQ 기술 심층 비교 및 선택 가이드 (추가 항목 완료)

---

## 🔗 주요 산출물 (Output)

| 파일 | 설명 |
|---|---|
| `docker-compose.yml` | 전체 MQ + DB 인프라 |
| `db/init.sql` | PostgreSQL 초기 스키마 |
| `api-server/python/main.py` | FastAPI 주문 API 뼈대 |
| `api-server/node/src/main.ts` | Node.js 주문 API 뼈대 |
| `workers/python/base_queue.py` | Python 공통 인터페이스 |
| `workers/node/base-queue.interface.ts` | Node.js 공통 인터페이스 |
| `docs/architecture/` | 시스템 아키텍처 및 설정 가이드 문서들 |

---

## 📝 이 Phase를 마치면 알 수 있는 것

- [ ] MQ가 없으면 이 구조가 왜 문제인지 설명할 수 있다
- [ ] 이벤트 스키마에서 `publishedAt`이 왜 필요한지 설명할 수 있다
- [ ] 공통 인터페이스 추상화가 왜 MQ 교체를 쉽게 만드는지 설명할 수 있다
- [ ] `docker-compose up -d`로 4종 MQ 모두 로컬에서 실행할 수 있다

---

*[← backlog 목록으로](./queue.md) | [Phase 2 →](./phase2.md)*
