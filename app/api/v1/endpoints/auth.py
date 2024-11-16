from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from schemas import Token, UserCreate
from services import AuthService
from config import get_settings

settings = get_settings()
auth_service = AuthService()

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm,Depends()]
) -> Token:
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={'sub': user.username},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/register")
async def register(user_create: UserCreate):
    return await auth_service.create_user(user_create)