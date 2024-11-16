from fastapi import APIRouter
from .endpoints import receipt_router

api_v1_router = APIRouter()

api_v1_router.include_router(receipt_router)