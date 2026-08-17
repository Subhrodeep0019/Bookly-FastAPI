import uuid
from typing import List
from pydantic import BaseModel
import datetime
from src.reviews.schemas import ReviewResponseModel


class ModelBook(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    publish_date: datetime.date
    page_count: int
    language: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

class BookWithReview(ModelBook):
    reviews: List[ReviewResponseModel]

class ModelCreateBook(BaseModel):
    title: str
    author: str
    publisher: str
    publish_date: datetime.date
    page_count: int
    language: str


class ModelUpdBook(BaseModel):
    title: str | None = None
    author: str | None = None
    publisher: str | None = None
    publish_date: datetime.date | None = None
    page_count: int | None = None
    language: str | None = None