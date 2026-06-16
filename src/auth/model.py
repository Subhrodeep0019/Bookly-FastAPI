from uuid import UUID, uuid4
from datetime import datetime
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str
    email: str
    f_name: str
    l_name: str
    is_verified: bool = False
    pswd: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def __repr__(self):
        return f"user: {self.username}"