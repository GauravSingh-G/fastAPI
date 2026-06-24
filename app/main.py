from typing import Optional
from fastapi import FastAPI, HTTPException, status, Response, Depends
from pydantic import BaseModel
from fastapi import Body
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy.orm import Session
import models
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

all_posts = [{"title": "Example Post", "content": "Example Content", "id": 1},
             {"title": "Visit to China", "content": "Tour was amazing!", "id": 2}]

class Post(BaseModel):
    title: str
    content: str
    published: Optional[bool] = True

def find_post(id: int):
    for i in all_posts:
      if i["id"]==id:
           return i

def find_index_of_Post(id: int):
    for i, p in enumerate(all_posts):
        if p["id"] == id:
            return i

#-----------------------------------------------------------------------

@app.get('/')
def root():
    return {'message': 'Hello World!'}

@app.get("/sqlalchemy")
def test(db: Session = Depends(get_db)):
    return {'status': 'fine'}

@app.get('/posts')
def get_posts():
    db_cursor.execute("""SELECT * FROM posts""")
    posts = db_cursor.fetchall()
    return {'data': posts}

"""
@app.post('/posts')
def createPost(uploaded_post: dict = Body(...)):
    print(uploaded_post)
    return {'data': f'title: {uploaded_post["title"]}, content: {uploaded_post["content"]}'}
"""

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def createPost(post: Post):
    # dict_post = post.model_dump()
    # dict_post["id"] = randrange(1, 1000000)
    # all_posts.append(dict_post)
    db_cursor.execute("""INSERT INTO posts (title, content) VALUES (%s, %s) RETURNING *""", (post.title, post.content))
    created_post = db_cursor.fetchone()
    db_conn.commit()
    return {'data': created_post}

@app.get("/posts/{id}")
def view_post_byID(id: int):

    db_cursor.execute("""SELECT * FROM posts WHERE id=%s""", (str(id), ))
    post = db_cursor.fetchone()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post for id: {id} not found")
    
    return post

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post_byID(id: int):
    db_cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id), ))
    deleted_post = db_cursor.fetchone()

    db_conn.commit()
    if deleted_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post for id: {id} not available to delete")
        
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}", status_code=status.HTTP_200_OK)
def update_post(post: Post, id: int):
    # index = find_index_of_Post(id)
    db_cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))
    updated_post = db_cursor.fetchone()
    db_conn.commit()
    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post for id: {id} not available to update")
    
    return {"updated_post": updated_post}