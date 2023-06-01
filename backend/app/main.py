from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body, Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from random import randrange

app = FastAPI()

# create a class to define what you want the schema to be
class Post(BaseModel):
    title: str
    content: str


my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1}, {"title": "title of post 2", "content": "content of post 2", "id": 2}]


# Configure CORS settings
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def find_post(id, posts_list):
    for post in posts_list:
        if post["id"] == int(id):
            return post

def find_post_index(id, posts_list):
    for index, post in enumerate(posts_list):
        if post["id"] == int(id):
            return index


# hello world route
@app.get("/")
def root():
    return {"message": "hello world"}


# get all posts
@app.get("/posts")
def get_posts():
    return {"data": my_posts}


# post a post
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    post_dict = post.dict()
    post_dict["id"] = randrange(0,10000000)
    my_posts.append(post_dict)
    print(my_posts)
    return {"your post": post_dict, "all posts": my_posts}


# get one post
@app.get("/posts/{id}")
def get_post(id: int):
    post = find_post(id, my_posts)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"id {id} not found")
    return {"post detail": post}


# delete one post
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = find_post_index(id, my_posts)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"id {id} not found")
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_post_index(id, my_posts)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"id {id} not found")
    post_dict = post.dict()
    my_posts[index] = post_dict
    print(my_posts[index])
    return {"message": f"updated post: {my_posts[index]}"}


