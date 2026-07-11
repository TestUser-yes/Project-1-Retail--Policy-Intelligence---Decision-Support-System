"""WebSocket endpoints for real-time agent execution updates."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from app.realtime.manager import get_connection_manager
from app.core.auth import verify_token
import json
import uuid

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/ws/query-stream/{token}")
async def websocket_query_stream(websocket: WebSocket, token: str):
    """
    WebSocket endpoint for streaming agent execution updates.

    Connection URL: ws://localhost:8001/ws/query-stream/{access_token}

    Messages sent to client:
    - agent_start: Agent execution started
    - agent_update: Agent processing update (reasoning, progress)
    - agent_complete: Agent finished execution
    - final_response: Complete query response
    - error: Error occurred during processing
    """
    # Verify token before accepting connection
    try:
        payload = verify_token(token, token_type="access")
        user_id = payload.get("user_id")
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return
    except Exception as e:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed")
        return

    # Generate unique connection ID
    connection_id = str(uuid.uuid4())

    # Connect to manager
    manager = get_connection_manager()
    await manager.connect(user_id, connection_id, websocket)

    try:
        # Listen for incoming messages
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                message_type = message.get("type")

                # Handle ping/pong
                if message_type == "ping":
                    await manager.send_personal(connection_id, {
                        "type": "pong",
                        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
                    })

                # Handle subscription
                elif message_type == "subscribe":
                    await manager.send_personal(connection_id, {
                        "type": "subscribed",
                        "message": "Successfully subscribed to query updates",
                        "connection_id": connection_id,
                    })

                else:
                    print(f"[WebSocket] Unknown message type: {message_type}")

            except json.JSONDecodeError:
                await manager.send_personal(connection_id, {
                    "type": "error",
                    "error": "Invalid JSON format",
                })
            except Exception as e:
                print(f"[WebSocket] Error processing message: {e}")

    except WebSocketDisconnect:
        manager.disconnect(user_id, connection_id)
        print(f"[WebSocket] Client disconnected: {connection_id}")

    except Exception as e:
        print(f"[WebSocket] Unexpected error: {e}")
        manager.disconnect(user_id, connection_id)


@router.get("/ws/stats")
async def websocket_stats():
    """Get WebSocket connection statistics."""
    manager = get_connection_manager()
    stats = manager.get_connection_stats()
    return {
        "status": "ok",
        "connections": {
            "total_users": stats["total_users"],
            "total_connections": stats["total_connections"],
        }
    }
