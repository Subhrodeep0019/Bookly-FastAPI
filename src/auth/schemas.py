from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class UserCreateModel(BaseModel):
    username: str = Field(max_length=15)
    f_name: str = Field(max_length=25)
    l_name: str = Field(max_length=25)
    email: str = Field(max_length=50)
    pswd: str = Field(min_length=6)

class UserResponseModel(BaseModel):
    uid: UUID
    username: str
    email: str
    f_name: str
    l_name: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime

class LoginModel(BaseModel):
    email: str
    pswd: str