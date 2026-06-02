from datetime import date
from typing import Optional

from pydantic import BaseModel


class RecurringRuleCreate(BaseModel):
    freq: str
    interval: int = 1
    weekdays: Optional[str] = None
    monthday: Optional[int] = None
    start_date: date
    end_date: Optional[date] = None
    count: Optional[int] = None


class RecurringRuleUpdate(BaseModel):
    freq: Optional[str] = None
    interval: Optional[int] = None
    weekdays: Optional[str] = None
    monthday: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    count: Optional[int] = None


class RecurringRuleOut(BaseModel):
    rule_id: int
    schedule_id: int
    freq: str
    interval: int
    weekdays: Optional[str] = None
    monthday: Optional[int] = None
    start_date: date
    end_date: Optional[date] = None
    count: Optional[int] = None

    class Config:
        from_attributes = True
