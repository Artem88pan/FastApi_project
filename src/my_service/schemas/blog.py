from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(...,min_length=1, max_length=100)

class CategoryRead(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}

class ArticleBase(BaseModel):
    title: str
    content: str
    category_id: int
    image_url: Optional[str] = None


class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None

class ArticleRead(BaseModel):
    id: int
    title: str
    content: str
    image_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class ArticleListResponse(BaseModel):
    items: List[ArticleRead]
    total: int
    page_number: int
    page_size: int
    model_config = {"from_attributes": True}



