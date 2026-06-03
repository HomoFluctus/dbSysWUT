from datetime import date as date_type, datetime, timedelta

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import TZ

from app.models.schedule import PriorityLevel, Schedule, ScheduleStatus


async def get_overview(db: AsyncSession, user_id: int) -> dict:
    stmt = (
        select(
            Schedule.status, func.count().label("cnt")
        )
        .where(Schedule.user_id == user_id)
        .group_by(Schedule.status)
    )
    result = await db.execute(stmt)
    by_status = {row.status.value: row.cnt for row in result}

    total = sum(by_status.values())
    overdue_stmt = select(func.count()).where(
        Schedule.user_id == user_id,
        Schedule.status != ScheduleStatus.DONE,
        Schedule.status != ScheduleStatus.CANCELLED,
        Schedule.due_date < datetime.now(TZ),
    )
    overdue = (await db.execute(overdue_stmt)).scalar() or 0

    return {
        "total": total,
        "todo": by_status.get("todo", 0),
        "in_progress": by_status.get("in_progress", 0),
        "done": by_status.get("done", 0),
        "cancelled": by_status.get("cancelled", 0),
        "overdue": overdue,
    }


async def get_completion_rate(db: AsyncSession, user_id: int, days: int = 30) -> list[dict]:
    since = datetime.now(TZ) - timedelta(days=days)
    stmt = (
        select(
            func.date(Schedule.due_date).label("day"),
            func.count().label("total"),
            func.sum(case((Schedule.status == ScheduleStatus.DONE, 1), else_=0)).label("completed"),
        )
        .where(Schedule.user_id == user_id, Schedule.due_date >= since)
        .group_by(func.date(Schedule.due_date))
        .order_by(func.date(Schedule.due_date))
    )
    result = await db.execute(stmt)
    return [{"day": str(row.day), "total": row.total, "completed": row.completed or 0} for row in result]


async def get_category_distribution(db: AsyncSession, user_id: int) -> list[dict]:
    from app.models.category import Category
    stmt = (
        select(
            Category.name,
            Category.color,
            func.count(Schedule.schedule_id).label("cnt"),
        )
        .join(Schedule, Schedule.category_id == Category.category_id, isouter=True)
        .where(Schedule.user_id == user_id)
        .group_by(Category.category_id)
        .order_by(func.count(Schedule.schedule_id).desc())
    )
    result = await db.execute(stmt)
    return [{"name": row.name, "color": row.color, "count": row.cnt} for row in result]


async def get_priority_distribution(db: AsyncSession, user_id: int) -> dict:
    stmt = (
        select(Schedule.priority, func.count().label("cnt"))
        .where(Schedule.user_id == user_id)
        .group_by(Schedule.priority)
    )
    result = await db.execute(stmt)
    return {row.priority.value: row.cnt for row in result}


async def get_activity_heatmap(db: AsyncSession, user_id: int) -> dict:
    since = datetime.now(TZ) - timedelta(days=365)
    merged: dict[str, int] = {}

    # Count by created_at
    stmt_create = (
        select(
            func.date(Schedule.created_at).label("day"),
            func.count().label("cnt"),
        )
        .where(Schedule.user_id == user_id, Schedule.created_at >= since)
        .group_by(func.date(Schedule.created_at))
    )
    result = await db.execute(stmt_create)
    for row in result:
        merged[str(row.day)] = merged.get(str(row.day), 0) + row.cnt

    # Count by due_date (only future or recent due dates)
    stmt_due = (
        select(
            func.date(Schedule.due_date).label("day"),
            func.count().label("cnt"),
        )
        .where(
            Schedule.user_id == user_id,
            Schedule.due_date.isnot(None),
            Schedule.due_date >= since,
        )
        .group_by(func.date(Schedule.due_date))
    )
    result = await db.execute(stmt_due)
    for row in result:
        merged[str(row.day)] = merged.get(str(row.day), 0) + row.cnt

    # Count recurring occurrences: expand each recurring schedule's dates in range
    from sqlalchemy.orm import selectinload
    from app.models.recurring_rule import RecurringRule
    from app.services.recurring_service import expand_recurring_dates

    stmt_recur = (
        select(Schedule)
        .where(Schedule.user_id == user_id)
        .where(Schedule.recurring.has(RecurringRule.start_date.isnot(None)))
        .options(selectinload(Schedule.recurring))
    )
    result = await db.execute(stmt_recur)
    recurring_schedules = result.unique().scalars().all()

    range_start = since.date()
    range_end = datetime.now(TZ).date()
    for s in recurring_schedules:
        if s.recurring:
            dates = expand_recurring_dates(s.recurring, range_start, range_end)
            for d in dates:
                key = d.isoformat()
                merged[key] = merged.get(key, 0) + 1

    return merged


