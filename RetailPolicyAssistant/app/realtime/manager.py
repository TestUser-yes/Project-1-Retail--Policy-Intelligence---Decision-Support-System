"""WebSocket connection manager for real-time communication."""

from typing import Dict, Set, Optional
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections and broadcasts messages."""

    def __init__(self):
        # Active connections: {user_id: {connection_id: websocket}}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        # Connection metadata for tracking
        self.connection_metadata: Dict[str, Dict] = {}

    async def connect(self, user_id: str, connection_id: str, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()

        # Initialize user dict if not exists
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}

        # Register connection
        self.active_connections[user_id][connection_id] = websocket
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "connected_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
        }

    def disconnect(self, user_id: str, connection_id: str):
        """Remove a WebSocket connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id].pop(connection_id, None)
            if not self.active_connections[user_id]:
                self.active_connections.pop(user_id, None)

        self.connection_metadata.pop(connection_id, None)

    async def send_personal(self, connection_id: str, message: dict):
        """Send message to a specific connection."""
        # Find the connection
        for user_id, connections in self.active_connections.items():
            if connection_id in connections:
                websocket = connections[connection_id]
                try:
                    await websocket.send_json(message)
                    # Update last activity
                    if connection_id in self.connection_metadata:
                        self.connection_metadata[connection_id]["last_activity"] = datetime.utcnow().isoformat()
                except Exception as e:
                    print(f"[WebSocket] Error sending personal message: {e}")
                    self.disconnect(user_id, connection_id)
                return
        print(f"[WebSocket] Connection not found: {connection_id}")

    async def broadcast_to_user(self, user_id: str, message: dict):
        """Broadcast message to all connections of a specific user."""
        if user_id not in self.active_connections:
            return

        disconnected = []
        for connection_id, websocket in self.active_connections[user_id].items():
            try:
                await websocket.send_json(message)
                # Update last activity
                if connection_id in self.connection_metadata:
                    self.connection_metadata[connection_id]["last_activity"] = datetime.utcnow().isoformat()
            except Exception as e:
                print(f"[WebSocket] Error broadcasting to user {user_id}: {e}")
                disconnected.append(connection_id)

        # Remove disconnected connections
        for connection_id in disconnected:
            self.disconnect(user_id, connection_id)

    async def broadcast_all(self, message: dict):
        """Broadcast message to all connected users."""
        disconnected = []
        for user_id in list(self.active_connections.keys()):
            for connection_id in list(self.active_connections[user_id].keys()):
                try:
                    websocket = self.active_connections[user_id][connection_id]
                    await websocket.send_json(message)
                    # Update last activity
                    if connection_id in self.connection_metadata:
                        self.connection_metadata[connection_id]["last_activity"] = datetime.utcnow().isoformat()
                except Exception as e:
                    print(f"[WebSocket] Error broadcasting: {e}")
                    disconnected.append((user_id, connection_id))

        # Remove disconnected connections
        for user_id, connection_id in disconnected:
            self.disconnect(user_id, connection_id)

    def get_user_connections(self, user_id: str) -> int:
        """Get number of active connections for a user."""
        return len(self.active_connections.get(user_id, {}))

    def get_total_connections(self) -> int:
        """Get total number of active connections."""
        total = 0
        for connections in self.active_connections.values():
            total += len(connections)
        return total

    def get_connection_stats(self) -> dict:
        """Get connection statistics."""
        total_users = len(self.active_connections)
        total_connections = self.get_total_connections()
        return {
            "total_users": total_users,
            "total_connections": total_connections,
            "active_connections": self.active_connections,
        }


# Global connection manager instance
_manager: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """Get or create the global connection manager."""
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
    return _manager
