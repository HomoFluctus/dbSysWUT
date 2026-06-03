from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ActivityLogOut(BaseModel):
    log_id: int
    schedule_id: int
    user_id: int
    action: str
    field_changed: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    schedule_title: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
