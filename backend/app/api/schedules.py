from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.database import get_db
from app.dependencies import get_current_user
from app.models.schedule import ScheduleStatus
from app.models.user import User
from app.schemas.recurring import RecurringRuleCreate, RecurringRuleOut
from app.schemas.reminder import ReminderCreate, ReminderOut
from app.schemas.schedule import (ScheduleCreate, ScheduleDetailOut,
                                   ScheduleOut, ScheduleUpdate, StatusUpdate)
from app.services import (reminder_service, schedule_service)
from app.services.recurring_service import (create_recurring,
                                              delete_recurring,
                                              get_recurring, update_recurring)

router = APIRouter()


@router.get("")
async def list_schedules(
    status: str | None = Query(None),
    priority: str | None = Query(None),
    category_id: int | None = Query(None),
    tag_ids: str | None = Query(None),
    focus: bool = Query(False),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tag_id_list = [int(t) for t in tag_ids.split(",")] if tag_ids else None
    result = await schedule_service.list_schedules(
        db, user.user_id, status=status, priority=priority,
        category_id=category_id, tag_ids=tag_id_list, focus=focus, page=page, per_page=per_page,
    )
    return {
        "items": [ScheduleOut.model_validate(item) for item in result.items],
        "total": result.total,
        "page": result.page,
        "per_page": result.per_page,
    }


@router.post("", response_model=ScheduleDetailOut, status_code=201)
async def create_schedule(
    data: ScheduleCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await schedule_service.create_schedule(db, user.user_id, data)


@router.get("/{schedule_id}", response_model=ScheduleDetailOut)
async def get_schedule(
    schedule_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await schedule_service.get_schedule(db, schedule_id, user.user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/{schedule_id}", response_model=ScheduleDetailOut)
async def update_schedule(
    schedule_id: int,
    data: ScheduleUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await schedule_service.update_schedule(db, schedule_id, user.user_id, data)
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(
    schedule_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await schedule_service.delete_schedule(db, schedule_id, user.user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/{schedule_id}/status", response_model=ScheduleDetailOut)
async def change_status(
    schedule_id: int,
    data: StatusUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await schedule_service.update_schedule_status(db, schedule_id, user.user_id, data.status)
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


# Reminders under schedule
@router.get("/{schedule_id}/reminders", response_model=list[ReminderOut])
async def list_reminders(
    schedule_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await reminder_service.list_reminders(db, schedule_id, user.user_id)


@router.post("/{schedule_id}/reminders", response_model=ReminderOut, status_code=201)
async def create_reminder(
    schedule_id: int,
    data: ReminderCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await reminder_service.create_reminder(db, schedule_id, user.user_id, data)


# Recurring under schedule
@router.get("/{schedule_id}/recurring", response_model=RecurringRuleOut | None)
async def get_recurring_rule(
    schedule_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_recurring(db, schedule_id, user.user_id)


@router.put("/{schedule_id}/recurring", response_model=RecurringRuleOut)
async def upsert_recurring_rule(
    schedule_id: int,
    data: RecurringRuleCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_recurring(db, schedule_id, user.user_id, data)


@router.delete("/{schedule_id}/recurring", status_code=204)
async def delete_recurring_rule(
    schedule_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await delete_recurring(db, schedule_id, user.user_id)


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------
from app.schemas.dependency import DependencyCreate, DependencyOut  # noqa: E402
from app.services import dependency_service  # noqa: E402


@router.get("/{schedule_id}/dependencies", response_model=list[DependencyOut])
async def list_dependencies(
    schedule_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await dependency_service.list_dependencies(db, schedule_id, user.user_id)


@router.post("/{schedule_id}/dependencies", response_model=DependencyOut, status_code=201)
async def create_dependency(
    schedule_id: int,
    data: DependencyCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await dependency_service.create_dependency(
        db, schedule_id, user.user_id, data.depends_on_id, data.dep_type
    )


@router.delete("/{schedule_id}/dependencies/{dependency_id}", status_code=204)
async def delete_dependency(
    schedule_id: int,
    dependency_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await dependency_service.delete_dependency(db, dependency_id, user.user_id)


# ---------------------------------------------------------------------------
# Duplicate
# ---------------------------------------------------------------------------
@router.post("/{schedule_id}/duplicate", response_model=ScheduleDetailOut, status_code=201)
async def duplicate_schedule(
    schedule_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        original = await schedule_service.get_schedule(db, schedule_id, user.user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    dup_data = ScheduleCreate(
        title=f"{original.title} (副本)",
        description=original.description,
        priority=original.priority,
        status=ScheduleStatus.TODO,
        due_date=original.due_date,
        estimated_minutes=original.estimated_minutes,
        category_id=original.category_id,
        tag_ids=[t.tag_id for t in original.tags] if original.tags else [],
    )
    return await schedule_service.create_schedule(db, user.user_id, dup_data)


# ---------------------------------------------------------------------------
# Batch operations
# ---------------------------------------------------------------------------
from pydantic import BaseModel  # noqa: E402


class BatchStatusUpdate(BaseModel):
    schedule_ids: list[int]
    status: ScheduleStatus


class BatchDelete(BaseModel):
    schedule_ids: list[int]


@router.post("/batch/status")
async def batch_update_status(
    data: BatchStatusUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count = 0
    for sid in data.schedule_ids:
        try:
            await schedule_service.update_schedule_status(db, sid, user.user_id, data.status)
            count += 1
        except NotFoundError:
            pass
    return {"updated": count}


@router.post("/batch/delete")
async def batch_delete(
    data: BatchDelete,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count = 0
    for sid in data.schedule_ids:
        try:
            await schedule_service.delete_schedule(db, sid, user.user_id)
            count += 1
        except NotFoundError:
            pass
    return {"deleted": count}


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------
import csv
import io
import json

from fastapi.responses import StreamingResponse


@router.get("/export/csv")
async def export_csv(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await schedule_service.list_schedules(db, user.user_id, per_page=1000)
    output = io.StringIO()
    csv_writer = csv.writer(output, lineterminator='\n')
    csv_writer.writerow(["ID", "标题", "描述", "优先级", "状态", "到期日", "分类", "标签"])
    for s in result.items:
        csv_writer.writerow([
            str(s.schedule_id),
            s.title,
            s.description or "",
            s.priority.value if s.priority else "",
            s.status.value if s.status else "",
            s.due_date.isoformat() if s.due_date else "",
            s.category.name if s.category else "",
            ", ".join(t.name for t in s.tags) if s.tags else "",
        ])
    csv_str = output.getvalue()
    return StreamingResponse(
        iter([csv_str.encode('utf-8-sig')]),
        media_type="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": "attachment; filename=schedules.csv"},
    )


@router.get("/export/json")
async def export_json(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await schedule_service.list_schedules(db, user.user_id, per_page=1000)
    data = [
        {
            "id": s.schedule_id, "title": s.title, "description": s.description or "",
            "priority": s.priority.value if s.priority else "",
            "status": s.status.value if s.status else "",
            "due_date": s.due_date.isoformat() if s.due_date else None,
            "category": s.category.name if s.category else None,
            "tags": [t.name for t in s.tags] if s.tags else [],
        }
        for s in result.items
    ]
    return StreamingResponse(
        iter([json.dumps(data, ensure_ascii=False, indent=2)]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=schedules.json"},
    )


# ---------------------------------------------------------------------------
# Subtasks
# ---------------------------------------------------------------------------
from app.schemas.subtask import SubtaskCreate, SubtaskOut, SubtaskUpdate  # noqa: E402
from app.services import subtask_service  # noqa: E402


@router.get("/{schedule_id}/subtasks", response_model=list[SubtaskOut])
async def list_subtasks(
    schedule_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await subtask_service.list_subtasks(db, schedule_id, user.user_id)


@router.post("/{schedule_id}/subtasks", response_model=SubtaskOut, status_code=201)
async def create_subtask(
    schedule_id: int,
    data: SubtaskCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await subtask_service.create_subtask(db, schedule_id, user.user_id, data.title)


@router.patch("/{schedule_id}/subtasks/{subtask_id}", response_model=SubtaskOut)
async def update_subtask(
    schedule_id: int,
    subtask_id: int,
    data: SubtaskUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        return await subtask_service.update_subtask(db, subtask_id, user.user_id, data.title, data.completed)
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{schedule_id}/subtasks/{subtask_id}", status_code=204)
async def delete_subtask(
    schedule_id: int,
    subtask_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await subtask_service.delete_subtask(db, subtask_id, user.user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
