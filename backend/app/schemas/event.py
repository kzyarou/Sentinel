from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class EventBase(BaseModel):
    event_type: str = Field(..., max_length=100)
    source: str = Field(..., max_length=100)
    timestamp: datetime
    host: Optional[str] = Field(None, max_length=255)
    user: Optional[str] = Field(None, max_length=255)
    normalized_data: Optional[Dict[str, Any]] = None
    raw_data: Optional[str] = None


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    event_type: Optional[str] = Field(None, max_length=100)
    source: Optional[str] = Field(None, max_length=100)
    timestamp: Optional[datetime] = None
    host: Optional[str] = Field(None, max_length=255)
    user: Optional[str] = Field(None, max_length=255)
    normalized_data: Optional[Dict[str, Any]] = None
    raw_data: Optional[str] = None


class EventInDBBase(EventBase):
    id: str
    ingestion_timestamp: datetime

    class Config:
        from_attributes = True


class Event(EventInDBBase):
    pass
