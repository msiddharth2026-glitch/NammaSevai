from pydantic import BaseModel, Field
from typing import Optional

class FeedbackCreate(BaseModel):
    session_id: Optional[str] = None
    participant_category: Optional[str] = Field(None, max_length=64)
    preferred_language: str = Field("ta", min_length=2, max_length=16)
    ease_of_use_rating: int = Field(..., ge=1, le=5)
    clarity_rating: int = Field(..., ge=1, le=5)
    usefulness_rating: int = Field(..., ge=1, le=5)
    problems_encountered: Optional[str] = Field(None, max_length=2000)
    suggestions: Optional[str] = Field(None, max_length=2000)

class FeedbackResponse(BaseModel):
    id: int
    message: str
    status: str = "received"