async def get_streaks(db: AsyncSession, user_id: int) -> dict:
    """Calculate current and longest completion streaks."""
    stmt = (
        select(func.date(Schedule.completed_at).label("day"))
        .where(
            Schedule.user_id == user_id,
            Schedule.completed_at.isnot(None),
        )
        .group_by(func.date(Schedule.completed_at))
        .order_by(func.date(Schedule.completed_at).desc())
    )
    result = await db.execute(stmt)
    completed_dates = [
        date_type.fromisoformat(row.day) if isinstance(row.day, str) else row.day
        for row in result
    ]

    if not completed_dates:
        return {"current_streak": 0, "longest_streak": 0}

    today = datetime.now(TZ).date()

    # Current streak: count consecutive days ending at today (or yesterday)
    current = 0
    check = today
    completed_set = set(completed_dates)
    while check in completed_set:
        current += 1
        check -= timedelta(days=1)
    # If today not done yet, check if yesterday starts the streak
    if current == 0:
        check = today - timedelta(days=1)
        while check in completed_set:
            current += 1
            check -= timedelta(days=1)

    # Longest streak: find max consecutive days
    longest = 0
    streak = 0
    sorted_dates = sorted(completed_set)
    for i, d in enumerate(sorted_dates):
        if i == 0:
            streak = 1
        elif (d - sorted_dates[i - 1]).days == 1:
            streak += 1
        else:
            streak = 1
        longest = max(longest, streak)

    return {"current_streak": current, "longest_streak": max(longest, current)}


async def get_time_accuracy(db: AsyncSession, user_id: int) -> dict:
    """Compare actual_minutes vs estimated_minutes for completed schedules."""
    stmt = (
        select(Schedule)
        .where(
            Schedule.user_id == user_id,
            Schedule.status == ScheduleStatus.DONE,
            Schedule.estimated_minutes.isnot(None),
            Schedule.actual_minutes.isnot(None),
        )
        .order_by(Schedule.completed_at.desc())
        .limit(50)
    )
    result = await db.execute(stmt)
    schedules = result.scalars().all()

    if not schedules:
        return {"accuracy": 0, "total_estimated": 0, "total_actual": 0, "samples": 0}

    total_estimated = sum(s.estimated_minutes or 0 for s in schedules)
    total_actual = sum(s.actual_minutes or 0 for s in schedules)
    accuracy = round(total_estimated / total_actual * 100, 1) if total_actual > 0 else 0

    return {
        "accuracy": min(accuracy, 200),
        "total_estimated": total_estimated,
        "total_actual": total_actual,
        "samples": len(schedules),
    }


async def get_review(db: AsyncSession, user_id: int, period: str = "day") -> dict:
    """Return completed / overdue / upcoming for daily or weekly review."""
    now = datetime.now(TZ)
    today = now.date()

    if period == "week":
        # This week: Monday to Sunday
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        next_start = week_end + timedelta(days=1)
        next_end = next_start + timedelta(days=6)
        range_start = week_start
        range_end = week_end
        upcoming_start = next_start
        upcoming_end = next_end
    else:
        range_start = today
        range_end = today
        upcoming_start = today + timedelta(days=1)
        upcoming_end = today + timedelta(days=1)

    # Completed in range
    stmt_done = (
        select(Schedule)
        .where(
            Schedule.user_id == user_id,
            func.date(Schedule.completed_at) >= range_start,
            func.date(Schedule.completed_at) <= range_end,
        )
        .order_by(Schedule.completed_at.desc())
        .limit(20)
    )
    result = await db.execute(stmt_done)
    completed = [_schedule_brief(s) for s in result.scalars().all()]

    # Overdue (not done, due date past)
    stmt_overdue = (
        select(Schedule)
        .where(
            Schedule.user_id == user_id,
            Schedule.status != ScheduleStatus.DONE,
            Schedule.status != ScheduleStatus.CANCELLED,
            Schedule.due_date < now,
        )
        .order_by(Schedule.due_date)
        .limit(20)
    )
    result = await db.execute(stmt_overdue)
    overdue = [_schedule_brief(s) for s in result.scalars().all()]

    # Upcoming
    stmt_upcoming = (
        select(Schedule)
        .where(
            Schedule.user_id == user_id,
            Schedule.due_date.isnot(None),
            func.date(Schedule.due_date) >= upcoming_start,
            func.date(Schedule.due_date) <= upcoming_end,
            Schedule.status != ScheduleStatus.DONE,
            Schedule.status != ScheduleStatus.CANCELLED,
        )
        .order_by(Schedule.due_date)
        .limit(20)
    )
    result = await db.execute(stmt_upcoming)
    upcoming = [_schedule_brief(s) for s in result.scalars().all()]

    return {
        "period": period,
        "completed": completed,
        "completed_count": len(completed),
        "overdue": overdue,
        "overdue_count": len(overdue),
        "upcoming": upcoming,
        "upcoming_count": len(upcoming),
    }


def _schedule_brief(s: Schedule) -> dict:
    return {
        "schedule_id": s.schedule_id,
        "title": s.title,
        "priority": s.priority.value,
        "status": s.status.value,
        "due_date": s.due_date.isoformat() if s.due_date else None,
        "completed_at": s.completed_at.isoformat() if s.completed_at else None,
    }


async def get_overdue_analysis(db: AsyncSession, user_id: int) -> list[dict]:
    stmt = (
        select(Schedule)
        .where(
            Schedule.user_id == user_id,
            Schedule.status != ScheduleStatus.DONE,
            Schedule.status != ScheduleStatus.CANCELLED,
            Schedule.due_date < datetime.now(TZ),
        )
        .order_by(Schedule.due_date)
        .limit(20)
    )
    result = await db.execute(stmt)
    schedules = result.scalars().all()

    now = datetime.now(TZ)
    return [
        {
            "schedule_id": s.schedule_id,
            "title": s.title,
            "due_date": s.due_date.isoformat() if s.due_date else None,
            "priority": s.priority.value,
            "overdue_days": (now - s.due_date.replace(tzinfo=TZ)).days if s.due_date else 0,
        }
        for s in schedules
    ]
