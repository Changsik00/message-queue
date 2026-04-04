# Spec: 1-003 - 아키텍처 구조 문서화 (Docs)

## 1. 개요 (Overview)
- **목적**: 구축된 컨테이너 기반 인프라(`docker-compose`)와 애플리케이션 코어(MQ Adapter)의 전체적인 아키텍처 흐름, 필수 구동 환경(Docker), 서버/인프라별 접속 포트 등의 실행 방법을 상세화하고, **각 MQ(Kafka, RabbitMQ, BullMQ, MQTT)의 기술적 특성과 차이점을 비교 분석하여 설계 근거를 마련**합니다.
- **영향 범위**: `docs/architecture/` 디렉토리 하위의 시스템 문서들.
- **관련 지표/이슈**: [Phase 1 Backlog](../../backlog/phase1.md)

## 2. 상세 요구사항 (Requirements)
- [ ] **서버 아키텍처 다이어그램 및 동작 흐름 설명** (`overview.md`): 시스템 전체 레이아웃 및 이벤트 발행/소비 구조 시각화.
- [ ] **서버 포트 및 실행 방법 명시** (`infrastructure.md`): Python / Node.js 서버 실행 스크립트 작성 및 포트 매핑 가이드.
- [ ] **컨테이너 선행 조건 명시** (`infrastructure.md`): `docker-compose` 구동 방법과 MQ/DB 컨테이너 헬스체크 확인법.
- [ ] **MQ 원리 및 기술 심층 비교** (`comparison.md`):
    - Kafka, RabbitMQ, BullMQ, MQTT 별 특징 (Push vs Pull, Persistence, Latency, Throughput).
    - "무조건 Kafka"가 정답이 아닌 이유와 서비스 시나리오별 적합한 MQ 선택 가이드 (Trade-off 분석).
- [ ] **공용 이벤트 스키마 정보** (`event-schema.md`): `OrderEvent` 필드 정의와 타임스탬프 기반 Latency 측정 원리.

## 3. 제약사항 및 비기능 요구사항
- 문서는 새로 합류한 개발자 관점에서 명령어 복사 및 붙여넣기로 즉시 실행해볼 수 있도록 간결하게 작성되어야 합니다.
- **기술 비교 시 중립적인 시각**으로 각 MQ의 장단점을 명확히 기술하고 설계 의사결정을 돕는 근거를 제공해야 합니다.
- GitHub 표준 가이드에 따라 확장된 Mermaid 렌더링 에러가 나타나지 않도록 특수기호를 지양해야 합니다.
