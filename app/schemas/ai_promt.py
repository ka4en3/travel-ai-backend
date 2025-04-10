from pydantic import BaseModel
from typing import List


class AIPromptRequest(BaseModel):
    origin: str
    destination: str
    duration_days: int
    interests: List[str]
    budget: float
