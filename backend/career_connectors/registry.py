from typing import Optional
from backend.career_connectors.base import BaseCareerConnector
from backend.career_connectors.greenhouse import GreenhouseConnector
from backend.career_connectors.lever import LeverConnector
from backend.career_connectors.ashby import AshbyConnector
from backend.career_connectors.smartrecruiters import SmartRecruitersConnector
from backend.career_connectors.generic_scraper import GenericCareerScraper

def detect_ats_provider(url: str) -> str:
    url_lower = url.lower()
    if "greenhouse.io" in url_lower:
        return "greenhouse"
    elif "lever.co" in url_lower:
        return "lever"
    elif "ashbyhq.com" in url_lower:
        return "ashby"
    elif "smartrecruiters.com" in url_lower:
        return "smartrecruiters"
    elif "workday" in url_lower or "myworkdayjobs.com" in url_lower:
        return "workday"
    return "generic"

def get_connector(company_name: str, career_url: str, ats_provider: Optional[str] = None, board_token: Optional[str] = None) -> BaseCareerConnector:
    provider = (ats_provider or "").lower().strip()
    if not provider or provider == "generic":
        provider = detect_ats_provider(career_url)
        
    if provider == "greenhouse":
        return GreenhouseConnector(company_name, career_url, board_token)
    elif provider == "lever":
        return LeverConnector(company_name, career_url, board_token)
    elif provider == "ashby":
        return AshbyConnector(company_name, career_url, board_token)
    elif provider == "smartrecruiters":
        return SmartRecruitersConnector(company_name, career_url, board_token)
    else:
        return GenericCareerScraper(company_name, career_url, board_token)
