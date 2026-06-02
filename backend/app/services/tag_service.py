from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.tag import Tag
from app.schemas.tag import TagCreate


async def list_tags(db: AsyncSession, user_id: int) -> list[Tag]:
    result = await db.execute(select(Tag).where(Tag.user_id == user_id).order_by(Tag.name))
    return list(result.scalars().all())


async def create_tag(db: AsyncSession, user_id: int, data: TagCreate) -> Tag:
    tag = Tag(user_id=user_id, name=data.name, color=data.color)
    db.add(tag)
    await db.flush()
    return tag


async def delete_tag(db: AsyncSession, tag_id: int, user_id: int) -> None:
    result = await db.execute(select(Tag).where(Tag.tag_id == tag_id, Tag.user_id == user_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise NotFoundError("Tag not found")
    await db.delete(tag)
    await db.flush()
