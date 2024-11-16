from fastapi import APIRouter, HTTPException
from typing import Dict
from schemas import ExampleResponses, ReceiptRequest, ReceiptResponse
from dependencies import ReceiptProcessorDep


router = APIRouter(
    prefix="/receipts",
    tags=["receipts"]
)

@router.post(
    "/process",
    response_model=ReceiptResponse
)
async def process_receipt(receipt: ReceiptRequest, processor: ReceiptProcessorDep):
    """
    Process a receipt and calculate splits based on the specified method.
    
    - Equal split divides all costs evenly among the party
    - Itemized split allows assigning specific items to specific people
    """
    try:
        result = processor.process_receipt(receipt)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Add documentation examples
process_receipt.responses = {
    200: {
        "description": "Successful receipt processing",
        "content": {
            "application/json": {
                "examples": {
                    "equal_split": {
                        "summary": "Equal Split Example",
                        "value": ExampleResponses.equal_split_example
                    },
                    "itemized_split": {
                        "summary": "Itemized Split Example",
                        "value": ExampleResponses.itemized_split_example
                    }
                }
            }
        }
    }
}