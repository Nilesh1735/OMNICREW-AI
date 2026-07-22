import json
import logging
import asyncio
import os
import hashlib
import redis
import litellm
from typing import Optional, List, Tuple
from pydantic import ValidationError
from crewai import Agent, Task, Crew, Process, LLM
from agents.tools import WebScraperTool, SnovEmailFinderTool
from models.schemas import LeadData, AgentLog
from db.mysql_client import insert_lead_sync
from utils.s3_client import archive_to_s3

logger = logging.getLogger(__name__)

litellm.drop_params = True
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)

def get_fallback_llms() -> List[Tuple[object, str]]:
    """
    Hardcoded 3-Tier LLM Fallback Router.
    1. DeepSeek (Primary - GPT-4 level quality, ultra-cheap)
    2. Mistral AI
    3. Google Gemini
    """
    llms = []
    
    # 1. DeepSeek (Primary)
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if deepseek_key:
        try:
            logger.info("Initializing DeepSeek (Tier 1).")
            llms.append((
                LLM(
                    model="deepseek-chat", 
                    api_key=deepseek_key,
                    base_url="https://api.deepseek.com/v1"
                ),
                "DeepSeek"
            ))
        except Exception as e:
            logger.error(f"DeepSeek init failed: {e}")

    # 2. Mistral AI (Secondary)
    mistral_key = os.getenv("MISTRAL_API_KEY")
    if mistral_key:
        try:
            logger.info("Initializing Mistral AI (Tier 2).")
            llms.append((
                LLM(
                    model="openai/mistral-large-latest", 
                    api_key=mistral_key, 
                    base_url="https://api.mistral.ai/v1/"
                ),
                "Mistral AI"
            ))
        except Exception as e:
            logger.error(f"Mistral init failed: {e}")

    # 3. Google Gemini (Tertiary)
    gemini_key = os.getenv("GOOGLE_API_KEY")
    if gemini_key and gemini_key != "AIzaSy_your_gemini_key_here":
        try:
            logger.info("Initializing Google Gemini (Tier 3).")
            llms.append((
                LLM(model="gemini/gemini-1.5-flash", api_key=gemini_key),
                "Gemini"
            ))
        except Exception as e:
            logger.error(f"Gemini init failed: {e}")

    if not llms:
        raise ValueError("No LLMs configured. Please set API keys in environment variables.")
        
    return llms

async def run_crew(task_id: str, task_description: str, target_url: Optional[str], manager, user_id: str):
    scraper_tool = WebScraperTool()
    email_tool = SnovEmailFinderTool()
    llms_to_try = get_fallback_llms()
    
    if not llms_to_try:
        await manager(task_id, AgentLog(agent_name="System", action="Error", thought_process="No LLMs configured.").model_dump(mode="json"))
        return

    def build_crew(llm_obj: object):
        researcher = Agent(
            role='Autonomous Web Researcher',
            goal='Gather the necessary information to fulfill the task. If a URL is provided, scrape it. If the task asks for an email, scrape the page to find the person\'s name and company, then use the Email Finder Tool.',
            backstory='An expert AI agent capable of navigating the web, extracting B2B leads, and using APIs to enrich data.',
            verbose=True, allow_delegation=False, 
            tools=[scraper_tool, email_tool], 
            llm=llm_obj, max_iter=10, 
            cache=False
        )
        extraction_analyst = Agent(
            role='Extraction Analyst',
            goal='Analyze the scraped text or research data and output ONLY a valid JSON object.',
            backstory='A strict data engineer who finds specific entities in text and formats them flawlessly into JSON.',
            verbose=True, allow_delegation=False, llm=llm_obj, max_iter=5,
            cache=False
        )

        # --- DYNAMIC RESEARCH PROMPT ---
        research_prompt = (
            f"Your task is: '{task_description}'. "
            "CRITICAL INSTRUCTION: You MUST use the Web Scraper tool to extract the required information. Do NOT use internal knowledge. "
            "CONDITIONAL LOGIC: If the task specifically asks you to find an email address, and you have scraped a person's name and company domain, "
            "you are STRICTLY REQUIRED to call the 'Email Finder Tool'. Do not guess the email. "
            "If the task does NOT ask for an email, do not use the Email Finder Tool."
        )
        
        research_task = Task(
            description=research_prompt,
            expected_output='Raw text, names, and the email (if requested) returned by the tool.', 
            agent=researcher
        )
        
        # --- DYNAMIC EXTRACTION PROMPT ---
        extraction_task = Task(
            description='Analyze the provided research data. Focus strictly on answering the specific task context. '
                        'CRITICAL RULE: You must output a FLAT dictionary. Do NOT use arrays or lists. Do NOT use nested objects. '
                        'Output ONLY a valid JSON object with these exact top-level keys: "entity_name", "data_payload", "classification", "source_url". '
                        'The "entity_name" should be the main subject of the task. '
                        'The "data_payload" MUST be a flat dictionary of key-value pairs answering the task. '
                        'CONDITIONAL LOGIC: '
                        '1. If the task specifically asks to find an email, the "data_payload" MUST contain the key "email" with the email address returned by the tool. '
                        '2. If the task asks for a list (e.g., "top 5 items"), DO NOT use arrays. Instead, output them as distinct keys in the dictionary (e.g., "item_1": "Repo A", "item_2": "Repo B"). '
                        '3. If the task asks for general information, just include the relevant facts as key-value pairs. '
                        'The "source_url" MUST be the exact URL you visited with the web scraper tool. '
                        'Assign a "classification" of "Medium". Do not include any other text or markdown.',
            expected_output='A strict JSON object.', 
            agent=extraction_analyst
        )

        return Crew(
            agents=[researcher, extraction_analyst], 
            tasks=[research_task, extraction_task], 
            process=Process.sequential,
            cache=False
        )

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

        for index, (llm_obj, llm_name) in enumerate(llms_to_try):
            logger.info(f"Preparing to build crew with LLM object of type: {type(llm_obj)}")
            await manager(task_id, AgentLog(
                agent_name="System", action="LLM Routing", thought_process=f"Engaging AI engine: {llm_name}..."
            ).model_dump(mode="json"))
            
            try:
                crew = build_crew(llm_obj)
                result = await asyncio.wait_for(asyncio.to_thread(crew.kickoff), timeout=240.0)
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
                logger.error(f"{llm_name} timed out after 240 seconds.")
                last_exception = Exception("Agent execution timed out (240s limit).")
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
        
        if not lead_dict.get('source_url'):
            lead_dict['source_url'] = target_url if target_url else "Internal Knowledge"
        
        # FIX: Fallback for LLM dropping the classification field
        if lead_dict.get('classification') not in ['High', 'Medium', 'Low']:
            lead_dict['classification'] = 'Medium'
            
        lead_data = LeadData(**lead_dict)
        insert_lead_sync(lead_data)
        
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