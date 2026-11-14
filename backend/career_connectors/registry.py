from typing import Optional
from backend.career_connectors.base import BaseCareerConnector
from backend.career_connectors.greenhouse import GreenhouseConnector
from backend.career_connectors.lever import LeverConnector
from backend.career_connectors.ashby import AshbyConnector
from backend.career_connectors.smartrecruiters import SmartRecruitersConnector
from backend.career_connectors.workday import WorkdayConnector
from backend.career_connectors.generic_scraper import GenericCareerScraper

KNOWN_ATS_MAPPINGS = {
    "datadog": ("greenhouse", "datadog"),
    "pure storage": ("greenhouse", "purestorage"),
    "zscaler": ("greenhouse", "zscaler"),
    "okta": ("greenhouse", "okta"),
    "agoda": ("greenhouse", "agoda"),
    "toast": ("greenhouse", "toast"),
    "samsara": ("greenhouse", "samsara"),
    "airbnb": ("greenhouse", "airbnb"),
    "rubrik": ("greenhouse", "rubrik"),
    "roku": ("greenhouse", "roku"),
    "highradius": ("greenhouse", "highradius"),
    "zenoti": ("greenhouse", "zenoti"),
    "commvault": ("greenhouse", "commvault"),
    "druva": ("greenhouse", "druva"),
    "slice": ("greenhouse", "slice"),
    "groww": ("greenhouse", "groww"),
    "swiggy": ("smartrecruiters", "swiggy"),
    "servicenow": ("smartrecruiters", "servicenow"),
    "arista networks": ("smartrecruiters", "aristanetworks"),
    "freshworks": ("smartrecruiters", "freshworks"),
    "unacademy": ("smartrecruiters", "unacademy"),
    "whatfix": ("smartrecruiters", "whatfix"),
    "coupa": ("lever", "coupa"),
    "linkedin": ("lever", "linkedin"),
    "cred": ("lever", "cred"),
    "meesho": ("lever", "meesho"),
}

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
    norm_name = (company_name or "").lower().strip()
    provider = (ats_provider or "").lower().strip()
    
    # Check if this company is a known ATS board
    if norm_name in KNOWN_ATS_MAPPINGS:
        mapped_prov, mapped_token = KNOWN_ATS_MAPPINGS[norm_name]
        provider = mapped_prov
        board_token = board_token or mapped_token

    if not provider or provider not in ["greenhouse", "lever", "ashby", "smartrecruiters", "workday"]:
        detected = detect_ats_provider(career_url)
        if detected != "generic":
            provider = detected
        elif provider not in ["greenhouse", "lever", "ashby", "smartrecruiters", "workday"]:
            provider = "generic"
        
    if provider == "greenhouse":
        return GreenhouseConnector(company_name, career_url, board_token)
    elif provider == "lever":
        return LeverConnector(company_name, career_url, board_token)
    elif provider == "ashby":
        return AshbyConnector(company_name, career_url, board_token)
    elif provider == "smartrecruiters":
        return SmartRecruitersConnector(company_name, career_url, board_token)
    elif provider == "workday":
        return WorkdayConnector(company_name, career_url, board_token)
    else:
        return GenericCareerScraper(company_name, career_url, board_token)
