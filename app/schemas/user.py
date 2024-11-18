
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    

class TokenData(BaseModel):
    username: str | None = None
    

class UserBase(BaseModel):
    username: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None

# For user creation/registration
class UserCreate(BaseModel):
    username: str
    password: str  # Plain password from user
    email: str
    first_name: str
    last_name: str
    phone_number: str
    zip: int

# For general use (without sensitive info)
class User(UserBase):
    pass

# For database storage
class UserInDB(UserBase):
    email: str
    first_name: str
    last_name: str
    phone_number: str
    zip: int
    hashed_password: str

class UserUpdate(BaseModel):
    username: str | None = None
    phone_number: str | None = None
    zip: int | None = None