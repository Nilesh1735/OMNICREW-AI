from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from slowapi import Limiter
from slowapi.util import get_remote_address
from models.schemas import TaskResponse, LeadData
from db.mysql_client import get_leads_from_db, get_pool
from typing import List
from pydantic import BaseModel
import uuid
import logging
import aiomysql
import os
import jwt

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()
logger = logging.getLogger(__name__)

class AutonomousTaskRequest(BaseModel):
    task_description: str

# --- DECODE JWT TO GET REAL USER ID ---
async def get_current_user_id(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    
    # DEBUG LOG: This will show us exactly what the frontend is sending
    logger.info(f"Received Auth Header: {auth_header}")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = auth_header.split(" ")[1]
    secret = os.getenv("JWT_SECRET", "supersecretjwt12345")
    
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/webhook/start-task", response_model=TaskResponse)
@limiter.limit("5/minute")
async def start_task(
    request: Request,
    payload: AutonomousTaskRequest, 
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id)
):
    task_id = str(uuid.uuid4())
    
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("INSERT INTO tasks (id, user_id, description, status) VALUES (%s, %s, %s, %s)", 
                              (task_id, user_id, payload.task_description, "queued"))

    from tasks import execute_agent_crew_task
    background_tasks.add_task(execute_agent_crew_task, task_id, payload.task_description, None, user_id)
    
    return TaskResponse(task_id=task_id, status="queued", message="Autonomous task successfully queued.")

@router.get("/tasks/history")
async def get_task_history(user_id: str = Depends(get_current_user_id)):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM tasks WHERE user_id = %s ORDER BY created_at DESC LIMIT 20", (user_id,))
            return await cur.fetchall()

@router.get("/leads", response_model=List[LeadData])
async def get_leads(user_id: str = Depends(get_current_user_id)):
    try:
        leads = await get_leads_from_db(user_id=user_id)
        return leads
    except Exception as e:
        logger.error(f"Failed to fetch leads: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error retrieving leads.")