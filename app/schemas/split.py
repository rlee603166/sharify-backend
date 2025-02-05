from typing import List, Optional
from pydantic import BaseModel


class SplitBase(BaseModel):
    receipt_id: int
    user_id: int
    subtotal: float
    items: List[dict]
    tax: float
    tip: float
    misc: float
    total: float


class SplitCreate(SplitBase):
    pass


class SplitUpdate(BaseModel):
    subtotal: Optional[float] = None
    items: Optional[List[dict]] = None
    tax: Optional[float] = None
    tip: Optional[float] = None
    misc: Optional[float] = None
    total: Optional[float] = None


class Split(SplitBase):
    split_id: int


