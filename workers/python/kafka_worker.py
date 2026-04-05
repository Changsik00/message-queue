import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from typing import Optional
from aiokafka import AIOKafkaConsumer
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Data Model
class ProcessedEvent(SQLModel, table=True):
    __tablename__ = "processed_events"
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str
    group_id: str
    mq_type: str
    data: str
    processed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    latency_ms: int

# DB 연결 정보
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/mq_db")
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
            
            # DB 저장 (SQLModel)
            with Session(engine) as session:
                event_record = ProcessedEvent(
                    event_id=order_id,
                    group_id=group_id,
                    mq_type="kafka",
                    data=json.dumps(event_dict),
                    latency_ms=latency_ms
                )
                session.add(event_record)
                session.commit()
                
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(consume_orders())
