from pydantic import BaseModel

class CreateFriend(BaseModel):
    user_1: int 
    user_2: int  
    status: str

class UpdateFriend(BaseModel):
    user_1: int | None = None
    user_2: int | None = None
    status: str | None = None


