from pydantic import BaseModel

class ReceiptCreate(BaseModel):
    user_id: str
    image_url: str
    status: str

class ReceiptUpdate(BaseModel):
    user_id: str | None = None
    image_url: str | None = None
    status: str | None = None
    processed_data: str | None = None


