import sys
import os
import json
import asyncio
import time
from aiokafka import AIOKafkaProducer
import aio_pika
import redis as redis_sync
from rq import Queue as RQQueue
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'packages'))
from shared_python import OrderEvent, BaseQueue

app = FastAPI()

class KafkaQueue(BaseQueue):
    def __init__(self):
        self.producer = None
        self.loop = asyncio.get_event_loop()
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()
        print(f"KafkaQueue: Connected to {self.bootstrap_servers}")

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    def connect(self) -> None:
        # FastAPI startup handler will call start()
        pass
    
    async def publish_async(self, event: OrderEvent) -> None:
        if not self.producer:
            await self.start()
        await self.producer.send_and_wait("orders", event.model_dump(mode='json'))
        print(f"KafkaQueue: Published event {event.order_id}")

    def publish(self, event: OrderEvent) -> None:
        # This is for compatibility with the interface if called synchronously
        # In FastAPI, we should use publish_async
        pass
    
    def consume(self) -> None:
        pass

class RabbitMQQueue(BaseQueue):
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None
        self.amqp_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

    async def start(self):
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()
        
        # DLQ Exchange
        dlq_exchange = await self.channel.declare_exchange(
            "dead-letter.exchange", aio_pika.ExchangeType.DIRECT, durable=True
        )
        dlq_queue = await self.channel.declare_queue("dead-letter.queue", durable=True)
        await dlq_queue.bind(dlq_exchange, routing_key="dlq")
        
        # Primary Exchange
        self.exchange = await self.channel.declare_exchange(
            "orders", aio_pika.ExchangeType.DIRECT, durable=True
        )
        
        # Primary Queue with DLQ arguments
        queue = await self.channel.declare_queue(
            "orders.queue",
            durable=True,
            arguments={
                "x-dead-letter-exchange": "dead-letter.exchange",
                "x-dead-letter-routing-key": "dlq"
            }
        )
        await queue.bind(self.exchange, routing_key="order.created")
        print(f"RabbitMQQueue: Connected to {self.amqp_url}")

    async def stop(self):
        if self.connection:
            await self.connection.close()

    def connect(self) -> None:
        pass
        
    async def publish_async(self, event: OrderEvent) -> None:
        if not self.exchange:
            await self.start()
        message = aio_pika.Message(
            body=json.dumps(event.model_dump(mode='json')).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        await self.exchange.publish(message, routing_key="order.created")
        print(f"RabbitMQQueue: Published event {event.order_id}")

    def publish(self, event: OrderEvent) -> None:
        pass
        
    def consume(self) -> None:
        pass

class BullMQProducer:
    """BullMQ 큐에 Job을 enqueue하는 Producer.

    BullMQ의 Redis 키 구조에 맞게 직접 데이터를 씁니다:
    - bull:{queue}:id       → INCR (auto-increment Job ID)
    - bull:{queue}:{jobId}  → HMSET (Job 데이터)
    - bull:{queue}:wait     → RPUSH (대기 중인 Job ID 목록)

    Python RQ Worker를 위해 orders-python 큐에도 동시 enqueue합니다.
    """

    BULL_PREFIX = "bull"
    BULL_QUEUE = "orders"
    RQ_QUEUE = "orders-python"

    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self._redis = redis_sync.from_url(redis_url, decode_responses=True)
        self._rq_queue = RQQueue(self.RQ_QUEUE, connection=redis_sync.from_url(redis_url))

    def _enqueue_bullmq(self, event: OrderEvent) -> str:
        """BullMQ 포맷으로 Redis에 직접 Job을 추가한다."""
        job_id = str(self._redis.incr(f"{self.BULL_PREFIX}:{self.BULL_QUEUE}:id"))
        job_opts = json.dumps({
            "attempts": 3,
            "backoff": {"type": "exponential", "delay": 1000},
        })
        self._redis.hset(
            f"{self.BULL_PREFIX}:{self.BULL_QUEUE}:{job_id}",
            mapping={
                "name": "order.created",
                "data": json.dumps(event.model_dump(mode="json")),
                "opts": job_opts,
                "timestamp": str(int(time.time() * 1000)),
                "delay": "0",
                "priority": "0",
                "attempts": "0",
            },
        )
        self._redis.rpush(f"{self.BULL_PREFIX}:{self.BULL_QUEUE}:wait", job_id)
        return job_id

    def _enqueue_rq(self, event: OrderEvent) -> None:
        """RQ 포맷으로 orders-python 큐에 Job을 추가한다."""
        self._rq_queue.enqueue(
            "bullmq_worker.process_order",
            event.model_dump(mode="json"),
        )

    def publish(self, event: OrderEvent) -> dict:
        bull_job_id = self._enqueue_bullmq(event)
        self._enqueue_rq(event)
        print(f"BullMQProducer: Published event {event.order_id} (BullMQ jobId={bull_job_id})")
        return {"bull_job_id": bull_job_id}


queue = KafkaQueue()
rabbitmq_queue = RabbitMQQueue()
bullmq_producer = BullMQProducer()

@app.on_event("startup")
async def startup_event():
    await queue.start()
    await rabbitmq_queue.start()

@app.on_event("shutdown")
async def shutdown_event():
    await queue.stop()
    await rabbitmq_queue.stop()

class CreateOrderRequest(BaseModel):
    amount: float
    items: list[str]

@app.post("/orders")
async def create_order(req: CreateOrderRequest):
    event = OrderEvent(
        order_id=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()),
        amount=req.amount,
        items=req.items
    )
    await queue.publish_async(event)
    return {"status": "success", "event": event.model_dump()}

@app.post("/rabbitmq/orders")
async def create_rabbitmq_order(req: CreateOrderRequest):
    event = OrderEvent(
        order_id=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()),
        amount=req.amount,
        items=req.items
    )
    await rabbitmq_queue.publish_async(event)
    return {"status": "success", "mq": "rabbitmq", "event": event.model_dump()}

@app.post("/bullmq/orders")
async def create_bullmq_order(req: CreateOrderRequest):
    event = OrderEvent(
        order_id=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()),
        amount=req.amount,
        items=req.items
    )
    result = bullmq_producer.publish(event)
    return {"status": "success", "mq": "bullmq", "event": event.model_dump(), **result}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
