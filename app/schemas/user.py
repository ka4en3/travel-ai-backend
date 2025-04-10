from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    language: Optional[str] = "en"
    is_premium: bool = False
    is_bot: bool = False


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
    first_name: str

    class Config:
        from_attributes = True
