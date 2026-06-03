from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models import BaseModel


class ScheduleTemplate(BaseModel):
    __tablename__ = "schedule_templates"

    template_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(10), default="medium")
    estimated_minutes = Column(Integer, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="SET NULL"), nullable=True)
    tag_ids = Column(Text, nullable=True)  # JSON array stored as text

    user = relationship("User")
