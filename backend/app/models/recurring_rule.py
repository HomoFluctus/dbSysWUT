from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models import BaseModel


class RecurringRule(BaseModel):
    __tablename__ = "recurring_rules"

    rule_id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.schedule_id", ondelete="CASCADE"), unique=True, nullable=False)
    freq = Column(String(10), nullable=False)
    interval = Column(Integer, default=1)
    weekdays = Column(String(30), nullable=True)
    monthday = Column(Integer, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    count = Column(Integer, nullable=True)

    schedule = relationship("Schedule", back_populates="recurring")
