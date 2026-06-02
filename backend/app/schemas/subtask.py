from pydantic import BaseModel


class SubtaskCreate(BaseModel):
    title: str


class SubtaskUpdate(BaseModel):
    title: str | None = None
    completed: bool | None = None
    sort_order: int | None = None


class SubtaskOut(BaseModel):
    subtask_id: int
    schedule_id: int
    title: str
    completed: bool
    sort_order: int

    class Config:
        from_attributes = True
