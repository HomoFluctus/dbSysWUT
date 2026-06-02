from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.schedule import Schedule
from app.models.schedule_tag import ScheduleTag


async def search_schedules(
    db: AsyncSession,
    user_id: int,
    q: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    category_id: int | None = None,
    tag_ids: list[int] | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    stmt = select(Schedule).where(Schedule.user_id == user_id)

    if q:
        stmt = stmt.where(
            or_(
                Schedule.title.ilike(f"%{q}%"),
                Schedule.description.ilike(f"%{q}%"),
            )
        )
    if status:
        stmt = stmt.where(Schedule.status == status)
    if priority:
        stmt = stmt.where(Schedule.priority == priority)
    if category_id is not None:
        stmt = stmt.where(Schedule.category_id == category_id)
    if tag_ids:
        stmt = stmt.join(Schedule.tags).where(ScheduleTag.tag_id.in_(tag_ids))
        stmt = stmt.group_by(Schedule.schedule_id)
        stmt = stmt.having(func.count(ScheduleTag.tag_id) == len(tag_ids))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.options(
        selectinload(Schedule.category),
        selectinload(Schedule.tags),
    ).order_by(Schedule.due_date.asc().nulls_last())
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(stmt)
    return {"items": list(result.unique().scalars().all()), "total": total, "page": page, "per_page": per_page}
