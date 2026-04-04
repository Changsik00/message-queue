import sys
import os
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import uuid

# add workers/python to sys.path to resolve base_queue
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'workers', 'python'))
from base_queue import OrderEvent, BaseQueue

app = FastAPI()

class MockQueue(BaseQueue):
    def connect(self) -> None:
        print("MockQueue: Connected")
    
    def publish(self, event: OrderEvent) -> None:
        print(f"MockQueue: Published event {event.order_id} at {event.published_at}")
    
    def consume(self) -> None:
        print("MockQueue: Consuming started")

queue = MockQueue()
queue.connect()

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
    queue.publish(event)
    return {"status": "success", "event": event.model_dump()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
