from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.reminder import Reminder
from app.models.schedule import Schedule
from app.schemas.reminder import ReminderCreate, ReminderUpdate


async def list_reminders(db: AsyncSession, schedule_id: int, user_id: int) -> list[Reminder]:
    await _check_schedule_owner(db, schedule_id, user_id)
    result = await db.execute(
        select(Reminder).where(Reminder.schedule_id == schedule_id).order_by(Reminder.remind_at)
    )
    return list(result.scalars().all())


async def create_reminder(db: AsyncSession, schedule_id: int, user_id: int, data: ReminderCreate) -> Reminder:
    await _check_schedule_owner(db, schedule_id, user_id)
    reminder = Reminder(schedule_id=schedule_id, remind_at=data.remind_at, method=data.method)
    db.add(reminder)
    await db.flush()
    return reminder


async def update_reminder(db: AsyncSession, reminder_id: int, user_id: int, data: ReminderUpdate) -> Reminder:
    result = await db.execute(select(Reminder).where(Reminder.reminder_id == reminder_id))
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise NotFoundError("Reminder not found")
    await _check_schedule_owner(db, reminder.schedule_id, user_id)

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(reminder, key, value)
    await db.flush()
    return reminder


async def delete_reminder(db: AsyncSession, reminder_id: int, user_id: int) -> None:
    result = await db.execute(select(Reminder).where(Reminder.reminder_id == reminder_id))
    reminder = result.scalar_one_or_none()
    if not reminder:
        raise NotFoundError("Reminder not found")
    await _check_schedule_owner(db, reminder.schedule_id, user_id)
    await db.delete(reminder)
    await db.flush()


async def _check_schedule_owner(db: AsyncSession, schedule_id: int, user_id: int):
    result = await db.execute(
        select(Schedule).where(Schedule.schedule_id == schedule_id, Schedule.user_id == user_id)
    )
    if not result.scalar_one_or_none():
        raise NotFoundError("Schedule not found")
