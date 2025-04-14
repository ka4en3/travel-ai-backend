# app/schemas/export.py

from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

from models.export import ExportType, ExportStatus


class ExportBase(BaseModel):
    route_id: int
    user_id: int
    export_type: ExportType


class ExportCreate(ExportBase):
    @field_validator("route_id", "user_id")
    @classmethod
    def validate_positive_id(cls, v):
        if v <= 0:
            raise ValueError("ID must be a positive integer")
        return v


class ExportRead(ExportBase):
    id: int
    status: ExportStatus
    file_path: Optional[str] = None
    external_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
