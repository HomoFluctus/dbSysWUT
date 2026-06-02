from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.schedule import ScheduleOut
from app.services import calendar_service

router = APIRouter()


@router.get("", response_model=list[ScheduleOut])
async def month_calendar(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await calendar_service.get_month_calendar(db, user.user_id, year, month)


@router.get("/week", response_model=list[ScheduleOut])
async def week_calendar(
    date: str = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await calendar_service.get_week_calendar(db, user.user_id, date)


@router.get("/day", response_model=list[ScheduleOut])
async def day_calendar(
    date: str = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await calendar_service.get_day_calendar(db, user.user_id, date)
