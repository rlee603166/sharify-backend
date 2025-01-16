import json
import re
import asyncio
from fastapi import APIRouter, HTTPException, UploadFile, Form, BackgroundTasks
from dependencies import ReceiptProcessorDep, ReceiptRepositoryDep 
from pydantic import BaseModel
from schemas import ReceiptForm
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
    

