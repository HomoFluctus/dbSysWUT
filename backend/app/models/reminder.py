from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Index,
                        Integer, String)
from sqlalchemy.orm import relationship

from app.models import BaseModel


class Reminder(BaseModel):
    __tablename__ = "reminders"
    __table_args__ = (
        Index("ix_reminders_remind_at_sent", "remind_at", "sent"),
    )

    reminder_id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.schedule_id", ondelete="CASCADE"), nullable=False, index=True)
    remind_at = Column(DateTime(timezone=True), nullable=False)
    method = Column(String(10), default="push")
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)

    schedule = relationship("Schedule", back_populates="reminders")
