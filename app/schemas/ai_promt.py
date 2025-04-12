# app/schemas/ai_promt.py

from pydantic import BaseModel, field_validator


class AIPromt(BaseModel):
    prompt: str

    @field_validator("prompt", mode="before")
    def validate_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Prompt must not be empty")
        return v
