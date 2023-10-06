from pydantic import BaseModel, Field
from typing import Optional

class UserIn(BaseModel):
    username: str
    email: str
    password: str

class UserDb(BaseModel):
    username: str = Field(alias="_id")
    email: str
    hashed_password: str

class TodoIn(BaseModel):
    title: str
    description: Optional[str]

class TodoDb(BaseModel):
    id: str = Field(alias="_id")
    username: str
    title: str
    description: Optional[str]