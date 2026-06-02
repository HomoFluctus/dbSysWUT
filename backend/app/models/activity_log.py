from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.models import BaseModel


class ActivityLog(BaseModel):
    __tablename__ = "activity_log"

    log_id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.schedule_id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(20), nullable=False)
    field_changed = Column(String(50), nullable=True)
    old_value = Column(String(200), nullable=True)
    new_value = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    schedule = relationship("Schedule", back_populates="activity_logs")
    user = relationship("User", back_populates="activity_logs")
