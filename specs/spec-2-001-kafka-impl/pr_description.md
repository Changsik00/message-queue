# PR: Spec 2-001 - Kafka 구현 및 아키텍처 기초 수립

## 1. 개요 (Description)
- Phase 2의 첫 번째 단계로, Kafka를 이용한 메시지 큐 파이프라인을 구축했습니다.
- 단순히 기능을 구현하는 것을 넘어, 향후 확장성을 고려한 패키지 관리(pnpm) 및 ORM(SQLModel) 표준화를 병행하였습니다.
- Resolves #Spec-2-001

## 2. 작업 상세 내용 (Changes)
- [x] **Kafka MVP 구현**: Python API Server(Producer)와 Python/Node.js Worker(Consumer) 간의 이벤트 발행/구독 로직 구현.
- [x] **pnpm 및 버전 고정**: Node.js 의존성 관리 도구를 pnpm으로 전환하고 모든 패키지 버전을 정적으로 고정하여 환경 일관성 확보.
- [x] **SQLModel 도입**: SQLAlchemy와 Pydantic을 통합한 SQLModel을 채택하고, `api-server/python/common/models.py`로 공통 DB 모델 추출.
- [x] **기술 결정 기록(ADR)**: `docs/tech/adr/` 하위에 패키지 매니저, ORM, 인프라 전략에 대한 ADR 001~003 문서 작성.

## 3. 아키텍처 및 로직 흐름 (Mermaid)
```mermaid
graph TD
    A["Client"] -->| "POST /orders" | B["Python API Server"]
    B -->| "Produce OrderEvent" | C["Kafka Broker"]
    C -->| "Consume" | D["Python Worker (payment-group)"]
    C -->| "Consume" | E["Node.js Worker (inventory-group)"]
    D -->| "Insert Log" | F["PostgreSQL"]
    E -->| "Insert Log" | F
```

## 4. 테스트 결과 및 체크리스트 (Testing Checklist)
- [x] Kafka를 통한 다중 컨슈머 그룹의 독립 소비 및 DB 저장 확인.
- [x] pnpm install 및 고정 버전 기반 빌드 정상 동작 확인.
- [x] SQLModel 기반의 공통 모델 임포트 및 DB 연동 확인.
- [x] Linting 및 ADR 문서 가이드 준수.

## 5. 리뷰어에게 (To Reviewers)
- **임의 처리 고지**: Kafka 토픽 자동 생성 설정을 사용 중입니다. Phase 3 진입 전 수동 관리로 전환할 계획입니다. (ADR-003 참고)
- **구조**: `api-server/python/common` 디렉토리를 통해 모델을 공유하는 방식에 대해 의견 부탁드립니다.
