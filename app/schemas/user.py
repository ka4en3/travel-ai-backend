# app/schemas/user.py

from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language: Optional[str] = None
    is_premium: bool = False
    is_bot: bool = False

    @field_validator("telegram_id")
    @classmethod
    def validate_telegram_id(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Telegram ID must be a positive integer")
        return value


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
    created_at: datetime
    last_active: datetime

    class Config:
        from_attributes = True


class UserShort(BaseModel):
    id: int
    telegram_id: int
    first_name: str

    class Config:
        from_attributes = True
