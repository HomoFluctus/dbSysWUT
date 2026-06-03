from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.activity_log import ActivityLogOut
from app.services import activity_log_service

router = APIRouter()


@router.get("", response_model=dict)
async def list_activity_logs(
    action: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await activity_log_service.list_activity_logs(db, user.user_id, action=action, page=page, per_page=per_page)
