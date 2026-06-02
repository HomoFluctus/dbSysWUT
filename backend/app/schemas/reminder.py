from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReminderCreate(BaseModel):
    remind_at: datetime
    method: str = "push"


class ReminderUpdate(BaseModel):
    remind_at: Optional[datetime] = None
    method: Optional[str] = None


class ReminderOut(BaseModel):
    reminder_id: int
    schedule_id: int
    remind_at: datetime
    method: str
    sent: bool
    sent_at: Optional[datetime] = None

    class Config:
        from_attributes = True
