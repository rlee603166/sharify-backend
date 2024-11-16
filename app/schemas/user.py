from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3)
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v):
        if not re.match('^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username must be alphanumeric')
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain an uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain a lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain a number')
        return v

class UserInDB(UserBase):
    id: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    disabled: bool = False

    class Config:
        orm_mode = True

class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }

class TokenData(BaseModel):
    user_id: str
    device_id: Optional[str] = None
    exp: datetime

class RefreshToken(BaseModel):
    refresh_token: str
    device_id: Optional[str] = None
