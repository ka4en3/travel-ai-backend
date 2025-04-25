# app/schemas/user.py

from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    # both registration options are possible
    # at the create-level will validate that at least one of them is
    telegram_id: Optional[int] = None
    email: Optional[EmailStr] = None

    @field_validator("telegram_id", "email", mode="before")
    @classmethod
    def at_least_one_identifier(cls, value, values, **kwargs):
        # Pydantic v2 style: check that at least one of the fields is filled in
        if not value and not (values.get("telegram_id") or values.get("email")):
            raise ValueError("Either telegram_id or email is required")
        return value

class UserCreate(UserBase):
    # only for e-mail registration
    password: Optional[str] = None

    @field_validator("password", mode="before")
    @classmethod
    def password_required_if_email(cls, value, values, **kwargs):
        if values.get("email") and not value:
            raise ValueError("Password is required when registering by email")
        return value


class UserRead(UserBase):
    id: int
    email: Optional[EmailStr]
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_active: datetime

    class Config:
        from_attributes = True

class UserShort(BaseModel):
    id: int
    email: Optional[EmailStr]
    first_name: Optional[str]

    class Config:
        from_attributes = True
