from pydantic import BaseModel
from typing import List


class GroupMember(BaseModel):
    user_id: int

class CreateGroup(BaseModel):
    group_name: str
    imageUri: str | None = None

class NewGroup(CreateGroup):
    members: List[GroupMember]

class UpdateGroup(BaseModel):
    group_name: str | None = None
    imageUri: str | None = None
