from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models import BaseModel


class Tag(BaseModel):
    __tablename__ = "tags"

    tag_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    color = Column(String(7), default="#a855f7")

    user = relationship("User", back_populates="tags")
    schedules = relationship("Schedule", secondary="schedule_tags", back_populates="tags")
