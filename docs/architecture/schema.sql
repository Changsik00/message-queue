-- processed_events 테이블: 각 MQ 워커가 처리한 이벤트의 최종 상태를 기록
CREATE TABLE IF NOT EXISTS processed_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(50) NOT NULL,          -- OrderEvent의 order_id
    group_id VARCHAR(50) NOT NULL,          -- 처리한 컨슈머 그룹 (payment-group, inventory-group 등)
    mq_type VARCHAR(20) NOT NULL,           -- 메시지 큐 종류 (kafka, rabbitmq, bullmq, mqtt)
    data JSONB NOT NULL,                    -- 수신한 이벤트 전체 데이터
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    latency_ms INTEGER                      -- (consumed_at - published_at) 지연 시간
);

-- 인덱스 생성: 특정 이벤트의 그룹별 처리 여부 확인용
CREATE INDEX IF NOT EXISTS idx_event_group ON processed_events (event_id, group_id);
