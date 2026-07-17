from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any
from datetime import datetime

class WebhookTrigger(BaseModel):
    task_description: str = Field(..., min_length=10, description="The high-level task for the agents to execute.")
    target_url: Optional[str] = Field(None, description="Optional starting URL for the browser.")
    priority: Literal["high", "medium", "low"] = Field("medium", description="Priority level of the task.")

class AgentLog(BaseModel):
    agent_name: str = Field(..., description="Name of the agent generating the log.")
    action: str = Field(..., description="The action performed by the agent.")
    thought_process: Optional[str] = Field(None, description="The reasoning step of the agent.")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class LeadData(BaseModel):
    id: Optional[int] = None
    user_id: str = Field(..., description="The ID of the user who initiated the task.")
    entity_name: str = Field(..., description="The main subject of the page (e.g., Company, Study Title, CVE ID).")
    data_payload: Dict[str, Any] = Field(..., description="A dictionary of all extracted key-value pairs.")
    classification: Literal["High", "Medium", "Low"] = Field("Medium", description="A generic classification or score based on context.")
    # Changed from HttpUrl to str to prevent Pydantic validation crashes
    source_url: str = Field("https://omnicrew.ai", description="URL where the data was extracted.")
    extracted_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class TaskResponse(BaseModel):
    task_id: str
    status: Literal["queued", "processing", "completed", "failed"]
    message: str