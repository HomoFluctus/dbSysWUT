from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.schedule import PriorityLevel, ScheduleStatus


class ScheduleCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: PriorityLevel = PriorityLevel.MEDIUM
    status: ScheduleStatus = ScheduleStatus.TODO
    due_date: Optional[datetime] = None
    estimated_minutes: Optional[int] = None
    category_id: Optional[int] = None
    tag_ids: list[int] = []


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
