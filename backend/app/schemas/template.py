from typing import Optional

from pydantic import BaseModel


class TemplateCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    estimated_minutes: Optional[int] = None
    category_id: Optional[int] = None
    tag_ids: list[int] = []


class TemplateOut(BaseModel):
    template_id: int
    user_id: int
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    estimated_minutes: Optional[int] = None
    category_id: Optional[int] = None
    tag_ids: Optional[str] = None

    class Config:
        from_attributes = True
