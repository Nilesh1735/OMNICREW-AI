import os
import json
import logging
import requests
import asyncio
from bs4 import BeautifulSoup
from crewai.tools import BaseTool
from security.validators import validate_target_url
from security.ssrf_blocker import check_ssrf_and_exposed_files

logger = logging.getLogger(__name__)

class WebScraperTool(BaseTool):
    name: str = "Web Scraper"
    description: str = "Useful for navigating to a specific URL and extracting all visible text content from the web page."

    def _run(self, url: str) -> str:
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
            
            # Fallback to Jina AI Reader if the page is JS-heavy and returned little/no text
            if len(text_content) < 200 or "Page not found" in text_content:
                logger.info(f"Standard scrape failed or returned empty. Falling back to Jina AI Reader for {url}")
                jina_url = f"https://r.jina.ai/{url}"
                jina_response = requests.get(jina_url, timeout=20, headers={"Accept": "text/plain"})
                if jina_response.status_code == 200 and len(jina_response.text) > 200:
                    text_content = jina_response.text
            
            if text_content:
                return text_content[:5000]
            return "No text content found on the page."
        except Exception as e:
            return f"Failed to scrape {url}. Error: {str(e)}"

    async def _arun(self, url: str) -> str:
        return await asyncio.to_thread(self._run, url)


class SnovEmailFinderTool(BaseTool):
    name: str = "Email Finder Tool"
    description: str = "Finds the most likely email address for a person given their first name, last name, and company domain. Use this tool ONLY after you have successfully scraped a hiring manager's name and company website."

    def _get_snov_token(self) -> str:
        client_id = os.getenv("SNOV_CLIENT_ID")
        client_secret = os.getenv("SNOV_CLIENT_SECRET")
        if not client_id or not client_secret:
            return None
        url = "https://api.snov.io/v1/oauth/access_token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
        try:
            res = requests.post(url, data=payload, timeout=10)
            if res.status_code == 200:
                return res.json().get("access_token")
            return None
        except Exception:
            return None

    def _run(self, first_name: str, last_name: str, company_domain: str) -> str:
        token = self._get_snov_token()
        if not token:
            return "Error: Could not authenticate with Snov.io. Check SNOV_CLIENT_ID and SNOV_CLIENT_SECRET env vars."
        
        url = "https://api.snov.io/v1/get-email"
        payload = {
            "access_token": token,
            "domain": company_domain,
            "firstName": first_name,
            "lastName": last_name
        }
        
        try:
            response = requests.post(url, data=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                email = data.get("data", {}).get("email")
                if email and email != "not_found":
                    return f"Success! Found email: {email}"
                else:
                    return f"Could not find an email for {first_name} {last_name} at {company_domain}."
            else:
                return f"Snov.io API Error: {response.status_code}"
        except Exception as e:
            return f"Error calling Snov.io API: {str(e)}"
            
    async def _arun(self, first_name: str, last_name: str, company_domain: str) -> str:
        return await asyncio.to_thread(self._run, first_name, last_name, company_domain)