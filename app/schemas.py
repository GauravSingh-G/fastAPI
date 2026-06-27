from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr, Field
from datetime import datetime
import fastapi


class BasePost(BaseModel):
    title: str
    content: str
    published: Optional[bool] = True

class CreatePost(BasePost):
    pass

class UpdatePost(BasePost):
    pass

class Post(CreatePost):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CreateUser(BaseModel):
    email: EmailStr
    password: str

class OutUser(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)