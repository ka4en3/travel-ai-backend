# app/schemas/ai_cache.py

from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


class AICacheBase(BaseModel):
    original_prompt: str
    prompt_hash: str

    origin: str
    destination: str
    duration_days: int
    budget: float
    cache_key: str
    interests: Optional[List[str]] = None

    result: dict

    @field_validator("origin", "destination")
    @classmethod
    def validate_location(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Location must be a non-empty string")
        return value

    @field_validator("duration_days")
    @classmethod
    def validate_duration(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Duration must be at least 1 day")
        return value

    @field_validator("budget")
    @classmethod
    def validate_budget(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("Budget must be greater than zero")
        return value


class AICacheCreate(AICacheBase):
    pass


class AICacheRead(AICacheBase):
    id: int
    hit_count: int
    source: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    user_id: Optional[int] = None

    class Config:
        from_attributes = True
