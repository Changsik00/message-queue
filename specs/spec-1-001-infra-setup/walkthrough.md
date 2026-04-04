# Walkthrough: 1-001 - 인프라 기반 구축 (Infra MVP)

> 이 문서는 개발 과정 전반을 실시간으로 기록하는 "개발 일지(Developer Log)"입니다. 

## 1. Thought Process (사고 과정)
- **Problem**: 4종의 MQ 데이터베이스 환경과 PostgreSQL을 로컬에 손쉽게 띄우고 테스트할 수 있어야 함.
- **Alternative 1**: 스크립트를 통한 5개 패키지 직접 설치 (설정 오류 및 패키지 꼬임 현상 우려)
- **Alternative 2**: `docker-compose` 하나로 묶기
- **Decision & Why**: Alternative 2 선택. 각기 다를 수 있는 로컬 환경과 무관하게 언제든 띄우고 지울 수 있는 형태인 컨테이너 통합본이어야 추후 MQ 비교 성능 측정 시 공정한 환경을 담보할 수 있음.

## 2. 상태 전이 및 로직 다이어그램 (Mermaid)

```mermaid
graph TD
    Client["Local Developer"] -->|5432| DB[("PostgreSQL: mq_db")]
    Client -->|9092| Kafka["Kafka (KRaft Mode)"]
    Client -->|"5672, 15672"| RabbitMQ["RabbitMQ + UI"]
    Client -->|6379| Redis["Redis"]
    Client -->|"1883, 9001"| MQTT["Mosquitto + WebSocket"]
    DB -.-> Volume["/docker-entrypoint-initdb.d/"]
```

## 3. 에러 해결 로그 (Troubleshooting)
- **발생 시점**: Task 체크박스 `[ ] 터미널에서 docker-compose up -d 명령어 구동...` 도중 
- **에러 메시지**: `failed to connect to the docker API at unix:///Users/ck/.docker/run/docker.sock`
- **원인 / 추론**: 로컬 PC의 Docker 데몬이 실행 중이지 않아 CLI가 API에 접근 불가.
- **해결 방법**: `docker-compose.yml` 린팅 및 검증만 진행하고, 실제 구동 체크는 사용자가 로컬에서 Docker 구동 후 직접 진행하도록 일임. (Task의 체크리스트상에서 해당 내용을 괄호로 명시하여 예외를 기록)
- **발생 시점**: `docker-compose up -d` 명령어 구동 시
- **에러 메시지**: `the attribute version is obsolete`
- **해결 방법**: `docker-compose.yml` 파일 상단의 `version: '3.8'` 제거
