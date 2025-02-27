from fastapi import APIRouter
import requests

health_router = APIRouter(tags=["health"])

@health_router.get("/health")
async def health_check():
    return {"status": "healthy"}

@health_router.get("/ping")
async def ping():
    print("Ping received")
    return {"status": "ok"}

@health_router.get("/microservice")
def micro_health():
    url = "http://0.0.0.0:8001/"
    response = requests.get(url)
    data = response.json()
    if data["status"] == "healthy":
        return {"status": "healthy"}
    else:
        return {"status": "not healthy"}