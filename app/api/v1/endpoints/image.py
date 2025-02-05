from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os


router = APIRouter(
    prefix="/images",
    tags=["images"]
)

UPLOADS_DIR = "../storage"

@router.get("/")
def hello():
    return { "message": "hello from images"}

@router.get("/pfp/{image_name}")
async def get_profile_picture(image_name: str):
    image_path = os.path.join(UPLOADS_DIR, "pfp", image_name)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Profile picture not found")
    return FileResponse(image_path)


@router.get("/groups/{image_name}")
async def get_group_picture(image_name: str):
    image_path = os.path.join(UPLOADS_DIR, "groups", image_name)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Group picture not found")
    return FileResponse(image_path)


@router.get("/receipts/{image_name}")
async def get_receipt_image(image_name: str):
    image_path = os.path.join(UPLOADS_DIR, "receipts", image_name)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Receipt image not found")
    return FileResponse(image_path)
