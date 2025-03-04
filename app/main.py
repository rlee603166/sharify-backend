from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncpg
from fastapi.middleware.cors import CORSMiddleware
import asyncio
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

active_connections = set()

async def listen_for_user_count():
    conn = await asyncpg.connect(settings.DATABASE_URL)
    await conn.add_listener('user_count_channel', handle_user_count)

async def handle_user_count(conn, pid, channel, payload):
    for connection in active_connections:
        try:
            await connection.send_text(payload)
        except Exception as e:
            print(f"Failed to send to client: {e}")
            active_connections.remove(connection)

@app.websocket("/ws/user-count")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    print(f"New connection: {websocket.client}")

    user_count = await get_user_count()

    print(user_count)
    await websocket.send_text(str(user_count))

    try:
        while True:
            await asyncio.sleep(3600)  # Keeps the connection alive
    except WebSocketDisconnect:
        print(f"Disconnected: {websocket.client}")
        active_connections.remove(websocket)

async def get_user_count():
    conn = await asyncpg.connect(settings.PSQL_URL)
    print(conn)
    user_count = await conn.fetchval('SELECT COUNT(*) FROM users')
    await conn.close()
    return user_count

@app.on_event("startup")
async def user_startup():
    asyncio.create_task(listen_for_user_count())


@app.on_event("startup")
def startup():
    initialize_driver()


@app.on_event("shutdown")
def shutdown():
    driver = initialize_driver()
    if driver:
        driver.quit()
