from typing import Optional, List
from fastapi import HTTPException
from services import AuthService
from repositories import UserRepository
from schemas import UserInDB, UserCreate

class UserService:
    def __init__(self):
        self.repository = UserRepository()
        self.auth_service = AuthService()
        
    async def get_all_users(self) -> List[UserInDB]:
        return await self.repository.get_all()
    
    async def get_user(self, username: str) -> Optional[UserInDB]:
        try:
            return await self.repository.get_by_username(username)
        except HTTPException as e:
            if e.status_code == 404:
                return None
            raise

    async def create_user(self, user: UserCreate) -> UserInDB:
        # Add any business logic here (e.g., password validation)
        hashed_password = self.auth_service.get_password_hash(user.hashed_password)
        user_db = UserCreate(**user, hashed_password=hashed_password)
        return await self.repository.create(user_db)

