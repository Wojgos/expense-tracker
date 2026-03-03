import uuid

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.security import decode_access_token
from app.services.notification_manager import manager

router = APIRouter()


@router.websocket("/ws/groups/{group_id}")
async def group_websocket(
    websocket: WebSocket,
    group_id: uuid.UUID,
    token: str = Query(),
):
    user_id = decode_access_token(token)
    if user_id is None:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await manager.connect(group_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(group_id, websocket)
