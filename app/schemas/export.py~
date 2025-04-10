from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.models.export import ExportType, ExportStatus


class ExportBase(BaseModel):
    route_id: int
    export_type: ExportType


class ExportCreate(BaseModel):
    route_id: int
    export_type: ExportType


class ExportRead(ExportBase):
    id: int
    user_id: int
    status: ExportStatus
    file_path: Optional[str] = None
    external_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
