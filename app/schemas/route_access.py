from pydantic import BaseModel

from app.models.route_access import RouteRole


class RouteAccessBase(BaseModel):
    user_id: int
    route_id: int
    role: RouteRole


class RouteAccessCreate(RouteAccessBase):
    pass


class RouteAccessRead(RouteAccessBase):
    class Config:
        from_attributes = True
