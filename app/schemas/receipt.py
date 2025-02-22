from pydantic import BaseModel, Json
from fastapi import UploadFile
from typing import Dict, Any, Optional, List


class ReceiptForm(BaseModel):
    user_id: int 


class ReceiptCreate(BaseModel):
    user_id: int 
    filepath: str
    status: str


class ReceiptUpdate(BaseModel):
    user_id: int | None = None
    filepath: str | None = None
    status: str | None = None
    processed_data: Dict[str, Any] | None = None


class Item(BaseModel):
    name: str
    price: float
    totalPrice: float


class PersonSplit(BaseModel):
    name: str
    id: Optional[str | int]
    items: List[Item]
    subtotal: float
    finalTotal: float
    tip: float = 0
    tax: float = 0
    misc: float = 0


class Summary(BaseModel):
    tip: float
    tax: float
    misc: float
    total: float


class ProcessedReceipt(BaseModel):
    receipt_id: int
    summary: Summary
    splits: List[PersonSplit]
