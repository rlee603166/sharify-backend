from fastapi import Depends
from services import ReceiptProcessor
from typing import Annotated

def get_receipt_processor() -> ReceiptProcessor:
    return ReceiptProcessor()

ReceiptProcessorDep = Annotated[ReceiptProcessor, Depends(get_receipt_processor)]
