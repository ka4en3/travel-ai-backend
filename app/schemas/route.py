# app/schemas/route.py

from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


# ================= ACTIVITY ================= #


class ActivityBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    cost: Optional[float] = None
    notes: Optional[str] = None
    activity_type: Optional[str] = None
    external_link: Optional[str] = None


class ActivityCreate(ActivityBase):
    @field_validator("name")
    @classmethod
    def name_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Activity name can't be empty")
        return value

    @field_validator("cost")
    @classmethod
    def cost_positive(cls, value: float) -> float:
        if value is not None and value < 0:
            raise ValueError("Cost must be positive")
        return value


class ActivityRead(ActivityBase):
    id: int

    class Config:
        from_attributes = True


# ================= ROUTE DAY ================= #


class RouteDayBase(BaseModel):
    day_number: int
    description: Optional[str] = None
    date: Optional[datetime] = None


class RouteDayCreate(RouteDayBase):
    activities: List[ActivityCreate] = []

    @field_validator("day_number")
    @classmethod
    def validate_day_number(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Day number must be greater than zero")
        return value


class RouteDayRead(RouteDayBase):
    id: int
    activities: List[ActivityRead] = []

    class Config:
        from_attributes = True


# ================= ROUTE ================= #


class RouteBase(BaseModel):
    name: str = "New Route"
    origin: str
    destination: str
    duration_days: int
    budget: float
    owner_id: int
    route_data: dict
    share_code: str
    interests: List[str] = []


class RouteCreate(RouteBase):
    days: List[RouteDayCreate] = []
    ai_cache_id: Optional[int] = None

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

    @field_validator("ai_cache_id")
    @classmethod
    def validate_budget(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("ID(ai_cache_id) must be a positive integer")
        return value


class RouteRead(RouteBase):
    id: int
    name: str
    days: List[RouteDayRead] = []
    created_at: datetime
    updated_at: datetime
    last_edited_by: Optional[int] = None

    class Config:
        from_attributes = True


class RouteShort(BaseModel):
    id: int
    name: str
    share_code: str
    origin: str
    destination: str
    duration_days: int
    budget: float

    class Config:
        from_attributes = True


# class RouteUpdate(BaseModel):
#     name: Optional[str] = None
#     origin: Optional[str] = None
#     destination: Optional[str] = None
#     duration_days: Optional[int] = None
#     interests: Optional[List[str]] = None
#     budget: Optional[float] = None
#     is_public: Optional[bool] = None
#     route_data: Optional[dict] = None
#
#     @field_validator("origin", "destination")
#     @classmethod
#     def validate_location(cls, value: Optional[str]) -> Optional[str]:
#         if value is not None and not value.strip():
#             raise ValueError("Location must be a non-empty string")
#         return value
#
#     @field_validator("duration_days")
#     @classmethod
#     def validate_duration(cls, value: Optional[int]) -> Optional[int]:
#         if value is not None and value <= 0:
#             raise ValueError("Duration must be at least 1 day")
#         return value
#
#     @field_validator("budget")
#     @classmethod
#     def validate_budget(cls, value: Optional[float]) -> Optional[float]:
#         if value is not None and value <= 0:
#             raise ValueError("Budget must be greater than zero")
#         return value
