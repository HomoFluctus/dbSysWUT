from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.recurring_rule import RecurringRule
from app.models.schedule import Schedule
from app.schemas.recurring import RecurringRuleCreate


async def get_recurring(db: AsyncSession, schedule_id: int, user_id: int) -> RecurringRule | None:
    await _check_schedule_owner(db, schedule_id, user_id)
    result = await db.execute(select(RecurringRule).where(RecurringRule.schedule_id == schedule_id))
    return result.scalar_one_or_none()


async def create_recurring(
    db: AsyncSession, schedule_id: int, user_id: int, data: RecurringRuleCreate
) -> RecurringRule:
    await _check_schedule_owner(db, schedule_id, user_id)

    # Remove existing if any
    await db.execute(select(RecurringRule).where(RecurringRule.schedule_id == schedule_id))
    existing = (await db.execute(select(RecurringRule).where(RecurringRule.schedule_id == schedule_id))).scalar_one_or_none()
    if existing:
        await db.delete(existing)
        await db.flush()

    rule = RecurringRule(
        schedule_id=schedule_id,
        freq=data.freq,
        interval=data.interval,
        weekdays=data.weekdays,
        monthday=data.monthday,
        start_date=data.start_date,
        end_date=data.end_date,
        count=data.count,
    )
    db.add(rule)
    await db.flush()
    return rule


async def update_recurring(
    db: AsyncSession, schedule_id: int, user_id: int, data: dict
) -> RecurringRule:
    await _check_schedule_owner(db, schedule_id, user_id)
    result = await db.execute(select(RecurringRule).where(RecurringRule.schedule_id == schedule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise NotFoundError("Recurring rule not found")
    for key, value in data.items():
        setattr(rule, key, value)
    await db.flush()
    return rule


async def delete_recurring(db: AsyncSession, schedule_id: int, user_id: int) -> None:
    await _check_schedule_owner(db, schedule_id, user_id)
    result = await db.execute(select(RecurringRule).where(RecurringRule.schedule_id == schedule_id))
    rule = result.scalar_one_or_none()
    if rule:
        await db.delete(rule)
        await db.flush()


async def _check_schedule_owner(db: AsyncSession, schedule_id: int, user_id: int):
    result = await db.execute(
        select(Schedule).where(Schedule.schedule_id == schedule_id, Schedule.user_id == user_id)
    )
    if not result.scalar_one_or_none():
        raise NotFoundError("Schedule not found")
