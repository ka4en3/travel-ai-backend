# app/schemas/common.py

from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    detail: str


class SuccessResponse(BaseModel):
    message: str


class PaginationMeta(BaseModel):
    total: int
    page: int
    size: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
