import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from aiokafka import AIOKafkaConsumer
from sqlalchemy import create_engine, text

# add 프로젝트 루트를 sys.path에 추가하여 base_queue 임포트 가능하게 함
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
# from workers.python.base_queue import OrderEvent

# DB 연결 정보
DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/mq_db")
engine = create_engine(DB_URL)

async def consume_orders():
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    group_id = "payment-group"
    
    consumer = AIOKafkaConsumer(
        "orders",
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset="earliest"
    )
    
    await consumer.start()
    print(f"[*] Python Worker ({group_id}) started. Listening on {bootstrap_servers}...")
    
    try:
        async for msg in consumer:
            event_dict = msg.value
            order_id = event_dict.get("order_id")
            published_at_str = event_dict.get("published_at")
            
            # 지연 시간 계산 (ms)
            consumed_at = datetime.now(timezone.utc)
            published_at = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
            latency_ms = int((consumed_at - published_at).total_seconds() * 1000)
            
            print(f" [x] {group_id} Received: {order_id} (Latency: {latency_ms}ms)")
            
            # DB 저장
            with engine.connect() as conn:
                query = text("""
                    INSERT INTO processed_events (event_id, group_id, mq_type, data, latency_ms)
                    VALUES (:event_id, :group_id, :mq_type, :data, :latency_ms)
                """)
                conn.execute(query, {
                    "event_id": order_id,
                    "group_id": group_id,
                    "mq_type": "kafka",
                    "data": json.dumps(event_dict),
                    "latency_ms": latency_ms
                })
                conn.commit()
                
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(consume_orders())
