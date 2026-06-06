import uuid

from pydantic import BaseModel
import datetime

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

class ModelCreateBook(BaseModel):
    title: str
    author: str
    publisher: str
    publish_date: datetime.date
    page_count: int
    language: str


class ModelUpdBook(BaseModel):
    title: str | None = None # value can be str or None, default value is None if str not provided
    author: str | None = None
    publisher: str | None = None
    page_count: int | None = None
    language: str | None = None