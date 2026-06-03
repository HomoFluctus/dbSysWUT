from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.database import engine, init_db

app = FastAPI(title="Task Scheduler", version="1.0.0")

app.include_router(api_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    # Import all models so Base.metadata knows about them
    import app.models.user  # noqa
    import app.models.category  # noqa
    import app.models.schedule  # noqa
    import app.models.tag  # noqa
    import app.models.schedule_tag  # noqa
    import app.models.recurring_rule  # noqa
    import app.models.reminder  # noqa
    import app.models.schedule_dependency  # noqa
    import app.models.subtask  # noqa
    import app.models.activity_log  # noqa
    import app.models.schedule_template  # noqa
    await init_db()


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
