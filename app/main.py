from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
from config import get_settings
from api import api_router
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import threading

from selenium_manager import initialize_driver, get_driver_lock


settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):

    app.state.http_client = httpx.AsyncClient()
    app.state.counter = 0
    
    yield
    
    # Shutdown: cleanup
    await app.state.http_client.aclose()

app = FastAPI(
    title= settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def startup():
    initialize_driver()  # Initialize the driver when the app starts

@app.on_event("shutdown")
def shutdown():
    driver = initialize_driver()
    if driver:
        driver.quit()
