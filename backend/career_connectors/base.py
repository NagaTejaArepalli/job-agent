from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import hashlib

class RawDiscoveredJob(BaseModel):
    ats_job_id: str
    title: str
    location: str = "Remote / Unspecified"
    department: Optional[str] = None
    employment_type: str = "Full-time"
    url: str
    description: str = ""
    salary_range: Optional[str] = None
    
    @property
    def hash_id(self) -> str:
        # Generate stable unique hash from title + company URL or ats_job_id
        content = f"{self.title.strip().lower()}|{self.url.strip().lower()}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

class BaseCareerConnector(ABC):
    def __init__(self, company_name: str, career_url: str, board_token: Optional[str] = None):
        self.company_name = company_name
        self.career_url = career_url
        self.board_token = board_token or self._extract_token(career_url)
        
    @abstractmethod
    def _extract_token(self, url: str) -> Optional[str]:
        """Extract board token or identifier from the career URL"""
        pass
        
    @abstractmethod
    async def fetch_jobs(self, keywords: Optional[str] = None, location: Optional[str] = None) -> List[RawDiscoveredJob]:
        """Fetch active job postings from the ATS or career site"""
        pass
