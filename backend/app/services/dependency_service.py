from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.models.schedule import Schedule
from app.models.schedule_dependency import ScheduleDependency


async def list_dependencies(db: AsyncSession, schedule_id: int, user_id: int) -> list[ScheduleDependency]:
    schedule = await db.execute(
        select(Schedule).where(Schedule.schedule_id == schedule_id, Schedule.user_id == user_id)
    )
    if not schedule.scalar_one_or_none():
        raise NotFoundError("Schedule not found")

    result = await db.execute(
        select(ScheduleDependency)
        .where(ScheduleDependency.schedule_id == schedule_id)
        .options(
            selectinload(ScheduleDependency.schedule),
        )
    )
    return result.scalars().all()


async def create_dependency(
    db: AsyncSession, schedule_id: int, user_id: int, depends_on_id: int, dep_type: str = "blocks"
) -> ScheduleDependency:
    schedule = await db.execute(
        select(Schedule).where(Schedule.schedule_id == schedule_id, Schedule.user_id == user_id)
    )
    if not schedule.scalar_one_or_none():
        raise NotFoundError("Schedule not found")

    dep = ScheduleDependency(schedule_id=schedule_id, depends_on_id=depends_on_id, dep_type=dep_type)
    db.add(dep)
    await db.flush()
    return dep


async def delete_dependency(db: AsyncSession, dependency_id: int, user_id: int) -> None:
    result = await db.execute(
        select(ScheduleDependency)
        .join(Schedule, Schedule.schedule_id == ScheduleDependency.schedule_id)
        .where(ScheduleDependency.dependency_id == dependency_id, Schedule.user_id == user_id)
    )
    dep = result.scalar_one_or_none()
    if not dep:
        raise NotFoundError("Dependency not found")
    await db.delete(dep)
    await db.flush()
