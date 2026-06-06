from sqlmodel import SQLModel, Field
import datetime
import uuid


class TableBook(SQLModel, table=True):
    __tablename__ = "books"
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str
    author: str
    publisher: str
    publish_date: datetime.date
    page_count: int
    language: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

    def __repr__(self):
        return f"<Book {self.uid} - {self.title}>"