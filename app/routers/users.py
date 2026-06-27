from fastapi import status, Depends, HTTPException, APIRouter
from database import get_db
from sqlalchemy.orm import Session
import schemas, models, utils


router = APIRouter(
    prefix="/users",
    tags=['Users']
)


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=schemas.OutUser)
def create_user(user: schemas.CreateUser ,db: Session = Depends(get_db)):

    hashed_pwd = utils.hash(user.password)
    user.password = hashed_pwd

    created_user = models.User(**user.model_dump())

    db.add(created_user)
    db.commit()
    db.refresh(created_user)

    return created_user



@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.OutUser)
def get_user_by_ID(id: int, db: Session = Depends(get_db)):
    
    fetched_user = db.query(models.User).filter_by(id=id).first()

    if fetched_user is None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= f"User for id: {id} not found")
    
    return fetched_user