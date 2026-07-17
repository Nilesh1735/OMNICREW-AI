from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis
import os
import logging
import asyncio

router = APIRouter()
logger = logging.getLogger(__name__)

redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=int(os.getenv("REDIS_PORT", 6379)), db=0, decode_responses=True)

@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    pubsub = redis_client.pubsub()
    try:
        task_id = await websocket.receive_text()
        pubsub.subscribe(f"task_logs_{task_id}")
        
        while True:
            message = await asyncio.to_thread(pubsub.get_message, ignore_subscribe_messages=True, timeout=1.0)
            if message and message['type'] == 'message':
                await websocket.send_text(message['data'])
            await asyncio.sleep(0.01)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        if 'pubsub' in locals():
            pubsub.close()