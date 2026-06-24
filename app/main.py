from typing import Optional, List
from fastapi import FastAPI, HTTPException, status, Response, Depends
from fastapi import Body
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
import models, schemas
from database import engine, get_db

from dotenv import load_dotenv
import os

load_dotenv()

models.Base.metadata.create_all(bind = engine)

try:
    db_conn = psycopg2.connect(host = os.getenv("DB_HOST"), database = os.getenv("DB_DATABASE"), user = os.getenv("DB_USER"), password = os.getenv("DB_PASSWORD"), cursor_factory=RealDictCursor)

    db_cursor = db_conn.cursor()

    print("Connection to Database Successfull...")
except Exception as e:
    print("Connection to Database Failed!")
    print("Error: ", e)


#----------------------------------------------------------------------

app = FastAPI()

#-----------------------------------------------------------------------

@app.get('/')
def root():
    return {'message': 'Hello World!'}

@app.get('/posts', response_model = List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):

    posts = db.query(models.Post).all()
    return posts



@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def createPost(post: schemas.CreatePost, db: Session = Depends(get_db)):
    created_post = models.Post(**post.model_dump())

    db.add(created_post)
    db.commit()
    db.refresh(created_post)
    return created_post

@app.get("/posts/{id}", response_model=schemas.Post)
def view_post_byID(id: int, db: Session = Depends(get_db)):

    post = db.query(models.Post).filter_by(id=id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post for id: {id} not found")
    
    return post

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post_byID(id: int, db: Session = Depends(get_db)):
    deleted_post = db.query(models.Post).filter_by(id=id)
    
    if deleted_post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post for id: {id} not available to delete")
    
    deleted_post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
   

@app.put("/posts/{id}", status_code=status.HTTP_200_OK, response_model=schemas.Post)
def update_post(post: schemas.UpdatePost, id: int, db: Session = Depends(get_db)):
    
    updated_post = db.query(models.Post).filter_by(id=id)
    
    if updated_post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post for id: {id} not available to update")
    updated_post.update(post.model_dump(), synchronize_session=False)
    db.commit()
    
    return updated_post.first()