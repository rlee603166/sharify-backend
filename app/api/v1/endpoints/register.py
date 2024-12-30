from fastapi import APIRouter, Depends, HTTPException, status
from schemas import User, UserCreate, RegAuth
from dependencies import UserServiceDep, UserRepositoryDep, TwilioServiceDep


router = APIRouter(
    prefix="/register",
    tags=["register"]
)


@router.post("/", response_model=User)
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


@router.get("/new-phone")
async def phone(
    phone_number: str,
    user_repo: UserRepositoryDep
):
    user = await user_repo.get_by_phone(phone_number)
    
    if user:
        raise HTTPException(
            status_code=409, 
            detail=f"Phone number {phone_number} is already registered"
        )
        
    return {
        'status': 'phone number available'
    }
    
    
@router.get("/verify-phone")
async def verify(
    phone_number: str,
    twilio_service: TwilioServiceDep
):
    try:
        verification = await twilio_service.send_sms(phone_number)
        return {
                "status": "verification_sent",
                "message": f"Verification code sent to phone",
                "verification_status": verification
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send verification: {str(e)}"
        )
        
        
@router.post("/verify-phone")
async def check(
    form_data: RegAuth,
    twilio_service: TwilioServiceDep
):
    try:
        verification_status = await twilio_service.verify_sms(form_data.phone_number, form_data.code)
        if verification_status == 'approved':
            return {
                "status": "success",
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