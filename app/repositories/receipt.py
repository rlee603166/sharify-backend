from .base import BaseRepository
from fastapi import HTTPException
from database import supabase
from schemas import ReceiptCreate, ReceiptUpdate

class ReceiptRepository(BaseRepository[dict, ReceiptCreate, ReceiptUpdate]):
    def __init__(self):
        super().__init__(supabase, "receipts", pk="receipt_id")

    async def get_by_path(self, filepath: str): 
        try:
            response = (
                self.db.table(self.table_name)
                    .select("*")
                    .eq("filepath", filepath)
                    .execute()
            )
            if not response.data:
                return None
            return response.data[0]

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


