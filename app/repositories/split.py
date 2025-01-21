from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from schemas import Split, SplitCreate, SplitUpdate
from .base import BaseRepository


class SplitRepository(BaseRepository[Split, SplitCreate, SplitUpdate]):
    def __init__(self):
        super().__init__(supabase, "splits", pk="split_id")
    
    async def list_by_user(self, user_id: int) -> List[Split]:
        return await self.list(query={'user_id': user_id})
    
    async def list_by_receipt(self, receipt_id: int) -> List[Split]:
        return await self.list(query={'receipt_id': receipt_id})
