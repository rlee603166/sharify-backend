from fastapi import APIRouter
from .endpoints import *

api_v1_router = APIRouter()

api_v1_router.include_router(receipt_router)
api_v1_router.include_router(user_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(register_router)
api_v1_router.include_router(group_router)
api_v1_router.include_router(image_router)
