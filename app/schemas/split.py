from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class Item(BaseModel):
    name: str
    price: float
    totalPrice: float


class SplitBase(BaseModel):
    receipt_id: int
    user_id: int
    subtotal: float
    items: List[Item]
    tax: float
    tip: float
    misc: float
    total: float


class SplitCreate(SplitBase):
    pass


class SplitUpdate(BaseModel):
    subtotal: Optional[float] = None
    items: Optional[List[Item]] = None
    tax: Optional[float] = None
    tip: Optional[float] = None
    misc: Optional[float] = None
    total: Optional[float] = None


class Split(SplitBase):
    split_id: int


