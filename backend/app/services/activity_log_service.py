from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_log import ActivityLog
from app.models.schedule import Schedule


async def list_activity_logs(
    db: AsyncSession, user_id: int, action: str | None = None, page: int = 1, per_page: int = 30
) -> dict:
    stmt = (
        select(ActivityLog, Schedule.title.label("schedule_title"))
        .outerjoin(Schedule, Schedule.schedule_id == ActivityLog.schedule_id)
        .where(ActivityLog.user_id == user_id)
        .order_by(desc(ActivityLog.created_at))
    )
    if action:
        stmt = stmt.where(ActivityLog.action == action)

    # Count
    from sqlalchemy import func
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(stmt)

    items = []
    for row in result:
        log, title = row
        items.append({
            "log_id": log.log_id,
            "schedule_id": log.schedule_id,
            "user_id": log.user_id,
            "action": log.action,
            "field_changed": log.field_changed,
            "old_value": log.old_value,
            "new_value": log.new_value,
            "schedule_title": title,
            "created_at": log.created_at,
        })

    return {"items": items, "total": total, "page": page, "per_page": per_page}
