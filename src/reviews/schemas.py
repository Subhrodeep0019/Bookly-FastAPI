from pydantic import BaseModel
from sqlmodel import Field
from uuid import UUID
from datetime import datetime

class ReviewCreateModel(BaseModel):
    rating: int = Field(ge=1, le=5)
    review_text: str

class ReviewResponseModel(BaseModel):
    uid: UUID
    rating: int
    review_text: str
    user_uid: UUID
    book_uid: UUID
    created_at: datetime
