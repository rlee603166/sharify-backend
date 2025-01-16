from pydantic import BaseModel, Json
from fastapi import UploadFile
from typing import Dict, Any


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
    extracted_text: str | None = None

