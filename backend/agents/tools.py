from langchain_core.tools import BaseTool
import logging
import json
import requests
from bs4 import BeautifulSoup
from security.validators import validate_target_url
from security.ssrf_blocker import check_ssrf_and_exposed_files

logger = logging.getLogger(__name__)

class WebScraperTool(BaseTool):
    name: str = "Web Scraper"
    description: str = "Useful for navigating to a specific URL and extracting all visible text content from the web page."

    def _run(self, url: str) -> str:
        """Synchronous fallback using requests (used by CrewAI sync execution)."""
        if url.strip().startswith("{"):
            try:
                data = json.loads(url)
                url = data.get("url", url)
            except Exception:
                pass
            
        logger.info(f"Security validation for URL: {url}")
        
        try:
            check_ssrf_and_exposed_files(url)
            validation = validate_target_url(url)
            if not validation["is_valid"]:
                return f"Security Block: {', '.join(validation['errors'])}"
            if validation["warnings"]:
                logger.warning(f"Security Warnings for {url}: {', '.join(validation['warnings'])}")
        except ValueError as e:
            return str(e)
        except Exception as e:
            return f"Security validation failed: {str(e)}"
            
        logger.info(f"Scraping URL with requests fallback: {url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
            response = requests.get(url, timeout=15, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text(separator='\n', strip=True)
            if text_content:
                return text_content[:5000]
            return "No text content found on the page."
        except Exception as e:
            return f"Failed to scrape {url}. Error: {str(e)}"

    async def _arun(self, url: str) -> str:
        """Asynchronous execution. Uses requests fallback for cloud deployment."""
        import asyncio
        return await asyncio.to_thread(self._run, url)