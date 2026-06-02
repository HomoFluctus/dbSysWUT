from datetime import date, datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.recurring_rule import RecurringRule
from app.models.schedule import Schedule
from app.services.recurring_service import expand_recurring_dates


async def get_month_calendar(db: AsyncSession, user_id: int, year: int, month: int) -> list[Schedule]:
    start_date = datetime(year, month, 1, tzinfo=timezone.utc)
    if month == 12:
        end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc)

    stmt = (
        select(Schedule)
        .where(Schedule.user_id == user_id)
        .where(
            or_(
                Schedule.due_date.between(start_date, end_date),
                Schedule.recurring.has(
                    RecurringRule.start_date <= end_date.date(),
                ),
            )
        )
        .options(
            selectinload(Schedule.category),
            selectinload(Schedule.tags),
            selectinload(Schedule.recurring),
            selectinload(Schedule.subtasks),
        )
        .order_by(Schedule.due_date, Schedule.priority.desc())
    )
    result = await db.execute(stmt)
    schedules = list(result.unique().scalars().all())

    range_start = start_date.date()
    range_end = (end_date - __import__('datetime').timedelta(days=1)).date()
    return _expand_recurring(schedules, range_start, range_end)


async def get_week_calendar(db: AsyncSession, user_id: int, date_str: str) -> list[Schedule]:
    target = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
    start_date = target.replace(hour=0, minute=0, second=0, microsecond=0)
    weekday = start_date.weekday()
    start_date = start_date.replace(day=start_date.day - weekday)
    end_date = start_date.replace(day=start_date.day + 7)

    stmt = (
        select(Schedule)
        .where(Schedule.user_id == user_id)
        .where(
            or_(
                Schedule.due_date.between(start_date, end_date),
                Schedule.recurring.has(
                    RecurringRule.start_date <= end_date.date(),
                ),
            )
        )
        .options(
            selectinload(Schedule.category),
            selectinload(Schedule.tags),
            selectinload(Schedule.recurring),
            selectinload(Schedule.subtasks),
        )
        .order_by(Schedule.due_date)
    )
    result = await db.execute(stmt)
    schedules = list(result.unique().scalars().all())

    range_start = start_date.date()
    range_end = (end_date - __import__('datetime').timedelta(days=1)).date()
    return _expand_recurring(schedules, range_start, range_end)


async def get_day_calendar(db: AsyncSession, user_id: int, date_str: str) -> list[Schedule]:
    target = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
    start_date = target.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date.replace(hour=23, minute=59, second=59)

    stmt = (
        select(Schedule)
        .where(Schedule.user_id == user_id)
        .where(
            or_(
                Schedule.due_date.between(start_date, end_date),
                Schedule.recurring.has(
                    RecurringRule.start_date <= end_date.date(),
                ),
            )
        )
        .options(
            selectinload(Schedule.category),
            selectinload(Schedule.tags),
            selectinload(Schedule.recurring),
            selectinload(Schedule.subtasks),
        )
        .order_by(Schedule.priority.desc())
    )
    result = await db.execute(stmt)
    schedules = list(result.unique().scalars().all())

    return _expand_recurring(schedules, start_date.date(), end_date.date())


def _expand_recurring(schedules: list[Schedule], range_start: date, range_end: date) -> list[dict]:
    """Expand schedules with recurring rules into dict entries, duplicating for each occurrence date."""
    from app.schemas.schedule import ScheduleOut

    expanded: list[dict] = []

    for s in schedules:
        if s.recurring and s.recurring.start_date:
            dates = expand_recurring_dates(s.recurring, range_start, range_end)
            if dates:
                base = ScheduleOut.model_validate(s).model_dump()
                for d in dates:
                    entry = dict(base)
                    entry["due_date"] = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
                    expanded.append(entry)
                continue

        expanded.append(ScheduleOut.model_validate(s).model_dump())

    def _sort_key(item):
        d = item.get("due_date")
        if d is None:
            return (1, "")
        # Normalize to UTC for comparison
        if hasattr(d, 'tzinfo') and d.tzinfo is not None:
            return (0, d.isoformat())
        return (0, d.isoformat() if hasattr(d, 'isoformat') else str(d))
    expanded.sort(key=_sort_key)
    return expanded
