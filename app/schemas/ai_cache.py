from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AICacheBase(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    duration_days: Optional[int] = None
    interests: Optional[List[str]] = None
    budget: Optional[float] = None


class AICacheCreate(AICacheBase):
    original_prompt: Optional[str] = None
    result: dict


class AICacheRead(AICacheBase):
    id: int
    cache_key: str
    prompt_hash: str
    result: dict
    hit_count: int
    source: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    user_id: Optional[int] = None

    class Config:
        from_attributes = True
