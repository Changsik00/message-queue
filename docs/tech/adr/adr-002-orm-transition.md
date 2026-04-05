# ADR-002: SQLModel 도입 및 ORM 마이그레이션

## 상태
**Accepted**

## 배경
API 서버(FastAPI)와 워커들이 동일한 데이터 모델을 다른 방식(Pydantic + SQLAlchemy)으로 중복 정의하고 있었습니다. 이는 스키마 변경 시 양쪽 모두를 수정해야 하는 비효율을 초래했습니다.

## 결정
1.  **SQLModel 도입**: SQLAlchemy와 Pydantic의 강점을 하나로 합친 SQLModel을 ORM 기반으로 채택합니다.
2.  **공통 모델 추출**: `api-server/python/common/models.py`에 공통 모델을 두고 API와 전용 워커들이 이를 임포트하여 사용하도록 합니다.

## 결과 및 향후 계획
- **결과**: 코드 중복 제거 및 모델 정의의 가독성 향상.
- **향후 계획**: `Alembic`을 연동하여 `SQLModel`에서 자동으로 마이그레이션 스크립트를 생성하도록 자동화할 계획입니다.
