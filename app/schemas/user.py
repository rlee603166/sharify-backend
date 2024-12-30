from typing import Optional
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    status: str
    message: str
    
class Token(BaseModel):
    status: str
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str
    
class RegisterToken(BaseModel):
    status: str
    register_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserBase(BaseModel):
    username: str
    phone_number: str | None = None

class UserCreate(BaseModel):
    username: str
    phone: str

class User(UserBase):
    first_name: str 
    last_name: str 

class UserInDB(User):
    user_id: int
    zip: int
    pin: str

class UserUpdate(BaseModel):
    username: str | None = None
    phone_number: str | None = None
    zip: int | None = None
   
class AuthForm(BaseModel):
    username: Optional[str] = None
    phone_number: Optional[str] = None
    code: Optional[str] = None

class RegAuth(BaseModel):
    phone_number: str
    code: str

class Venmo(BaseModel):
    name: str
    photo_url: str
    username: str
    handle: str

class RegisterForm(BaseModel):
    username: str
    phone_number: str
    register_token: str

class NewUser(BaseModel):
    user_id: int
    username: str
    created_at: str
    phone: str
