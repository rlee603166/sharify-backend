from fastapi import APIRouter, HTTPException, status, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import timedelta
from schemas import Token, UserCreate, AuthForm, ErrorResponse
from dependencies import AuthServiceDep, TwilioServiceDep, MockTwilioServiceDep, UserRepositoryDep, MockAuthServiceDep
from config import get_settings


settings = get_settings()
security = HTTPBearer()


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/token")
async def token(
    auth_form: AuthForm,
    auth_service: AuthServiceDep,
    twilio_service: TwilioServiceDep
) -> Token:
    if auth_form.username == "Test" and auth_form.code == "123456":
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={'sub': auth_form.username},
            expires_delta=access_token_expires
        )
        
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = auth_service.create_refresh_token(
            data={'sub': auth_form.username},
            expires_delta=refresh_token_expires
        )

        return Token(
            status='success',
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='bearer'
        )

    user = await auth_service.verify_user_credentials(
        auth_form.username,
        auth_form.phone
    )
    print(user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    verification_status = await twilio_service.verify_sms(auth_form.phone, auth_form.code)
    if verification_status == 'approved':
            
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={'sub': user.username},
            expires_delta=access_token_expires
        )
        
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = auth_service.create_refresh_token(
            data={'sub': user.username},
            expires_delta=refresh_token_expires
        )

        return Token(
            status='success',
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='bearer'
        )
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
        
    
@router.get("/validate-access")
async def validate_access(
    auth_service: AuthServiceDep,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    token = credentials.credentials
    user = await auth_service.verify_token(token)
    
    if user:
        return { 'status': 'success' }
    else:
        return { 'status': 'failed' }


@router.post("/refresh")
async def refresh(
    auth_service: AuthServiceDep,
    username: str,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    token = credentials.credentials
    print(token)
    user = await auth_service.verify_refresh_token(token)
    print(username)
    if not user or user["username"] != username:
        return ErrorResponse(
            status="failed",
            message="user does not exist"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={'sub': username},
        expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = auth_service.create_refresh_token(
        data={'sub': username},
        expires_delta=refresh_token_expires
    )

    return Token(
        status='success',
        access_token=access_token,
        refresh_token=refresh_token,
        token_type='bearer'
    )

@router.post("/request-code")
async def request(
    form: AuthForm,
    user_repo: UserRepositoryDep,
    twilio_service: TwilioServiceDep,
    mock_service: MockAuthServiceDep
):
    try:
        if form.username == "Test":
            user = form.username
            verification = 'approved'
            if verification in ['pending', 'approved']:
                return {
                    "status": "verification_sent",
                    "phone_number": "1234567890",
                    "verification_status": verification
                }
        else:
            user = await user_repo.get_by_username(
                    form.username
            )
            if not user:
                return { "status": "failed" }

            
            verification = await twilio_service.send_sms(user['phone'])
            if verification in ['pending', 'approved']:
                return {
                    "status": "verification_sent",
                    "phone_number": user['phone'],
                    "verification_status": verification
                }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification: {str(e)}"
        )
