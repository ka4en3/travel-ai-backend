# app/schemas/user.py

from pydantic import BaseModel, field_validator, EmailStr, model_validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    # both registration options are possible
    # at the create-level will validate that at least one of them is set
    telegram_id: Optional[int] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language: Optional[str] = None
    is_premium: bool = False
    is_bot: bool = False


class UserCreate(UserBase):
    # only for e-mail registration
    password: Optional[str] = None

    @model_validator(mode="after")
    def check_identifiers_and_password(cls, data):
        # check that at least one of the fields is filled in
        if not (data.telegram_id or data.email):
            raise ValueError("Either telegram_id or email must be provided")
        # check that password is provided when registering by email
        if data.email and not data.password:
            raise ValueError("Password is required when registering by email")
        return data

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
