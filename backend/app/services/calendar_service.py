from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.recurring_rule import RecurringRule
from app.models.schedule import Schedule


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
        )
        .order_by(Schedule.due_date, Schedule.priority.desc())
    )
    result = await db.execute(stmt)
    return list(result.unique().scalars().all())


async def get_week_calendar(db: AsyncSession, user_id: int, date_str: str) -> list[Schedule]:
    target = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
    start_date = target.replace(hour=0, minute=0, second=0, microsecond=0)
    weekday = start_date.weekday()
    start_date = start_date.replace(day=start_date.day - weekday)
    end_date = start_date.replace(day=start_date.day + 7)

    stmt = (
        select(Schedule)
        .where(Schedule.user_id == user_id)
        .where(Schedule.due_date.between(start_date, end_date))
        .options(selectinload(Schedule.category), selectinload(Schedule.tags))
        .order_by(Schedule.due_date)
    )
    result = await db.execute(stmt)
    return list(result.unique().scalars().all())


async def get_day_calendar(db: AsyncSession, user_id: int, date_str: str) -> list[Schedule]:
    target = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
    start_date = target.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date.replace(hour=23, minute=59, second=59)

    stmt = (
        select(Schedule)
        .where(Schedule.user_id == user_id)
        .where(Schedule.due_date.between(start_date, end_date))
        .options(selectinload(Schedule.category), selectinload(Schedule.tags))
        .order_by(Schedule.priority.desc())
    )
    result = await db.execute(stmt)
    return list(result.unique().scalars().all())
