# app/schemas/route_access.py

from pydantic import BaseModel, field_validator

from models.route_access import RouteRole


class RouteAccessBase(BaseModel):
    user_id: int
    route_id: int
    role: RouteRole = RouteRole.VIEWER


class RouteAccessCreate(RouteAccessBase):
    @field_validator("user_id", "route_id")
    @classmethod
    def validate_ids(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("ID must be a positive integer")
        return value


class RouteAccessRead(RouteAccessBase):
    class Config:
        from_attributes = True
