import secrets
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import TZ
from app.models.recurring_rule import RecurringRule
from app.models.schedule import Schedule
from app.models.user import User
from app.services.recurring_service import expand_recurring_dates


def generate_ical_token() -> str:
    return secrets.token_urlsafe(32)


async def get_or_create_ical_token(db: AsyncSession, user_id: int) -> str:
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one()
    if not user.ical_token:
        user.ical_token = generate_ical_token()
        db.add(user)
        await db.flush()
    return user.ical_token


async def generate_ics(db: AsyncSession, token: str) -> str | None:
    result = await db.execute(select(User).where(User.ical_token == token))
    user = result.scalar_one_or_none()
    if not user:
        return None

    stmt = (
        select(Schedule)
        .where(Schedule.user_id == user.user_id)
        .options(selectinload(Schedule.recurring))
    )
    result = await db.execute(stmt)
    schedules = result.unique().scalars().all()

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//TaskScheduler//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    now_str = datetime.now(TZ).strftime("%Y%m%dT%H%M%S")
    today = datetime.now(TZ).date()
    range_end = today.replace(year=today.year + 1)

    for s in schedules:
        if s.recurring and s.recurring.start_date:
            dates = expand_recurring_dates(s.recurring, today, range_end)
            for d in dates:
                _add_vevent(lines, s.title, s.description, d, s.priority.value)
        elif s.due_date:
            _add_vevent(lines, s.title, s.description, s.due_date, s.priority.value)

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


def _add_vevent(lines: list, title: str, desc: str | None, dt: datetime, priority: str):
    dt_str = dt.strftime("%Y%m%dT%H%M%S")
    uid = f"{secrets.token_hex(8)}@taskscheduler"
    lines.extend([
        "BEGIN:VEVENT",
        f"DTSTART:{dt_str}",
        f"SUMMARY:{title}",
        f"UID:{uid}",
        f"DTSTAMP:{datetime.now(TZ).strftime('%Y%m%dT%H%M%S')}",
    ])
    if desc:
        lines.append(f"DESCRIPTION:{_escape_ical(desc)}")
    lines.append(f"PRIORITY:{_ical_priority(priority)}")
    lines.append("END:VEVENT")


def _ical_priority(p: str) -> str:
    return {"urgent": "1", "high": "3", "medium": "5", "low": "9"}.get(p, "5")


def _escape_ical(text: str) -> str:
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
