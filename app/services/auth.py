from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext

from schemas import UserInDB, User, UserCreate
from repositories import UserRepository
from config import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.repository = UserRepository()
    
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    
    async def get_user(self, username: str) -> Optional[UserInDB]:
        try:
            return await self.repository.get_by_username(username)
        except HTTPException as e:
            if e.status_code == 404:
                return None
            raise

    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        try:
            user = await self.repository.get_by_username(username)
            if not user:
                return None
                
            if not self.verify_password(password, user.get('hashed_password')):
                return None
                
            return User(**user)
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail="Authentication failed"
            )

    
    async def create_user(self, user_data: UserCreate):
        try:
            existing_user = await self.repository.get_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=400, 
                    detail="Email already registered"
                )
            
            existing_username = await self.repository.get_by_username(user_data.username)
            if existing_username:
                raise HTTPException(
                    status_code=400, 
                    detail="Username already taken"
                )

            user_dict = user_data.model_dump()
            user_dict['hashed_password'] = self.get_password_hash(user_data.hashed_password)
            
            return await self.repository.create(UserCreate(**user_dict))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating user: {str(e)}"
            )
