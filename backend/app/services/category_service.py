from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


async def list_categories(db: AsyncSession, user_id: int) -> list[Category]:
    result = await db.execute(
        select(Category).where(Category.user_id == user_id).order_by(Category.is_default.desc(), Category.name)
    )
    return list(result.scalars().all())


async def create_category(db: AsyncSession, user_id: int, data: CategoryCreate) -> Category:
    cat = Category(user_id=user_id, name=data.name, color=data.color)
    db.add(cat)
    await db.flush()
    return cat


async def update_category(db: AsyncSession, category_id: int, user_id: int, data: CategoryUpdate) -> Category:
    result = await db.execute(
        select(Category).where(Category.category_id == category_id, Category.user_id == user_id)
    )
    cat = result.scalar_one_or_none()
    if not cat:
        raise NotFoundError("Category not found")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cat, key, value)
    await db.flush()
    return cat


async def delete_category(db: AsyncSession, category_id: int, user_id: int) -> None:
    result = await db.execute(
        select(Category).where(Category.category_id == category_id, Category.user_id == user_id)
    )
    cat = result.scalar_one_or_none()
    if not cat:
        raise NotFoundError("Category not found")
    await db.delete(cat)
    await db.flush()
