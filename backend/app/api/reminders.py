from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.reminder import ReminderOut, ReminderUpdate
from app.services import reminder_service

router = APIRouter()


@router.patch("/{reminder_id}", response_model=ReminderOut)
async def update_reminder(
    reminder_id: int,
    data: ReminderUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await reminder_service.update_reminder(db, reminder_id, user.user_id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{reminder_id}", status_code=204)
async def delete_reminder(
    reminder_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await reminder_service.delete_reminder(db, reminder_id, user.user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
