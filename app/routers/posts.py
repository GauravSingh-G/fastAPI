from fastapi import Depends, status, HTTPException, Response, APIRouter
from sqlalchemy.orm import Session
import schemas, models
from database import get_db
from typing import List

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

@router.get("/", response_model = List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):

    posts = db.query(models.Post).all()
    return posts



@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def createPost(post: schemas.CreatePost, db: Session = Depends(get_db)):
    created_post = models.Post(**post.model_dump())

    db.add(created_post)
    db.commit()
    db.refresh(created_post)
    return created_post

@router.get("/{id}", response_model=schemas.Post)
def view_post_byID(id: int, db: Session = Depends(get_db)):

    post = db.query(models.Post).filter_by(id=id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post for id: {id} not found")
    
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post_byID(id: int, db: Session = Depends(get_db)):
    deleted_post = db.query(models.Post).filter_by(id=id)
    
    if deleted_post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post for id: {id} not available to delete")
    
    deleted_post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
   

@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.Post)
def update_post(post: schemas.UpdatePost, id: int, db: Session = Depends(get_db)):
    
    post_query = db.query(models.Post).filter_by(id=id)
    
    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post for id: {id} not available to update")
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()

    updated_post = post_query.first()
    
    return updated_post
