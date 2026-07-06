from sqlmodel import SQLModel, Field, Relationship
from datetime import date, datetime
from uuid import UUID, uuid4
from typing import Optional, List


class TableBook(SQLModel, table=True):
    __tablename__ = "books"
    uid: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    author: str
    publisher: str
    publish_date: date
    page_count: int
    language: str
    user_uid: Optional[UUID] = Field(default=None, foreign_key="users.uid")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    user: Optional["User"] = Relationship(back_populates="books")
    reviews: List["Reviews"] = Relationship(
        back_populates="book",
        sa_relationship_kwargs={'lazy': 'selectin'}
    )

    def __repr__(self):
        return f"<Book {self.uid} - {self.title}>"

class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str
    email: str
    f_name: str
    l_name: str
    is_verified: bool = False
    pswd: str
    role: str = Field(default="user", nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    books: List["TableBook"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={'lazy': 'selectin'}
    )
    reviews: List["Reviews"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={'lazy': 'selectin'}
    )

    def __repr__(self):
        return f"user: {self.username}"


class Reviews(SQLModel, table=True):
    __tablename__ = "reviews"
    uid: UUID = Field(default_factory=uuid4, primary_key=True)
    rating: int = Field(le=5)
    review_text: str
    user_uid: Optional[UUID] = Field(default=None, foreign_key="users.uid")
    book_uid: Optional[UUID] = Field(default=None, foreign_key="books.uid")
    created_at: datetime = Field(default_factory=datetime.now)
    user: Optional["User"] = Relationship(back_populates="reviews")
    book: Optional["TableBook"] = Relationship(back_populates="reviews")