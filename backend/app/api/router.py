from fastapi import APIRouter

from app.api import (auth, calendar, categories, reminders, schedules, search,
                     statistics, tags)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["reminders"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["statistics"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
