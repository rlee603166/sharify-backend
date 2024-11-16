from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings

from api import api_router


app = FastAPI(
    title= settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"  
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


