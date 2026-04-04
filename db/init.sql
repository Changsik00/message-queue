-- 주문 테이블 (API 서버에서 생성)
CREATE TABLE orders (
    order_id    UUID PRIMARY KEY,
    user_id     VARCHAR(100) NOT NULL,
    total_price INTEGER NOT NULL,
    status      VARCHAR(20) DEFAULT 'PENDING',  -- PENDING | SUCCESS | FAILED
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 이벤트 처리 로그 (Worker에서 처리할 때마다 기록)
-- -> 중복 처리 검증, 유실 검증에 핵심적으로 사용
CREATE TABLE event_logs (
    id           SERIAL PRIMARY KEY,
    order_id     UUID NOT NULL,
    worker_type  VARCHAR(50) NOT NULL,  -- 'payment' | 'inventory' | 'notification'
    mq_type      VARCHAR(50) NOT NULL,  -- 'kafka' | 'rabbitmq' | 'bullmq' | 'mqtt'
    language     VARCHAR(20) NOT NULL,  -- 'python' | 'node'
    published_at TIMESTAMPTZ,           -- 이벤트 발행 시각
    consumed_at  TIMESTAMPTZ,           -- Worker 수신 시각
    latency_ms   INTEGER,               -- consumed_at - published_at (ms)
    status       VARCHAR(20),           -- 'SUCCESS' | 'FAILED'
    created_at   TIMESTAMPTZ DEFAULT NOW()
);
