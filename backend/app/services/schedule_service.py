from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.models.activity_log import ActivityLog
from app.models.schedule import Schedule, ScheduleStatus
from app.models.schedule_tag import ScheduleTag
from app.schemas.schedule import PaginatedResponse, ScheduleCreate, ScheduleUpdate


async def list_schedules(
    db: AsyncSession,
    user_id: int,
    status: str | None = None,
    priority: str | None = None,
    category_id: int | None = None,
    tag_ids: list[int] | None = None,
    focus: bool = False,
    page: int = 1,
    per_page: int = 20,
) -> PaginatedResponse:
    stmt = select(Schedule).where(Schedule.user_id == user_id)

    if focus:
        now = datetime.now(timezone.utc)
        end_of_today = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        stmt = stmt.where(Schedule.due_date <= end_of_today)
        stmt = stmt.where(Schedule.status != ScheduleStatus.DONE)
        stmt = stmt.where(Schedule.status != ScheduleStatus.CANCELLED)

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

    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.options(
        selectinload(Schedule.category),
        selectinload(Schedule.tags),
        selectinload(Schedule.subtasks),
    ).order_by(Schedule.due_date.asc().nulls_last(), Schedule.priority.desc())
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(stmt)
    items = result.unique().scalars().all()
    return PaginatedResponse(items=items, total=total, page=page, per_page=per_page)


async def get_schedule(db: AsyncSession, schedule_id: int, user_id: int) -> Schedule:
    result = await db.execute(
        select(Schedule)
        .where(Schedule.schedule_id == schedule_id, Schedule.user_id == user_id)
        .options(
            selectinload(Schedule.category),
            selectinload(Schedule.tags),
            selectinload(Schedule.recurring),
            selectinload(Schedule.reminders),
            selectinload(Schedule.subtasks),
        )
    )
    schedule = result.unique().scalar_one_or_none()
    if not schedule:
        raise NotFoundError("Schedule not found")
    return schedule


async def create_schedule(db: AsyncSession, user_id: int, data: ScheduleCreate) -> Schedule:
    schedule = Schedule(
        user_id=user_id,
        category_id=data.category_id,
        title=data.title,
        description=data.description,
        priority=data.priority,
        status=data.status,
        due_date=data.due_date,
        estimated_minutes=data.estimated_minutes,
    )
    db.add(schedule)
    await db.flush()

    if data.tag_ids:
        for tag_id in data.tag_ids:
            db.add(ScheduleTag(schedule_id=schedule.schedule_id, tag_id=tag_id))

    db.add(ActivityLog(schedule_id=schedule.schedule_id, user_id=user_id, action="created"))
    await db.flush()
    return await get_schedule(db, schedule.schedule_id, user_id)


async def update_schedule(db: AsyncSession, schedule_id: int, user_id: int, data: ScheduleUpdate) -> Schedule:
    result = await db.execute(
        select(Schedule).where(Schedule.schedule_id == schedule_id, Schedule.user_id == user_id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise NotFoundError("Schedule not found")

    update_data = data.model_dump(exclude_unset=True)
    tag_ids = update_data.pop("tag_ids", None)

    for key, value in update_data.items():
        setattr(schedule, key, value)

    if tag_ids is not None:
        await db.execute(
            select(ScheduleTag).where(ScheduleTag.schedule_id == schedule_id)
        )
        # Delete existing tags and re-add
        from sqlalchemy import delete
        await db.execute(delete(ScheduleTag).where(ScheduleTag.schedule_id == schedule_id))
        for tag_id in tag_ids:
            db.add(ScheduleTag(schedule_id=schedule_id, tag_id=tag_id))

    db.add(ActivityLog(schedule_id=schedule_id, user_id=user_id, action="updated"))
    await db.flush()
    return await get_schedule(db, schedule_id, user_id)


async def delete_schedule(db: AsyncSession, schedule_id: int, user_id: int) -> None:
    result = await db.execute(
        select(Schedule).where(Schedule.schedule_id == schedule_id, Schedule.user_id == user_id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise NotFoundError("Schedule not found")
    await db.delete(schedule)
    await db.flush()


async def update_schedule_status(
    db: AsyncSession, schedule_id: int, user_id: int, status: ScheduleStatus
) -> Schedule:
    result = await db.execute(
        select(Schedule).where(Schedule.schedule_id == schedule_id, Schedule.user_id == user_id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise NotFoundError("Schedule not found")

    old_status = schedule.status.value
    schedule.status = status
    if status == ScheduleStatus.DONE:
        schedule.completed_at = datetime.now(timezone.utc)

    db.add(ActivityLog(
        schedule_id=schedule_id, user_id=user_id, action="status_changed",
        field_changed="status", old_value=old_status, new_value=status.value,
    ))
    await db.flush()
    return await get_schedule(db, schedule_id, user_id)
