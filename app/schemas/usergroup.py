from pydantic import BaseModel

class CreateUG(BaseModel):
    user_id: int
    group_id: int


class UpdateUG(BaseModel):
    user_id: int | None = None
    group_id: int | None = None
