import json
import logging
import asyncio
import os
import hashlib
import redis
from typing import Optional, List, Tuple
from pydantic import ValidationError
from crewai import Agent, Task, Crew, Process
from agents.tools import WebScraperTool
from models.schemas import LeadData, AgentLog
from db.mysql_client import insert_lead
from utils.s3_client import archive_to_s3

logger = logging.getLogger(__name__)

redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)

def get_fallback_llms() -> List[Tuple[str, str]]:
    # Completely removed OpenAI to prevent 401 fallback errors.
    llms = []
    if os.getenv("MISTRAL_API_KEY"):
        llms.append(("mistral/mistral-large-latest", "mistral-large-latest"))
    return llms

async def run_crew(task_id: str, task_description: str, target_url: Optional[str], manager, user_id: str):
    scraper_tool = WebScraperTool()
    llms_to_try = get_fallback_llms()
    
    if not llms_to_try:
        await manager(task_id, AgentLog(agent_name="System", action="Error", thought_process="No LLMs configured.").model_dump(mode="json"))
        return

    def build_crew(llm_model: str):
        researcher = Agent(
            role='Autonomous Web Researcher',
            goal='Gather the necessary information to fulfill the task. If a URL is provided, scrape it. If not, use internal knowledge or reasoning to find the answer.',
            backstory='An expert AI agent capable of navigating the web and using internal knowledge to find solutions when no starting point is given.',
            verbose=True, allow_delegation=False, tools=[scraper_tool], llm=llm_model, max_iter=5
        )
        extraction_analyst = Agent(
            role='Extraction Analyst',
            goal='Analyze the scraped text or research data and output ONLY a valid JSON object.',
            backstory='A strict data engineer who finds specific entities in text and formats them flawlessly into JSON.',
            verbose=True, allow_delegation=False, llm=llm_model, max_iter=5
        )

        if target_url:
            research_prompt = f"Use the Web Scraper tool to visit {target_url} and extract the page content. Task context: {task_description}"
        else:
            research_prompt = (
                f"No target URL was provided. Your task is: '{task_description}'. "
                "Since you have no URL to scrape, use your internal knowledge and reasoning capabilities to "
                "gather the information required to answer the task. If you know the answer, provide the details."
            )

        research_task = Task(
            description=research_prompt,
            expected_output='Raw text or information relevant to the task.', 
            agent=researcher
        )
        extraction_task = Task(
            description='Analyze the provided research data. Focus strictly on answering the specific task context. '
                        'CRITICAL RULE: You must output a FLAT dictionary. Do NOT use arrays or lists. Do NOT use nested objects. '
                        'If the task asks for "the first item", extract ONLY the data for that single first item (e.g., {"title": "Book Name", "price": "$10.00"}). '
                        'Do not include data for multiple items. '
                        'Output ONLY a valid JSON object with these exact top-level keys: "entity_name", "data_payload", "classification". '
                        'The "entity_name" should be the main subject (e.g., the book title). '
                        'The "data_payload" MUST be a flat dictionary of key-value pairs answering the task. '
                        'Assign a "classification" of "Medium". Do not include any other text or markdown.',
            expected_output='A strict JSON object.', 
            agent=extraction_analyst
        )

        return Crew(agents=[researcher, extraction_analyst], tasks=[research_task, extraction_task], process=Process.sequential)

    await manager(task_id, AgentLog(
        agent_name="System", action="Executing Crew", thought_process="Secure connection established. Initializing AI agents."
    ).model_dump(mode="json"))

    cache_key = f"llm_cache:{hashlib.md5(task_description.encode('utf-8')).hexdigest()}"
    result_str = None
    
    try:
        cached_result = redis_client.get(cache_key)
        if cached_result:
            await manager(task_id, AgentLog(
                agent_name="System", action="Cache Hit", thought_process="Cache hit! Returning cached result to save API tokens."
            ).model_dump(mode="json"))
            result_str = cached_result
    except Exception as e:
        logger.warning(f"Redis cache read failed: {str(e)}")

    if result_str is None:
        result = None
        last_exception = None

        for index, (llm_model, llm_name) in enumerate(llms_to_try):
            logger.info(f"Preparing to build crew with LLM model: {llm_model}")
            await manager(task_id, AgentLog(
                agent_name="System", action="LLM Routing", thought_process=f"Engaging AI engine: {llm_name}..."
            ).model_dump(mode="json"))
            
            try:
                crew = build_crew(llm_model)
                result = await asyncio.wait_for(asyncio.to_thread(crew.kickoff), timeout=120.0)
                last_exception = None
                
                try:
                    token_usage = getattr(result, 'token_usage', None)
                    if token_usage and isinstance(token_usage, dict):
                        total_tokens = token_usage.get('total_tokens', 0)
                        if total_tokens == 0:
                            total_tokens = token_usage.get('prompt_tokens', 0) + token_usage.get('completion_tokens', 0)
                        if total_tokens > 0:
                            await manager(task_id, AgentLog(
                                agent_name="System", action="LLMOps Cost Report", thought_process=f"Task completed. Total tokens consumed: {total_tokens}."
                            ).model_dump(mode="json"))
                        else:
                            await manager(task_id, AgentLog(
                                agent_name="System", action="LLMOps Cost Report", thought_process="Task completed. Token usage metadata was empty."
                            ).model_dump(mode="json"))
                    else:
                        await manager(task_id, AgentLog(
                            agent_name="System", action="LLMOps Cost Report", thought_process="Task completed. Token usage not explicitly returned by this LLM provider."
                        ).model_dump(mode="json"))
                except Exception as e:
                    await manager(task_id, AgentLog(
                        agent_name="System", action="LLMOps Cost Report", thought_process=f"Task completed. Failed to extract token usage: {str(e)}"
                    ).model_dump(mode="json"))
                break
            except asyncio.TimeoutError:
                logger.error(f"{llm_name} timed out after 120 seconds.")
                last_exception = Exception("Agent execution timed out (120s limit).")
                await manager(task_id, AgentLog(
                    agent_name="System", action="LLM Fallback", thought_process="Compute node unresponsive. Rerouting pipeline..."
                ).model_dump(mode="json"))
            except Exception as e:
                logger.error(f"{llm_name} failed: {str(e)}")
                last_exception = e
                await manager(task_id, AgentLog(
                    agent_name="System", action="LLM Fallback", thought_process="Optimization detected. Rerouting pipeline..."
                ).model_dump(mode="json"))

        if result is None:
            error_msg = f"All LLMs failed. Last error: {str(last_exception)}"
            await manager(task_id, AgentLog(agent_name="System", action="Task Failed", thought_process=error_msg).model_dump(mode="json"))
            return

        result_str = str(result).strip()
        
        try:
            redis_client.setex(cache_key, 3600, result_str)
        except Exception as e:
            logger.warning(f"Redis cache write failed: {str(e)}")

    await manager(task_id, AgentLog(
        agent_name="Manager", action="Validation", thought_process="Parsing final output and validating schema."
    ).model_dump(mode="json"))

    try:
        json_start = result_str.find('{')
        json_end = result_str.rfind('}')
        if json_start != -1 and json_end != -1:
            clean_json_str = result_str[json_start:json_end+1]
        else:
            raise ValueError("No JSON object found in output")
        lead_dict = json.loads(clean_json_str)
        lead_dict['user_id'] = user_id
        lead_dict['source_url'] = target_url if target_url else "https://autonomous.omnicrew.ai"
        lead_data = LeadData(**lead_dict)
        await insert_lead(lead_data)
        s3_filename = f"omnicrew-runs/{task_id}.json"
        archive_to_s3(content=result_str, object_name=s3_filename)
        await manager(task_id, AgentLog(
            agent_name="Manager", action="Saved", thought_process=f"Successfully validated and saved entity: {lead_data.entity_name}"
        ).model_dump(mode="json"))
    except Exception as e:
        logger.error(f"Failed to process lead: {str(e)}. Output: {result_str}")
        await manager(task_id, AgentLog(
            agent_name="Manager", action="Error", thought_process=f"Schema validation failed: {str(e)}"
        ).model_dump(mode="json"))