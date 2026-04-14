"""Python RQ Worker for BullMQ spec.

RQ(Redis Queue)를 사용하여 'orders-python' 큐에서 Job을 가져와 처리합니다.
API Server가 enqueue한 Job을 소비하고 processed_events 테이블에 저장합니다.

Job 처리 함수(process_order)는 module 경로로 참조되므로,
이 파일이 Python path에 있어야 합니다 (workers/python/ 에서 실행).

macOS 실행 시 주의:
    RQ는 내부적으로 fork()를 사용하며, macOS에서 Objective-C 런타임과
    충돌할 수 있습니다. 아래 환경변수를 설정해야 합니다:
    OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES venv/bin/python bullmq_worker.py
"""

import json
import os
import random
import sys
from datetime import datetime, timezone

import redis
from rq import Queue, Worker
from sqlmodel import Session, create_engine

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'packages'))
from shared_python import ProcessedEvent

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/mq_db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
QUEUE_NAME = "orders-python"
GROUP_ID = "payment-group"
SIMULATE_FAILURE = os.getenv("SIMULATE_FAILURE", "false") == "true"


def _get_engine():
    """RQ 포크 서브프로세스에서 SQLAlchemy 엔진 충돌을 방지하기 위해 lazy 생성."""
    return create_engine(os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/mq_db"))


def process_order(event_dict: dict) -> dict:
    """RQ Worker가 실행하는 Job 처리 함수.

    API Server가 'bullmq_worker.process_order' 경로로 enqueue합니다.
    RQ Worker는 이 함수를 import하여 실행합니다.
    """
    order_id = event_dict.get("order_id")
    published_at_str = event_dict.get("published_at")

    consumed_at = datetime.now(timezone.utc)
    published_at = datetime.fromisoformat(str(published_at_str).replace("Z", "+00:00"))
    latency_ms = int((consumed_at - published_at).total_seconds() * 1000)

    # SIMULATE_FAILURE: 50% 확률로 강제 실패 → RQ가 자동 retry
    if SIMULATE_FAILURE and random.random() < 0.5:
        raise Exception(f"[SIMULATE_FAILURE] Intentional failure for order {order_id}")

    print(f" [x] {GROUP_ID} Received: {order_id} (Latency: {latency_ms}ms)")

    with Session(_get_engine()) as session:
        event_record = ProcessedEvent(
            event_id=order_id,
            group_id=GROUP_ID,
            mq_type="bullmq",
            data=json.dumps(event_dict),
            latency_ms=latency_ms,
        )
        session.add(event_record)
        session.commit()

    print(f" [✓] {GROUP_ID} Completed: {order_id}")
    return {"status": "ok", "order_id": order_id}


if __name__ == "__main__":
    conn = redis.from_url(REDIS_URL)
    queue = Queue(QUEUE_NAME, connection=conn)
    worker = Worker([queue], connection=conn)

    print(f"[*] Python RQ Worker ({GROUP_ID}) started. Listening on queue '{QUEUE_NAME}' (SIMULATE_FAILURE={SIMULATE_FAILURE})")
    worker.work(with_scheduler=True)
