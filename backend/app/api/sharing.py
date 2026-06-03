from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleDetailOut

router = APIRouter()


@router.get("/{token}", response_model=ScheduleDetailOut)
async def view_shared_schedule(token: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Schedule)
        .where(Schedule.share_token == token)
        .options(
            selectinload(Schedule.category),
            selectinload(Schedule.tags),
            selectinload(Schedule.recurring),
            selectinload(Schedule.reminders),
            selectinload(Schedule.subtasks),
        )
    )
    s = result.unique().scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Schedule not found or share link invalid")
    return s
