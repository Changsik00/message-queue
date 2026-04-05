from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel

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
