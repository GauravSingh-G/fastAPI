from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


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