from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services import ical_service

router = APIRouter()


@router.get("/token")
async def get_ical_token(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    token = await ical_service.get_or_create_ical_token(db, user.user_id)
    return {"ical_token": token, "url": f"/api/ical/feed?token={token}"}


@router.get("/feed", response_class=PlainTextResponse)
async def ical_feed(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    ics = await ical_service.generate_ics(db, token)
    if ics is None:
        raise HTTPException(status_code=404, detail="Invalid token")
    return PlainTextResponse(ics, media_type="text/calendar")
