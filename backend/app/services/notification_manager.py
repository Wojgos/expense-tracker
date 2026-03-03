import uuid
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections grouped by group_id."""

    def __init__(self):
        self._connections: dict[uuid.UUID, list[WebSocket]] = defaultdict(list)

    async def connect(self, group_id: uuid.UUID, websocket: WebSocket):
        await websocket.accept()
        self._connections[group_id].append(websocket)

    def disconnect(self, group_id: uuid.UUID, websocket: WebSocket):
        self._connections[group_id].remove(websocket)
        if not self._connections[group_id]:
            del self._connections[group_id]

    async def broadcast_to_group(self, group_id: uuid.UUID, message: dict):
        dead: list[WebSocket] = []
        for ws in self._connections.get(group_id, []):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(group_id, ws)


manager = ConnectionManager()
