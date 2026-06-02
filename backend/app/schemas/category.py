from typing import Optional

from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    color: str = "#6366f1"


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class CategoryOut(BaseModel):
    category_id: int
    user_id: int
    name: str
    color: str
    is_default: bool

    class Config:
        from_attributes = True
