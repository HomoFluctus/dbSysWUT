import enum

from sqlalchemy import (Column, DateTime, Enum, Float, ForeignKey, Index,
                        Integer, String, Text, func)
from sqlalchemy.orm import relationship

from app.models import BaseModel


class PriorityLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ScheduleStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class Schedule(BaseModel):
    __tablename__ = "schedules"
    __table_args__ = (
        Index("ix_schedules_user_due", "user_id", "due_date"),
        Index("ix_schedules_user_status", "user_id", "status"),
    )

    schedule_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="SET NULL"), nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Enum(PriorityLevel), default=PriorityLevel.MEDIUM, index=True)
    status = Column(Enum(ScheduleStatus), default=ScheduleStatus.TODO, index=True)
    due_date = Column(DateTime(timezone=True), nullable=True, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    estimated_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="schedules")
    category = relationship("Category", back_populates="schedules")
    tags = relationship("Tag", secondary="schedule_tags", back_populates="schedules")
    recurring = relationship("RecurringRule", uselist=False, back_populates="schedule", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="schedule", cascade="all, delete-orphan")
    dependencies = relationship(
        "ScheduleDependency",
        foreign_keys="[ScheduleDependency.schedule_id]",
        back_populates="schedule",
        cascade="all, delete-orphan",
    )
    activity_logs = relationship("ActivityLog", back_populates="schedule", cascade="all, delete-orphan")
    subtasks = relationship("Subtask", back_populates="schedule", cascade="all, delete-orphan")
