# Plan: 1-003 - 아키텍처 구조 문서화 (Docs)

## 1. 접근 방법론 (Approach)
코드나 인프라 환경에서 추론할 수 있는 정보를 바탕으로, 다음 4가지 핵심 요소를 상세히 기술 문서화합니다. 특히, **단순 구현을 넘어 시나리오별 각 MQ의 설계 철학(Trade-offs)을 비교 분석**하는 지식 베이스를 구축합니다.

1. **아키텍처 가시화**: 전체 서비스 플로우 및 메시지 흐름 다이어그램 작성.
2. **실행 매뉴얼**: 로컬 개발 환경(Docker, API Server) 구축 및 실행 가이드.
3. **MQ 기술 비교**: Kafka, RabbitMQ, BullMQ, MQTT의 장단점 및 특징 기술.
    - *왜 Kafka를 안 쓸 때도 있는가?* 에 대한 운영적/비즈니스적 트레이드오프 설명.
4. **스키마 명세**: 이벤트 데이터 규격 및 Latency 측정을 위한 데이터 설계 가이드.

## 2. 디렉토리/파일 변경 계획
- `[NEW]` `/docs/architecture/overview.md` - 아키텍처 흐름 및 시나리오 정리
- `[NEW]` `/docs/architecture/infrastructure.md` - Docker 구동 가이드, API 서버별 실행 명령어 매뉴얼 및 포트 테이블
- `[NEW]` `/docs/architecture/comparison.md` - 4종 MQ(Kafka, RabbitMQ, BullMQ, MQTT) 심층 비교 및 선택 가이드 (Trade-off 분석)
- `[NEW]` `/docs/architecture/event-schema.md` - `OrderEvent` 스키마 디자인 및 Latency 측정 원리 설명
- `[MODIFY]` `/README.md` - 신규 문서들에 대한 Reference Link 추가

## 3. 테스트 전략 (Testing Strategy)
- 문서 내 명시된 `docker-compose` 및 API 서버 실행 명령어를 직접 터미널에서 수행하여 가이드의 정확성 검증.
- Mermaid 다이어그램이 GitHub(로컬 렌더러)에서 정상적으로 출력되는지 확인.
