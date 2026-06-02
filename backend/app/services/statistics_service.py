from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

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
        Schedule.due_date < datetime.now(timezone.utc),
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
    since = datetime.now(timezone.utc) - timedelta(days=days)
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
    since = datetime.now(timezone.utc) - timedelta(days=365)
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

    return merged


async def get_overdue_analysis(db: AsyncSession, user_id: int) -> list[dict]:
    stmt = (
        select(Schedule)
        .where(
            Schedule.user_id == user_id,
            Schedule.status != ScheduleStatus.DONE,
            Schedule.status != ScheduleStatus.CANCELLED,
            Schedule.due_date < datetime.now(timezone.utc),
        )
        .order_by(Schedule.due_date)
        .limit(20)
    )
    result = await db.execute(stmt)
    schedules = result.scalars().all()

    now = datetime.now(timezone.utc)
    return [
        {
            "schedule_id": s.schedule_id,
            "title": s.title,
            "due_date": s.due_date.isoformat() if s.due_date else None,
            "priority": s.priority.value,
            "overdue_days": (now - s.due_date.replace(tzinfo=timezone.utc)).days if s.due_date else 0,
        }
        for s in schedules
    ]
