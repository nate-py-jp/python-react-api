from pydantic import BaseModel
from datetime import datetime

# class to define post schema basic model
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


# class inheriting from base for creating post
class PostCreate(PostBase):
    pass

class Post(PostBase):
    created_at: datetime

    class Config:
        orm_mode = True


class User(BaseModel):
    email: str

    class Config:
        orm_mode = True