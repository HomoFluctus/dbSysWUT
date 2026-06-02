from sqlalchemy import Column, ForeignKey, Integer

from app.models import BaseModel


class ScheduleTag(BaseModel):
    __tablename__ = "schedule_tags"

    schedule_id = Column(Integer, ForeignKey("schedules.schedule_id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.tag_id", ondelete="CASCADE"), primary_key=True)
