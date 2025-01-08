from fastapi import APIRouter

health_router = APIRouter(tags=["health"])

@health_router.get("/health")
async def health_check():
    return {"status": "healthy"}

@health_router.get("/ping")
async def ping():
    print("Ping received")
    return {"status": "ok"}
