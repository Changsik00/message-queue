import abc
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class OrderEvent(BaseModel):
    order_id: str
    user_id: str
    amount: float
    items: list[str]
    published_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BaseQueue(abc.ABC):
    
    @abc.abstractmethod
    def connect(self) -> None:
        """Connect to the message queue."""
        pass
        
    @abc.abstractmethod
    def publish(self, event: OrderEvent) -> None:
        """Publish an OrderEvent to the queue."""
        pass
        
    @abc.abstractmethod
    def consume(self) -> None:
        """Start consuming events from the queue."""
        pass
