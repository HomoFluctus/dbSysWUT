from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.database import get_db
from app.dependencies import get_current_user
from app.models.schedule import ScheduleStatus
from app.models.user import User
from app.schemas.recurring import RecurringRuleCreate, RecurringRuleOut
from app.schemas.reminder import ReminderCreate, ReminderOut
from app.schemas.schedule import (ScheduleCreate, ScheduleDetailOut,
                                   ScheduleOut, ScheduleUpdate, StatusUpdate)
from app.services import (reminder_service, schedule_service)
from app.services.recurring_service import (create_recurring,
                                              delete_recurring,
                                              get_recurring, update_recurring)

router = APIRouter()


@router.get("")
async def list_schedules(
    status: str | None = Query(None),
    priority: str | None = Query(None),
    category_id: int | None = Query(None),
    tag_ids: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tag_id_list = [int(t) for t in tag_ids.split(",")] if tag_ids else None
    result = await schedule_service.list_schedules(
        db, user.user_id, status=status, priority=priority,
        category_id=category_id, tag_ids=tag_id_list, page=page, per_page=per_page,
    )
    return {
        "items": [ScheduleOut.model_validate(item) for item in result.items],
        "total": result.total,
        "page": result.page,
        "per_page": result.per_page,
    }


@router.post("", response_model=ScheduleDetailOut, status_code=201)
async def create_schedule(
    data: ScheduleCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await schedule_service.create_schedule(db, user.user_id, data)


@router.get("/{schedule_id}", response_model=ScheduleDetailOut)
async def get_schedule(
    schedule_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await schedule_service.get_schedule(db, schedule_id, user.user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/{schedule_id}", response_model=ScheduleDetailOut)
async def update_schedule(
    schedule_id: int,
    data: ScheduleUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await schedule_service.update_schedule(db, schedule_id, user.user_id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(
    schedule_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await schedule_service.delete_schedule(db, schedule_id, user.user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/{schedule_id}/status", response_model=ScheduleDetailOut)
async def change_status(
    schedule_id: int,
    data: StatusUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await schedule_service.update_schedule_status(db, schedule_id, user.user_id, data.status)
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# Reminders under schedule
@router.get("/{schedule_id}/reminders", response_model=list[ReminderOut])
async def list_reminders(
    schedule_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await reminder_service.list_reminders(db, schedule_id, user.user_id)


@router.post("/{schedule_id}/reminders", response_model=ReminderOut, status_code=201)
async def create_reminder(
    schedule_id: int,
    data: ReminderCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await reminder_service.create_reminder(db, schedule_id, user.user_id, data)


# Recurring under schedule
@router.get("/{schedule_id}/recurring", response_model=RecurringRuleOut | None)
async def get_recurring_rule(
    schedule_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_recurring(db, schedule_id, user.user_id)


@router.put("/{schedule_id}/recurring", response_model=RecurringRuleOut)
async def upsert_recurring_rule(
    schedule_id: int,
    data: RecurringRuleCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_recurring(db, schedule_id, user.user_id, data)


@router.delete("/{schedule_id}/recurring", status_code=204)
async def delete_recurring_rule(
    schedule_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await delete_recurring(db, schedule_id, user.user_id)
