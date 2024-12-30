from .receipt import router as receipt_router
from .user import router as user_router
from .auth import router as auth_router
from .register import router as register_router


__all__ = [
    "receipt_router",
    "user_router",
    "auth_router",
    "register_router"
]