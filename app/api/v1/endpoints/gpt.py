from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends
from dependencies import AuthServiceDep
from config import get_settings
from typing import Annotated


settings = get_settings()


router = APIRouter(
    prefix="/gpt",
    tags=["gpt"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/")
def gpt():
    return "Hello from gpt endpoint"

@router.post("/")
async def token(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthServiceDep
):
    print("Received Token:", token)  # Debug: Log the received token
    verified = await auth_service.verify_token(token)
    print("Verified:", verified)
    
    if verified:
        return { "apiKey": settings.OPENAI_API_KEY }
