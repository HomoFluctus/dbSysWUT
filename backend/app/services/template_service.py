import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.schedule_template import ScheduleTemplate
from app.schemas.template import TemplateCreate


async def list_templates(db: AsyncSession, user_id: int) -> list[ScheduleTemplate]:
    result = await db.execute(
        select(ScheduleTemplate)
        .where(ScheduleTemplate.user_id == user_id)
        .order_by(ScheduleTemplate.template_id.desc())
    )
    return list(result.scalars().all())


async def create_template(db: AsyncSession, user_id: int, data: TemplateCreate) -> ScheduleTemplate:
    tmpl = ScheduleTemplate(
        user_id=user_id,
        title=data.title,
        description=data.description,
        priority=data.priority,
        estimated_minutes=data.estimated_minutes,
        category_id=data.category_id,
        tag_ids=json.dumps(data.tag_ids) if data.tag_ids else None,
    )
    db.add(tmpl)
    await db.flush()
    return tmpl


async def delete_template(db: AsyncSession, template_id: int, user_id: int) -> None:
    result = await db.execute(
        select(ScheduleTemplate).where(
            ScheduleTemplate.template_id == template_id,
            ScheduleTemplate.user_id == user_id,
        )
    )
    tmpl = result.scalar_one_or_none()
    if not tmpl:
        raise NotFoundError("Template not found")
    await db.delete(tmpl)
    await db.flush()


async def apply_template(db: AsyncSession, template_id: int, user_id: int) -> dict:
    """Return a dict ready to populate ScheduleCreate."""
    result = await db.execute(
        select(ScheduleTemplate).where(
            ScheduleTemplate.template_id == template_id,
            ScheduleTemplate.user_id == user_id,
        )
    )
    tmpl = result.scalar_one_or_none()
    if not tmpl:
        raise NotFoundError("Template not found")

    tag_ids = json.loads(tmpl.tag_ids) if tmpl.tag_ids else []
    return {
        "title": tmpl.title,
        "description": tmpl.description,
        "priority": tmpl.priority,
        "estimated_minutes": tmpl.estimated_minutes,
        "category_id": tmpl.category_id,
        "tag_ids": tag_ids,
    }
