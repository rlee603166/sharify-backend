from fastapi import HTTPException
from .base import BaseRepository
from schemas import UserCreate, UserUpdate
from database import supabase

class UserRepository(BaseRepository[dict, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(supabase, "users", pk="user_id")

    async def get_by_query(self, query: str):
        try:
            search_pattern = f"%{query}%"
            response = (
                self.db.table(self.table_name)
                .select("*")
                .or_(f"name.ilike.{search_pattern},username.ilike.{search_pattern}")
                .limit(20)
                .execute()
            )
            if not response.data:
                return None
            return response.data
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


    async def get_by_email(self, email: str):
        try:
            response = (
                self.db.table(self.table_name)
                    .select("*")
                    .eq("email", email)
                    .execute()
            )
            if not response.data:
                return None
            return response.data[0]
        
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        
    async def get_by_username(self, username: str):
        try:
            response = (
                self.db.table(self.table_name)
                    .select("*")
                    .eq("username", username)
                    .execute()
            )
            # Check if we got any results
            if not response.data:
                return None
            return response.data[0]
        except Exception as e:
            if "JSON object requested" in str(e):  # Handle the specific no-rows error
                return None
            raise HTTPException(status_code=400, detail=str(e))
        
        
    async def get_by_phone(self, phone: str):
        try:
            response = (
                self.db.table(self.table_name)
                    .select("*")
                    .eq("phone", phone)
                    .execute()
            )

            if response.data and len(response.data) > 0:
                return response.data[0]
            return None  
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
