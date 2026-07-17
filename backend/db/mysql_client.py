import aiomysql
import pymysql
import os
import logging
import json
import hashlib
from typing import List
from models.schemas import LeadData

logger = logging.getLogger(__name__)

_pool = None

async def create_pool():
    global _pool
    if _pool is None:
        _pool = await aiomysql.create_pool(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", "root_password"),
            db=os.getenv("MYSQL_DB", "autobrowse_db"),
            autocommit=True,
            minsize=1,
            maxsize=10
        )
        logger.info("MySQL connection pool created.")

async def get_pool():
    global _pool
    if _pool is None:
        await create_pool()
    return _pool

async def close_pool():
    global _pool
    if _pool is not None:
        _pool.close()
        await _pool.wait_closed()
        _pool = None
        logger.info("MySQL connection pool closed.")

async def insert_lead(lead: LeadData):
    pool = await get_pool()
    
    payload_str = json.dumps(lead.data_payload, sort_keys=True)
    hash_string = f"{lead.entity_name}:{payload_str}"
    data_hash = hashlib.md5(hash_string.encode('utf-8')).hexdigest()
    
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            sql = """
                INSERT IGNORE INTO leads (user_id, entity_name, data_payload, classification, source_url, data_hash)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            await cur.execute(sql, (
                lead.user_id, 
                lead.entity_name, 
                json.dumps(lead.data_payload), 
                lead.classification, 
                str(lead.source_url),
                data_hash
            ))

def insert_lead_sync(lead: LeadData):
    """Synchronous insert for background tasks to avoid asyncio loop conflicts."""
    payload_str = json.dumps(lead.data_payload, sort_keys=True)
    hash_string = f"{lead.entity_name}:{payload_str}"
    data_hash = hashlib.md5(hash_string.encode('utf-8')).hexdigest()
    
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "root_password"),
        db=os.getenv("MYSQL_DB", "autobrowse_db"),
        autocommit=True
    )
    try:
        with conn.cursor() as cur:
            sql = """
                INSERT IGNORE INTO leads (user_id, entity_name, data_payload, classification, source_url, data_hash)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql, (
                lead.user_id, 
                lead.entity_name, 
                json.dumps(lead.data_payload), 
                lead.classification, 
                str(lead.source_url),
                data_hash
            ))
    finally:
        conn.close()

async def get_leads_from_db(user_id: str) -> List[LeadData]:
    pool = await get_pool()
        
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT id, user_id, entity_name, data_payload, classification, source_url, extracted_at FROM leads WHERE user_id = %s ORDER BY extracted_at DESC LIMIT 100", 
                (user_id,)
            )
            rows = await cur.fetchall()
            
            leads = []
            for row in rows:
                if isinstance(row.get('data_payload'), str):
                    row['data_payload'] = json.loads(row['data_payload'])
                leads.append(LeadData(**row))
            return leads