from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional
from .enums import SplitMethod


class LineItem(BaseModel):
    name: str
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")
    price: float = Field(gt=0, description="Price must be greater than 0")
    assigned_to: Optional[List[str]] = None

    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        return round(float(v), 2)

class ReceiptRequest(BaseModel):
    items: List[LineItem]
    additional_charges: Dict[str, float]
    party_size: Optional[int] = Field(gt=0, default=None)
    split_method: SplitMethod = Field(default=SplitMethod.EQUAL)
    assigned_parties: Optional[List[str]] = None

    @field_validator('additional_charges')
    @classmethod
    def validate_charges(cls, v):
        return {k: round(float(amount), 2) for k, amount in v.items()}

    @field_validator('assigned_parties')
    @classmethod
    def validate_assigned_parties(cls, v, info):
        # Note: values is now accessed through info.data
        if info.data.get('split_method') == SplitMethod.ITEMIZED and not v:
            raise ValueError("assigned_parties is required for itemized split")
        return v

class ChargesModel(BaseModel):
    tax: float
    tip: float
    service_fee: Optional[float] = None

class PerPersonCharges(BaseModel):
    base_amount: float
    charges: ChargesModel
    total: float

class ItemDetail(BaseModel):
    name: str
    quantity: int
    price: float
    share: float

class PersonTotal(BaseModel):
    items: List[ItemDetail]
    subtotal: float
    charges: ChargesModel
    total: float

class ReceiptResponse(BaseModel):
    split_method: str
    subtotal: float
    charges: ChargesModel
    total_paid: float
    per_person: Optional[PerPersonCharges] = None
    person_totals: Optional[Dict[str, PersonTotal]] = None
