from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models import BaseModel


class Subtask(BaseModel):
    __tablename__ = "subtasks"

    subtask_id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.schedule_id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(300), nullable=False)
    completed = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)

    schedule = relationship("Schedule", back_populates="subtasks")
