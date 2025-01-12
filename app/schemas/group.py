from pydantic import BaseModel

class CreateGroup(BaseModel):
    group_id: int 
    group_name: str
    group_photo: str


class UpdateGroup(BaseModel):
    group_id: int | None = None
    group_name: str | None = None
    group_photo: str | None = None
