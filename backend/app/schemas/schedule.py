from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from app.config import TZ
from app.models.schedule import PriorityLevel, ScheduleStatus


def _ensure_beijing_tz(dt: datetime | None) -> datetime | None:
    """If datetime is naive, assume it represents Beijing time (UTC+8)."""
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=TZ)
    return dt


class ScheduleCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: PriorityLevel = PriorityLevel.MEDIUM
    status: ScheduleStatus = ScheduleStatus.TODO
    due_date: Optional[datetime] = None
    estimated_minutes: Optional[int] = None
    category_id: Optional[int] = None
    tag_ids: list[int] = []

    @field_validator("due_date", mode="after")
    @classmethod
    def coerce_due_date(cls, v):
        return _ensure_beijing_tz(v)


class ScheduleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityLevel] = None
    status: Optional[ScheduleStatus] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_minutes: Optional[int] = None
    category_id: Optional[int] = None
    tag_ids: Optional[list[int]] = None

    @field_validator("due_date", mode="after")
    @classmethod
    def coerce_due_date(cls, v):
        return _ensure_beijing_tz(v)


class StatusUpdate(BaseModel):
    status: ScheduleStatus


class ScheduleOut(BaseModel):
    schedule_id: int
    user_id: int
    category_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    priority: PriorityLevel
    status: ScheduleStatus
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_minutes: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    subtasks: list["SubtaskOut"] = []

    class Config:
        from_attributes = True


class ScheduleDetailOut(ScheduleOut):
    category: Optional["CategoryOut"] = None
    tags: list["TagOut"] = []
    recurring: Optional["RecurringRuleOut"] = None
    reminders: list["ReminderOut"] = []
    subtasks: list["SubtaskOut"] = []

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    per_page: int


from app.schemas.category import CategoryOut  # noqa: E402
from app.schemas.tag import TagOut  # noqa: E402
from app.schemas.reminder import ReminderOut  # noqa: E402
from app.schemas.recurring import RecurringRuleOut  # noqa: E402
from app.schemas.subtask import SubtaskOut  # noqa: E402
