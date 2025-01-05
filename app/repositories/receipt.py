from .base import BaseRepository
from database import supabase
from schemas import ReceiptCreate, ReceiptUpdate

class ReceiptRepository(BaseRepository[dict, ReceiptCreate, ReceiptUpdate]):
    def __init__(self):
        super().__init__(supabase, "receipts", pk="receipt_id")

