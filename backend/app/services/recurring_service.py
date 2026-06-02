from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
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


def expand_recurring_dates(rule: RecurringRule, range_start: date, range_end: date) -> list[date]:
    """Compute all occurrence dates of a recurring rule within [range_start, range_end]."""
    start = rule.start_date
    if rule.end_date:
        effective_end = min(rule.end_date, range_end)
    else:
        effective_end = range_end

    if start > effective_end:
        return []

    dates: list[date] = []
    max_count = rule.count or 9999
    interval = max(rule.interval, 1)

    if rule.freq == "daily":
        current = start
        while current <= effective_end and len(dates) < max_count:
            if current >= range_start:
                dates.append(current)
            current = current + timedelta(days=interval)

    elif rule.freq == "weekly":
        if rule.weekdays:
            target_days = {int(d) for d in rule.weekdays.split(",") if d.strip()}
        else:
            target_days = {start.weekday()}

        current = start
        week_start = current - timedelta(days=current.weekday())
        while week_start <= effective_end and len(dates) < max_count:
            for wd in sorted(target_days):
                d = week_start + timedelta(days=wd)
                if start <= d <= effective_end and d >= range_start:
                    dates.append(d)
                    if len(dates) >= max_count:
                        break
            week_start += timedelta(weeks=interval)

    elif rule.freq == "monthly":
        day = rule.monthday if rule.monthday else start.day
        current = start.replace(day=1)
        while current <= effective_end and len(dates) < max_count:
            try:
                occ = current.replace(day=min(day, _days_in_month(current.year, current.month)))
            except ValueError:
                occ = current.replace(day=_days_in_month(current.year, current.month))
            if occ >= start and occ <= effective_end and occ >= range_start:
                dates.append(occ)
            current += relativedelta(months=interval)

    elif rule.freq == "yearly":
        current = start
        while current <= effective_end and len(dates) < max_count:
            if current >= range_start:
                dates.append(current)
            current = start.replace(year=start.year + interval * (len(dates) + 1))

    return sorted(set(dates))


def _days_in_month(year: int, month: int) -> int:
    import calendar
    return calendar.monthrange(year, month)[1]
