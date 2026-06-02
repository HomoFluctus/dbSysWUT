from pydantic import BaseModel


class TagCreate(BaseModel):
    name: str
    color: str = "#a855f7"


class TagOut(BaseModel):
    tag_id: int
    user_id: int
    name: str
    color: str

    class Config:
        from_attributes = True
