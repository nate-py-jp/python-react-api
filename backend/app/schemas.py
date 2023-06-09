from pydantic import BaseModel

# class to define post schema basic model
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


# class inheriting from base for creating post
class PostCreate(PostBase):
    pass