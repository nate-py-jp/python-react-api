from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body, Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
from . import models
from sqlalchemy.orm import Session
from .database import engine, get_db
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

db_name = os.environ.get("DB_NAME")
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT")
db_username = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# create a class to define schema
class Post(BaseModel):
    title: str
    content: str
    published: bool = True

while True:
    try:
        conn = psycopg2.connect(
            host = db_host, 
            database=db_name, 
            user=db_username, 
            password=db_password, 
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        print("db conn OK!")
        break
    except Exception as error:
        print(f"error in getting conn:", error)


# Configure CORS settings to let fastapi calls work from browswer in JS world
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

# funcs to find posts by id
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


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"posts": posts}


# get all posts from db
@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    
    posts = db.query(models.Post).all()
    
    # (alternative) raw sql 
    # cursor.execute(""" SELECT * FROM posts""")
    # posts = cursor.fetchall()


    return {"data": posts}


# post a post
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post, db: Session = Depends(get_db)):
    
    
    new_post = models.Post(**post.dict())
    # (alternative)
    # new_post = models.Post(title=post.title, content=post.content)
    
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)


    # (alternative) with sql directly
    # post_dict = post.dict()
    # cursor.execute(""" INSERT INTO posts (title, content) VALUES (%s, %s) RETURNING *""", (post.title, post.content))
    # new_post = cursor.fetchone()
    # conn.commit()
    return {"your post": new_post}


# get one post
@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):

    post = db.query(models.Post).filter(models.Post.id == id).first()
    print(post)

    #cursor.execute(""" SELECT * FROM posts WHERE id = %s""", (str(id)))
    #post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"id {id} not found")
    return {"post detail": post}


# delete one post
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    index = cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", (str(id),))
    deleted_post = cursor.fetchone()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"id {id} not found")
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# update one post
@app.put("/posts/{id}")
def update_post(id: int, post: Post):

    cursor.execute("""UPDATE posts SET title = %s, content= %s WHERE id = %s Returning * """, (post.title, post.content, str(id)))
    updated_post = cursor.fetchone()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"id {id} not found")
    conn.commit()
    return {"message": f"updated post: {updated_post}"}
