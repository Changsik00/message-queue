# Event Schema: OrderEvent 데이터 명세 및 성능 측정 원리

본 프로젝트에서 발행/소비되는 모든 이벤트는 동일한 `OrderEvent` 스키마를 준수합니다. 이를 통해 서로 다른 MQ 기술을 사용하더라도 데이터 무결성을 유지하며 정량적인 비교가 가능합니다.

## 1. 상위 데이터 모델 (OrderEvent)
모든 필드는 JSON 직렬화를 통해 전송되며, 각 언어별(Python, TS) 데이터 타입은 다음과 같습니다.

| Field | Type (Python) | Type (TS) | Description |
|---|---|---|---|
| `order_id` | `str` | `string` | 주문의 유니크한 UUID |
| `user_id` | `str` | `string` | 주문을 생성한 유저 고유 ID |
| `amount` | `float` | `number` | 주문 총 금액 |
| `items` | `list[str]` | `string[]` | 주문 상품 리스트 |
| `published_at` | `datetime` | `Date` | **핵심 지표**: 이벤트가 발행된 시점 (UTC) |

---

## 2. Latency (지연 시간) 측정 원리
본 프로젝트의 핵심 성능 분석인 **"메시지가 얼마나 실시간으로 도착하는가?"**는 `published_at` 필드를 사용하여 다음과 같이 계산됩니다.

- **발행(Publish)** : API 서버에서 메시지를 생성할 때 즉시 UTC 시간을 `published_at`에 기록합니다.
- **소비(Consume)** : Worker가 메시지를 최종 수신하는 순간의 시간을 `consumed_at`으로 정의합니다.
- **계산식** : `Latency = consumed_at - published_at` (ms 단위)

이 측정 결과는 추후 `results/` 폴더에 CSV 로깅되어 시각화 차트로 변환됩니다.

## 3. 데이터 일관성 가이드
- 모든 날짜/시간 데이터는 ISO 8601 포맷으로 통일합니다.
- 각 MQ 어댑터는 바이너리 또는 문자열 전송 시 반드시 `utf-8` 인코딩을 준수해야 합니다.
