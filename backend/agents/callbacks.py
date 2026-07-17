import logging
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.agents import AgentAction, AgentFinish
from models.schemas import AgentLog
import asyncio

logger = logging.getLogger(__name__)

class WebSocketStreamingCallback(BaseCallbackHandler):
    """
    Custom callback to stream CrewAI/LangChain thoughts and actions 
    directly to the FastAPI WebSocket manager.
    """
    def __init__(self, manager, task_id: str):
        self.manager = manager
        self.task_id = task_id

    async def _broadcast(self, agent_name: str, action: str, thought: str):
        log = AgentLog(agent_name=agent_name, action=action, thought_process=thought)
        # Run broadcast in the background
        asyncio.create_task(self.manager.broadcast(log.model_dump(mode="json")))

    def on_agent_action(self, action: AgentAction, **kwargs):
        """Triggered when the agent decides to use a tool or think."""
        agent_name = kwargs.get("run_id", "Agent")
        thought = action.log.strip()
        # Use asyncio.run_coroutine_threadsafe if running in a thread, but since crewai runs in a thread, we use create_task directly on the running loop
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._broadcast(agent_name, "Thought", thought))
        except RuntimeError:
            pass # Fallback if no loop is running in this exact thread context

    def on_agent_finish(self, finish: AgentFinish, **kwargs):
        """Triggered when the agent completes its task."""
        agent_name = kwargs.get("run_id", "Agent")
        thought = finish.return_values.get("output", "Task completed.").strip()
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._broadcast(agent_name, "Finished", thought))
        except RuntimeError:
            pass

    def on_tool_end(self, output: str, **kwargs):
        """Triggered when a tool (like Web Scraper) finishes."""
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._broadcast("System", "Tool Output", output[:200] + "..."))
        except RuntimeError:
            pass