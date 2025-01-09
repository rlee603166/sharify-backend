from pydantic import BaseModel

class CreateFriend(BaseModel):
    user_1: str
    user_2: str
    status: str

class UpdateFriend(BaseModel):
    user_1: str | None = None
    user_2: str | None = None
    status: str | None = None
