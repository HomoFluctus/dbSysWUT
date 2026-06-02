from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services import statistics_service

router = APIRouter()


@router.get("/overview")
async def overview(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await statistics_service.get_overview(db, user.user_id)


@router.get("/completion")
async def completion_rate(
    days: int = Query(30),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await statistics_service.get_completion_rate(db, user.user_id, days)


@router.get("/category-distribution")
async def category_distribution(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await statistics_service.get_category_distribution(db, user.user_id)


@router.get("/priority-distribution")
async def priority_distribution(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await statistics_service.get_priority_distribution(db, user.user_id)


@router.get("/overdue")
async def overdue(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await statistics_service.get_overdue_analysis(db, user.user_id)
