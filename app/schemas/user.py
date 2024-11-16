
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    

class TokenData(BaseModel):
    username: str | None = None
    

class UserBase(BaseModel):
    username: str
    hashed_password: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class User(UserBase):
    pass


class UserInDB(UserBase):
    hashed_password: str
    
    
class UserCreate(UserBase):
    email: str
    first_name: str
    last_name: str
    phone_number: str
    zip: int
    
    
# Look later no fully dev
class UserUpdate(UserBase):
    username: str | None = None
    phone_number: str | None = None
    zip: int | None = None