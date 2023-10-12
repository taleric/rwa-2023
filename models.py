from pydantic import BaseModel, Field
from typing import Optional


class UserDb(BaseModel):
    username: str = Field(alias="_id")
    email: str
    hashed_password: str


class UserIn(BaseModel):
    username: str
    email: str
    password: str


class PostIn(BaseModel):
    title: str
    slug: str
    content: Optional[str]
    published: bool = Field(default=False)


class PostDb(PostIn):
    id: str = Field(alias="_id")


class CommentIn(BaseModel):
    comment: str


class CommentDb(CommentIn):
    id: str = Field(alias="_id")
    post_id: str
    username: str
