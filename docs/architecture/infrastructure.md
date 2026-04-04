# Infrastructure Guide: 인프라 구동 및 서버 실행 방법

본 프로젝트의 전체 인프라 환경(MQ, DB)은 Docker 컨테이너 기반으로 구성됩니다. 각 서버와 브로커의 필수 실행 환경 및 포트 정보를 명시합니다.

## 1. 선행 필수 조건: Docker (Container) 구동
서버 앱(API Server, Worker)이 MQ 및 DB에 연결되어 작동하려면 가장 먼저 Docker 인프라가 실행 중이어야 합니다.

- **전체 인프라 기동 명령어**:
  ```bash
  docker compose up -d
  ```

- **개별 서비스 상태 확인**:
  ```bash
  docker compose ps
  ```
  (모든 서비스가 `healthy` 상태로 전환될 때까지 약 10~30초 소요됩니다.)

## 2. Infrastructure Port Map
전용 포트 충돌 방지를 위해 아래와 같이 기본 포트가 할당되어 있습니다.

| Service | Port | Description |
|---|---|---|
| **Kafka** | `9092` | Event Streaming Broker |
| **RabbitMQ** | `5672`, `15672` | AMQP Broker & Web Management Console |
| **Redis (BullMQ)** | `6379` | Job Queue Persistence |
| **Mosquitto (MQTT)** | `1883` | Lightweight IoT Messaging Broker |
| **PostgreSQL** | `5432` | 주문 및 처리 결과 통합 영속 저장소 |

---

## 3. API 서버 실행 가이드
사용자 주문을 수신하고 MQ로 발행하는 역할을 합니다. Python(8000)과 Node.js(3000) 각각 독립적으로 동작 가능합니다.

### A. Python API Server (FastAPI)
1. **디렉토리 이동**: `cd api-server/python`
2. **가상환경 세팅 및 의존성 설치**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **서버 실행**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### B. Node.js API Server (Express)
1. **디렉토리 이동**: `cd api-server/node`
2. **의존성 설치**:
   ```bash
   npm install
   ```
3. **서버 실행 (tsx)**:
   ```bash
   npx tsx src/main.ts
   ```

---

## 4. 로컬 테스트 및 검증
서버가 정상적으로 기동된 후, 아래 cURL 명령어를 통해 데이터가 MQ(Mock)로 인입되는지 확인합니다.

```bash
# Python Server Test (8000)
curl -X POST http://localhost:8000/orders \
-H "Content-Type: application/json" \
-d '{"amount": 100.0, "items": ["item1", "item2"]}'

# Node Server Test (3000)
curl -X POST http://localhost:3000/orders \
-H "Content-Type: application/json" \
-d '{"amount": 250.5, "items": ["premium-item"]}'
```
