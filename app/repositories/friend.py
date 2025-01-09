from fastapi import HTTPException
from database import supabase
from .base import BaseRepository
from schemas import CreateFriend, UpdateFriend


class FriendRepository(BaseRepository[dict, CreateFriend, UpdateFriend]):
    def __init__(self):
        super().__init__(supabase, "friends", pk="friend_id")

    async def get_by_user(self, user_id: int):
        try:
            response = (
                self.db.table(self.table_name)
                    .select("*")
                    .or_(f"user_1.eq.{user_id}, user_2.eq.{user_id}")
                    .execute()
            )
            if not response.data:
                return None
            return response.data
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
