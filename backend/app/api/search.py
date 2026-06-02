from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services import search_service

router = APIRouter()


@router.get("")
async def search(
    q: str | None = Query(None),
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
    return await search_service.search_schedules(
        db, user.user_id, q=q, status=status, priority=priority,
        category_id=category_id, tag_ids=tag_id_list, page=page, per_page=per_page,
    )
