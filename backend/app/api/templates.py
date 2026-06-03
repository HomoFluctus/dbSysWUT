from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.template import TemplateCreate, TemplateOut
from app.services import template_service

router = APIRouter()


@router.get("", response_model=list[TemplateOut])
async def list_templates(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await template_service.list_templates(db, user.user_id)


@router.post("", response_model=TemplateOut, status_code=201)
async def create_template(
    data: TemplateCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await template_service.create_template(db, user.user_id, data)


@router.delete("/{template_id}", status_code=204)
async def delete_template(
    template_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await template_service.delete_template(db, template_id, user.user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{template_id}/apply")
async def apply_template(
    template_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await template_service.apply_template(db, template_id, user.user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
