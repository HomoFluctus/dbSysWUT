from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models import BaseModel


class ScheduleDependency(BaseModel):
    __tablename__ = "schedule_dependencies"
    __table_args__ = (
        UniqueConstraint("schedule_id", "depends_on_id", name="uq_schedule_depends"),
    )

    dependency_id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.schedule_id", ondelete="CASCADE"), nullable=False)
    depends_on_id = Column(Integer, ForeignKey("schedules.schedule_id", ondelete="CASCADE"), nullable=False)
    dep_type = Column(String(20), default="blocks")

    schedule = relationship("Schedule", foreign_keys=[schedule_id], back_populates="dependencies")
