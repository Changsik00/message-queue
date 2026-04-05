import sys
import os
import json
import asyncio
from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import uuid

# add workers/python to sys.path to resolve base_queue
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'workers', 'python'))
from base_queue import OrderEvent, BaseQueue

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

queue = KafkaQueue()

@app.on_event("startup")
async def startup_event():
    await queue.start()

@app.on_event("shutdown")
async def shutdown_event():
    await queue.stop()

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
