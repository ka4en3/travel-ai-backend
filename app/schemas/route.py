# app/schemas/route.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ---------- Activity ----------


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
    pass


class ActivityRead(ActivityBase):
    id: int

    class Config:
        from_attributes = True


# ---------- RouteDay ----------


class RouteDayBase(BaseModel):
    day_number: int
    description: Optional[str] = None
    date: Optional[datetime] = None


class RouteDayCreate(RouteDayBase):
    activities: List[ActivityCreate] = []


class RouteDayRead(RouteDayBase):
    id: int
    activities: List[ActivityRead] = []

    class Config:
        from_attributes = True


# ---------- Route ----------


class RouteBase(BaseModel):
    name: str
    origin: str
    destination: str
    duration_days: int
    interests: Optional[List[str]] = None
    budget: float
    is_public: bool = False


class RouteCreate(RouteBase):
    share_code: str
    route_data: Optional[dict] = None
    ai_cache_id: Optional[int] = None
    days: List[RouteDayCreate] = []


class RouteRead(RouteBase):
    id: int
    share_code: str
    created_at: datetime
    updated_at: datetime
    owner_id: int
    last_edited_by: Optional[int] = None
    route_data: Optional[dict] = None
    days: List[RouteDayRead] = []

    class Config:
        from_attributes = True


class RouteShort(BaseModel):
    id: int
    name: str
    destination: str
    duration_days: int

    class Config:
        from_attributes = True


class RouteUpdate(BaseModel):
    name: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    duration_days: Optional[int] = None
    interests: Optional[List[str]] = None
    budget: Optional[float] = None
    is_public: Optional[bool] = None
    route_data: Optional[dict] = None
