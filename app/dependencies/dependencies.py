from typing import Annotated
import httpx
from twilio.rest import Client as TwilioClient
from supabase import create_client, Client as SupabaseClient
from functools import lru_cache
from fastapi import Depends, Request
from repositories import UserRepository, ReceiptRepository, FriendRepository, GroupRepository, UGRepository, SplitRepository
from services import AuthService, UserService, TwilioService, MockTwilioService, ReceiptProcessor, MockAuthService, SplitService, GroupService
from config import Settings, get_settings

settings = get_settings()

"""
repositories
"""

@lru_cache()
def get_user_repository() -> UserRepository:
    return UserRepository()

@lru_cache()
def get_receipt_repository() -> ReceiptRepository:
    return ReceiptRepository()

@lru_cache()
def get_friend_repository() -> FriendRepository:
    return FriendRepository()

@lru_cache()
def get_group_repository() -> GroupRepository:
    return GroupRepository()

@lru_cache()
def get_ug_repository() -> UGRepository:
    return UGRepository()

@lru_cache()
def get_split_repository() -> SplitRepository:
    return SplitRepository()

"""
services
"""

@lru_cache()
def get_auth_service(repo: Annotated[UserRepository, Depends(get_user_repository)]) -> AuthService:
    return AuthService(repository=repo)

@lru_cache()
def get_user_service(
    repo: Annotated[UserRepository, Depends(get_user_repository)],
    auth: Annotated[AuthService, Depends(get_auth_service)],
    friend_repo: Annotated[FriendRepository, Depends(get_friend_repository)]
) -> UserService:
    return UserService(repository=repo, auth=auth, friend_repo=friend_repo)

@lru_cache()
def get_receipt_processor(
    repo: Annotated[ReceiptRepository, Depends(get_receipt_repository)]
) -> ReceiptProcessor:
    return ReceiptProcessor(repository=repo)

@lru_cache()
def get_split_service(repo: Annotated[SplitRepository, Depends(get_split_repository)]):
    return SplitService(split_repo=repo)

@lru_cache()
def get_group_service(repo: Annotated[GroupRepository, Depends(get_group_repository)]):
    return GroupService(repo=repo)

ReceiptProcessorDep = Annotated[ReceiptProcessor, Depends(get_receipt_processor)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
FriendRepositoryDep = Annotated[FriendRepository, Depends(get_friend_repository)]
ReceiptRepositoryDep = Annotated[ReceiptRepository, Depends(get_receipt_repository)]
GroupRepositoryDep = Annotated[GroupRepository, Depends(get_group_repository)]
UGRepositoryDep = Annotated[UGRepository, Depends(get_ug_repository)]
SplitRepositoryDep = Annotated[SplitRepository, Depends(get_split_repository)]

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
SplitServiceDep = Annotated[SplitService, Depends(get_split_service)]
GroupServiceDep = Annotated[GroupService, Depends(get_group_service)]

"""
Third Part Clients
"""

@lru_cache()
def get_supabase_client() -> SupabaseClient:
    return create_client(
        settings.DATABASE_URL,
        settings.SUPABASE_KEY
    )
    
@lru_cache()
def get_twilio_client() -> TwilioClient:
    return TwilioClient(
        settings.TWILIO_ASID,
        settings.TWILIO_AUTH_TOKEN
    )

def get_twilio_service(
    request: Request,
    repo: Annotated[UserRepository, Depends(get_user_repository)],
    settings: Settings = Depends(get_settings),
):
    return TwilioService(
        repo=repo,
        account_sid=settings.TWILIO_ASID,
        auth_token=settings.TWILIO_AUTH_TOKEN,
        service_id=settings.TWILIO_SERVICE_ID,
        http_client=request.app.state.http_client
    )
    
async def get_mock_auth_service() -> MockAuthService:
    return MockAuthService()

async def get_mock_service() -> MockTwilioService:
    return MockTwilioService()


TwilioServiceDep = Annotated[TwilioService, Depends(get_twilio_service)]
TwilioClientDep = Annotated[TwilioClient, Depends(get_twilio_client)]
SupabaseClientDep = Annotated[SupabaseClient, Depends(get_supabase_client)]
MockAuthServiceDep = Annotated[MockAuthService, Depends(get_mock_auth_service)]
MockTwilioServiceDep = Annotated[MockTwilioService, Depends(get_mock_service)]
