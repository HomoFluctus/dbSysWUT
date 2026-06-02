from pydantic import BaseModel


class DependencyCreate(BaseModel):
    depends_on_id: int
    dep_type: str = "blocks"


class DependencyOut(BaseModel):
    dependency_id: int
    schedule_id: int
    depends_on_id: int
    dep_type: str

    class Config:
        from_attributes = True
