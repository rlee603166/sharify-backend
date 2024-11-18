from typing import Optional, List
from fastapi import HTTPException
from schemas import UserInDB, UserCreate

class UserService:
    def __init__(self, repository, auth):
        self.repository = repository
        self.auth_service = auth
        
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
        existing_user = await self.repository.get_by_phone(user.phone_number)
        
        if existing_user:
            raise HTTPException(
                status_code=409,  # Conflict status code
                detail=f"User with phone number {user.phone_number} already exists"
            )
            
        hashed_password = self.auth_service.get_password_hash(user.password)
        
        user_db = UserInDB(
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone_number,
            zip=user.zip,
            hashed_password=hashed_password
        )
        
        return await self.repository.create(user_db)

