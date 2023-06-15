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


# class for creating user
class UserCreate(BaseModel):
    email: str
    password: str

# class to output after creating user
class UserOut(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        orm_mode = True

# class to for user login
class UserLogin(BaseModel):
    email: str
    password: str