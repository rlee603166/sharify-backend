import os
import asyncio
from typing import Optional, List
from fastapi import HTTPException
from schemas import UserInDB, UserCreate

class UserService:
    def __init__(self, repository, auth, friend_repo):
        self.repository = repository
        self.auth_service = auth
        self.friend_repo = friend_repo
        self.pwd = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(__file__))
            ), 
            "storage/pfp"
        )
        
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

    async def get_friends(self, user_id: int):
        friends = await self.friend_repo.get_by_user(user_id)
        friend_ids =  [
            friend["user_1"] if friend["user_1"] != user_id else friend["user_2"] 
            for friend in friends
        ]

        tasks = [self.repository.get(id) for id in friend_ids]

        friends = await asyncio.gather(*tasks)
        
        result = []

        for friend in friends:
            result.append(UserInDB(
                user_id=friend["user_id"],
                name=friend["name"],
                username=friend["username"],
                phone=friend["phone"],
                created_at=friend["created_at"],
                imageUri=friend["imageUri"],
            ))

        return result


