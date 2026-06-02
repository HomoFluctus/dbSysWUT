from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models import BaseModel


class Category(BaseModel):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    color = Column(String(7), default="#6366f1")
    is_default = Column(Boolean, default=False)

    user = relationship("User", back_populates="categories")
    schedules = relationship("Schedule", back_populates="category")
