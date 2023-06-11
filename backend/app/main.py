# general imports
from typing import Optional, List

# fastapi imports
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body, Optional
from fastapi.middleware.cors import CORSMiddleware
from . import schemas

# postgres imports
import psycopg2
from psycopg2.extras import RealDictCursor

# sqlalchemy imports
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db

# env var imports
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

# connect to postgres for direct sql queries
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


# boilerplate to configure CORS settings to let fastapi calls work from browswer with React
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


# funcs to find posts by id for sql directly
"""def find_post(id, posts_list):
    for post in posts_list:
        if post["id"] == int(id):
            return post

def find_post_index(id, posts_list):
    for index, post in enumerate(posts_list):
        if post["id"] == int(id):
            return index"""


# FASTAPI ROUTES #


# get all posts
@app.get("/posts", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    
    posts = db.query(models.Post).all()
    
    # (alternative) raw sql 
    # cursor.execute(""" SELECT * FROM posts""")
    # posts = cursor.fetchall()

    return posts


# post a post
@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    
    
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
    
    return new_post


# get one post
@app.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):

    post = db.query(models.Post).filter(models.Post.id == id).first()

    # (alternative) with sql directly
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s""", (str(id)))
    # post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"id {id} not found")

    print(post)
    return post


# delete one post
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):


    post_to_delete = db.query(models.Post).filter(models.Post.id == id).first()
    # (alternative) with sql directly
    # index = cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", (str(id),))
    # deleted_post = cursor.fetchone()
    
    if not post_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"id {id} not found")

    db.delete(post_to_delete)
    
    db.commit()
    # (alternative) with sql directly
    #conn.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# update one post
@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):


    post_query = db.query(models.Post).filter(models.Post.id == id)
    post_to_update = post_query.first()
    # (alternative) with sql directly
    # cursor.execute("""UPDATE posts SET title = %s, content= %s WHERE id = %s Returning * """, (post.title, post.content, str(id)))
    # updated_post = cursor.fetchone()

    if not post_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"id {id} not found")
    
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    # (alternative) with sql directly
    # conn.commit()

    return post_query.first()

"""
# create a user
@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.User, db: Session = Depends(get_db)):
    print(user)
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
"""