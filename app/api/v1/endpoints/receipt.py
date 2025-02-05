from fastapi import APIRouter, HTTPException, UploadFile, Form, BackgroundTasks
from dependencies import ReceiptProcessorDep, ReceiptRepositoryDep, SplitServiceDep, SplitRepositoryDep
from pydantic import ValidationError
from schemas import ProcessedReceipt
from typing import Annotated


router = APIRouter(
    prefix="/receipts",
    tags=["receipts"]
)


@router.post("/")
async def create_receipt(
    user_id: Annotated[int, Form()],
    image: UploadFile,
    service: ReceiptProcessorDep,
    background_tasks: BackgroundTasks
):
    png = await service.standardize(image)

    filepath = service.create_filepath(user_id)

    receipt_data = {
        "user_id": user_id,
        "filepath": filepath,
        "status": "pending"
    }
    
    background_tasks.add_task(service.save_and_process, png, filepath)

    return await service.upload(receipt_data)


@router.get("/{receipt_id}")
async def get_receipt(receipt_id: int, repo: ReceiptRepositoryDep):
    return await repo.get(receipt_id)
    

@router.post("/venmo")
async def process_venmo(receipt: ProcessedReceipt, service: SplitServiceDep):
    try:
        print("\n=== Received Venmo Processing Request ===")
        print(f"\nReceipt ID: {receipt.receipt_id}")
        
        first_split = receipt.splits[0]
        print("\nFirst split data:")
        print(f"Items: {first_split.items}")
        print(f"Subtotal: {first_split.subtotal}")
        print(f"Tax: {first_split.tax}")
        print(f"Tip: {first_split.tip}")
        print(f"Misc: {first_split.misc}")
        print(f"Final Total: {first_split.finalTotal}")
        
        result = await service.upload(receipt.receipt_id, first_split)
        return { 
            "split": result,
            "status": "success"
        }
    except ValidationError as e:
        print(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
