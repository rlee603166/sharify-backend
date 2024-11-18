from datetime import datetime, timedelta, timezone
from typing import Annotated, List

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext

from dependencies import AuthServiceDep, UserServiceDep
from config import settings
from schemas import User, UserCreate

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


router = APIRouter(prefix="/users", tags=["users"])

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthServiceDep
) -> User:
    user = await auth_service.verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user

@router.get("/me/", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user

@router.get("/", response_model=List[User])
async def read_users(
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: UserServiceDep
):
    return await user_service.get_all_users()

@router.post("/register", response_model=User)
async def create_user(
    user: UserCreate,
    user_service: UserServiceDep
):
    return await user_service.create_user(user)
