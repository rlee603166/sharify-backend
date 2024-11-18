from typing import Annotated
from twilio.rest import Client as TwilioClient
from supabase import create_client, Client as SupabaseClient
from functools import lru_cache
from fastapi import Depends
from services import ReceiptProcessor
from repositories import UserRepository
from services import AuthService, UserService
from config import get_settings

settings = get_settings()


"""
Receipt Processor
"""
@lru_cache()
def get_receipt_processor() -> ReceiptProcessor:
    return ReceiptProcessor()

ReceiptProcessorDep = Annotated[ReceiptProcessor, Depends(get_receipt_processor)]


"""
User and Auth
"""

@lru_cache()
def get_user_repository() -> UserRepository:
    return UserRepository()


@lru_cache()
def get_auth_service(repo: Annotated[UserRepository, Depends(get_user_repository)]) -> AuthService:
    return AuthService(repository=repo)

@lru_cache()
def get_user_service(
    repo: Annotated[UserRepository, Depends(get_user_repository)],
    auth: Annotated[UserRepository, Depends(get_auth_service)]
) -> UserService:
    return UserService(repository=repo, auth=auth)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]


"""
Third Part Clients
"""

@lru_cache()
def get_twilio_client() -> TwilioClient:
    return TwilioClient(
        settings.TWILIO_ASID,
        settings.TWILIO_AUTH_TOKEN
    )

@lru_cache()
def get_supabase_client() -> SupabaseClient:
    return create_client(
        settings.DATABASE_URL,
        settings.SUPABASE_KEY
    )


TwilioClientDep = Annotated[TwilioClient, Depends(get_twilio_client)]
SupabaseClientDep = Annotated[SupabaseClient, Depends(get_supabase_client)]