from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.schedule import Schedule
from app.models.subtask import Subtask


async def list_subtasks(db: AsyncSession, schedule_id: int, user_id: int) -> list[Subtask]:
    s = await db.execute(
        select(Schedule).where(Schedule.schedule_id == schedule_id, Schedule.user_id == user_id)
    )
    if not s.scalar_one_or_none():
        raise NotFoundError("Schedule not found")
    result = await db.execute(
        select(Subtask).where(Subtask.schedule_id == schedule_id).order_by(Subtask.sort_order)
    )
    return result.scalars().all()


async def create_subtask(db: AsyncSession, schedule_id: int, user_id: int, title: str) -> Subtask:
    s = await db.execute(
        select(Schedule).where(Schedule.schedule_id == schedule_id, Schedule.user_id == user_id)
    )
    if not s.scalar_one_or_none():
        raise NotFoundError("Schedule not found")
    st = Subtask(schedule_id=schedule_id, title=title)
    db.add(st)
    await db.flush()
    return st


async def update_subtask(db: AsyncSession, subtask_id: int, user_id: int, title: str | None, completed: bool | None) -> Subtask:
    result = await db.execute(
        select(Subtask).join(Schedule, Schedule.schedule_id == Subtask.schedule_id)
        .where(Subtask.subtask_id == subtask_id, Schedule.user_id == user_id)
    )
    st = result.scalar_one_or_none()
    if not st:
        raise NotFoundError("Subtask not found")
    if title is not None:
        st.title = title
    if completed is not None:
        st.completed = completed
    await db.flush()
    return st


async def delete_subtask(db: AsyncSession, subtask_id: int, user_id: int) -> None:
    result = await db.execute(
        select(Subtask).join(Schedule, Schedule.schedule_id == Subtask.schedule_id)
        .where(Subtask.subtask_id == subtask_id, Schedule.user_id == user_id)
    )
    st = result.scalar_one_or_none()
    if not st:
        raise NotFoundError("Subtask not found")
    await db.delete(st)
    await db.flush()
