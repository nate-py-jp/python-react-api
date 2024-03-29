from typing import Optional, List
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from fastapi.params import Body, Optional
from .. import models, schemas, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

# get all posts
@router.get("/", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):
    
    posts = db.query(models.Post).all()
    
    # (alternative) raw sql 
    # cursor.execute(""" SELECT * FROM posts""")
    # posts = cursor.fetchall()

    return posts


# post a post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):
    
    
    print(user_id)
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
@router.get("/{id}")
def get_post(id: int, db: Session = Depends(get_db)):

    post_query = db.query(models.Post).filter(models.Post.id == id).first()

    # (alternative) with sql directly
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s""", (str(id)))
    # post = cursor.fetchone()
    if not post_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"id {id} not found")

    return post_query


# delete one post
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):


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


## debug update post NEEDED, it can't find the id ##

# update one post
@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):

    post_query = db.query(models.Post).filter(models.Post.id == id).first()

    # (alternative) with sql directly
    # cursor.execute("""UPDATE posts SET title = %s, content= %s WHERE id = %s Returning * """, (post.title, post.content, str(id)))
    # updated_post = cursor.fetchone()

    if not post_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"id {id} not found")
    
    #post_query.update(post.dict(), synchronize_session=False)

    post_query.title = post.title
    post_query.content = post.content

    db.commit()
    # (alternative) with sql directly
    # conn.commit()

    return post_query