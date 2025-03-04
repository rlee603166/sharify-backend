# from fastapi import APIRouter, WebSocket
# from webhook import listen_for_user_count, get_connections
# import asyncio
# import asyncpg
#
#
# router = APIRouter(
#     prefix="/live",
#     tags=["live"]
# )
#
#
# active_connections = get_connections()
#
# @router.get("/")
# def hello():
#     return { "message": "Hello from live count" }
#
# @router.websocket("/ws/user-count")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     active_connections.add(websocket)
#
#     try:
#         while True:
#             await asyncio.sleep(3600)
#     except WebSocketDisconnect:
#         active_connections.remove(websocket)
#
#
