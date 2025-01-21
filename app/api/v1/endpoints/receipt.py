import json
import re
import asyncio
from fastapi import APIRouter, HTTPException, UploadFile, Form, BackgroundTasks
from dependencies import ReceiptProcessorDep, ReceiptRepositoryDep 
from pydantic import BaseModel
from schemas import ReceiptForm, ProcessedReceipt
from typing import Annotated


class Prompt(BaseModel):
    prompt: str

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
    print(user_id)
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
    print(receipt_id)
    return await repo.get(receipt_id)
    


@router.post("/venmo")
async def process_venmo(receipt: ProcessedReceipt):
    print("\n=== Received Venmo Processing Request ===")
    print(f"\nSummary:")
    print(f"Total: ${receipt.summary.total:.2f}")
    print(f"Tip: ${receipt.summary.tip:.2f}")
    print(f"Tax: ${receipt.summary.tax:.2f}")
    print(f"Misc: ${receipt.summary.misc:.2f}")
    
    print("\nSplits:")
    for person in receipt.splits:
        print(f"\n{person.name}:")
        print(f"ID: {person.id}")
        for item in person.items:
            print(f"  - {item.name}: ${item.totalPrice:.2f}")
        print(f"Subtotal: ${person.subtotal:.2f}")
        print(f"Final Total: ${person.finalTotal:.2f}")
        print(f"Charges: Tip=${person.tip:.2f}, Tax=${person.tax:.2f}, Misc=${person.misc:.2f}")

    return {"status": "success", "message": "Venmo requests queued"}
