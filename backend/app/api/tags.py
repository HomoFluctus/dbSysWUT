from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.tag import TagCreate, TagOut
from app.services import tag_service

router = APIRouter()


@router.get("", response_model=list[TagOut])
async def list_tags(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await tag_service.list_tags(db, user.user_id)


@router.post("", response_model=TagOut, status_code=201)
async def create_tag(
    data: TagCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await tag_service.create_tag(db, user.user_id, data)


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await tag_service.delete_tag(db, tag_id, user.user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
