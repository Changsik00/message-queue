import asyncio
import json
import os
import sys
import random
from datetime import datetime, timezone

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'packages'))
from shared_python import ProcessedEvent

import aio_pika
from sqlmodel import Session, create_engine

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/mq_db")
engine = create_engine(DB_URL)

async def process_message(message: aio_pika.abc.AbstractIncomingMessage):
    group_id = "payment-group"
    
    # We use manual ack/nack, so we do not use the context manager message.process()
    try:
        event_dict = json.loads(message.body.decode('utf-8'))
        order_id = event_dict.get("order_id")
        published_at_str = event_dict.get("published_at")
        
        consumed_at = datetime.now(timezone.utc)
        published_at = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
        latency_ms = int((consumed_at - published_at).total_seconds() * 1000)
        
        if os.getenv("SIMULATE_FAILURE", "false") == "true" and random.random() < 0.5:
            raise Exception("Simulated failure for DLQ routing")
            
        print(f" [x] {group_id} Received: {order_id} (Latency: {latency_ms}ms)")
        
        with Session(engine) as session:
            event_record = ProcessedEvent(
                event_id=order_id,
                group_id=group_id,
                mq_type="rabbitmq",
                data=json.dumps(event_dict),
                latency_ms=latency_ms
            )
            session.add(event_record)
            session.commit()
            
        await message.ack()
        
    except Exception as e:
        print(f" [!] {group_id} Error processing message: {e}")
        await message.reject(requeue=False)

async def consume_orders():
    amqp_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    group_id = "payment-group"
    
    connection = await aio_pika.connect_robust(amqp_url)
    
    async with connection:
        channel = await connection.channel()
        
        await channel.set_qos(prefetch_count=1)
        
        queue = await channel.declare_queue(
            "orders.queue",
            durable=True,
            arguments={
                "x-dead-letter-exchange": "dead-letter.exchange",
                "x-dead-letter-routing-key": "dlq"
            }
        )
        
        print(f"[*] Python Worker ({group_id}) started. Listening on {amqp_url}...")
        
        await queue.consume(process_message, no_ack=False)
        
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(consume_orders())
