# app/schemas/route.py

from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, field_validator
from .route_access import RouteAccessCreate, RouteAccessRead
from .export import ExportCreate, ExportRead

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
    date: Optional[date]
    description: Optional[str] = None


class RouteDayCreate(RouteDayBase):
    # date: Optional[date] = None
    activities: List[ActivityCreate] = []

    @field_validator("day_number")
    @classmethod
    def validate_day_number(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Day number must be greater than zero")
        return value


class RouteDayRead(RouteDayBase):
    id: int
    # date: Optional[date]
    activities: List[ActivityRead] = []

    class Config:
        from_attributes = True


# ================= ROUTE ================= #


class RouteGenerateRequest(BaseModel):
    origin: str
    destination: str
    duration_days: int
    budget: float
    interests: List[str] = []
    is_public: bool = False

    @field_validator("origin", "destination")
    @classmethod
    def validate_location(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Location must be a non-empty string")
        return v

    @field_validator("duration_days")
    @classmethod
    def validate_duration(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Duration must be at least 1 day")
        return v

    @field_validator("budget")
    @classmethod
    def validate_budget(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Budget must be greater than zero")
        return v


class RouteCreate(RouteGenerateRequest):
    name: str
    share_code: str
    owner_id: int
    route_data: dict
    days: List[RouteDayCreate] = []
    ai_cache_id: Optional[int] = None
    last_edited_by: Optional[int] = None

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
    def validate_cache_id(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("ID(ai_cache_id) must be a positive integer")
        return value


class RouteShort(BaseModel):
    id: int
    name: str
    owner_id: int
    share_code: str
    origin: str
    destination: str
    duration_days: int
    budget: float
    interests: List[str]

    class Config:
        from_attributes = True


class RouteRead(RouteShort):
    route_data: dict
    days: List[RouteDayRead] = []
    ai_cache_id: Optional[int]
    last_edited_by: Optional[int]
    access_list: List[RouteAccessRead] = []
    exports: List[ExportRead] = []
    is_public: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
