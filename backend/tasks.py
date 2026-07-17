import asyncio
import json
import os
import redis
import logging
from agents.crew import run_crew
from db.mysql_client import create_pool
from models.schemas import AgentLog

logger = logging.getLogger(__name__)

redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=int(os.getenv("REDIS_PORT", 6379)), db=0, decode_responses=True)

async def redis_publisher(task_id: str, log_data: dict):
    log_data['task_id'] = task_id
    redis_client.publish(f"task_logs_{task_id}", json.dumps(log_data))

# Removed @celery_app.task so FastAPI BackgroundTasks can call this directly
def execute_agent_crew_task(task_id: str, task_description: str, target_url: str, user_id: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(create_pool())
    
    async def run_async():
        try:
            await run_crew(task_id, task_description, target_url, redis_publisher, user_id)
            # BROADCAST COMPLETION HERE
            await redis_publisher(task_id, AgentLog(
                agent_name="System", action="Task Completed", thought_process="Extraction sequence finished successfully."
            ).model_dump(mode="json"))
        except Exception as e:
            logger.error(f"Task failed: {str(e)}")
            await redis_publisher(task_id, {"agent_name": "System", "action": "Task Failed", "thought_process": str(e)})

    loop.run_until_complete(run_async())