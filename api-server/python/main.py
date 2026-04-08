import sys
import os
import json
import asyncio
from aiokafka import AIOKafkaProducer
import aio_pika
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

queue = KafkaQueue()
rabbitmq_queue = RabbitMQQueue()

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
