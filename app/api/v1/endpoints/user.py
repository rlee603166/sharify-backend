from datetime import datetime, timedelta, timezone
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext

from api.v1.endpoints.auth import token
from dependencies import AuthServiceDep, UserServiceDep, TwilioServiceDep
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

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    return current_user

@router.get("/", response_model=List[User])
async def read_users(
    current_user: Annotated[User, Depends(get_current_active_user)],
    user_service: UserServiceDep
):
    return await user_service.get_all_users()


@router.get("/login")
async def login(
    user: Annotated[User, Depends(get_current_active_user)],
    twilio_service: TwilioServiceDep
):
    try:
        verification = await twilio_service.send_sms(user)
        return {
            "status": "verification_sent",
            "message": f"Verification code sent to phone",
            "verification_status": verification  # Optionally include the Twilio status
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification: {str(e)}"
        )
        
@router.post("/verify-phone")  # or whatever your route path is
async def verify_phone(
    user: Annotated[User, Depends(get_current_active_user)],
    code: str,  # You might want to use a Pydantic model for this
    twilio_service: TwilioServiceDep,
    auth_service: AuthServiceDep,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    try:
        verification_status = await twilio_service.verify_sms(user, code)
        if verification_status == 'approved':
            new_token = await token(form_data, auth_service)
            return {
                "status": "success",
                "is_verified": True,
                "message": "Phone verified successfully",
                "access_token": new_token.access_token,
                "token_type": new_token.token_type
            }
        # Always return a dictionary
        return {
            "status": verification_status,
            "message": "Phone verification completed"
        }
    except Exception as e:
        print(f"Verification error: {str(e)}")  # Debug logging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify code: {str(e)}"
        )

@router.post("/register", response_model=User)
async def create_user(
    user: UserCreate,
    user_service: UserServiceDep
):
    return await user_service.create_user(user)

@router.get("/test")
async def test(
    user_service: UserServiceDep
):
    return await user_service.get_user('ryan')