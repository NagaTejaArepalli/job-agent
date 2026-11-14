import re
import html
from typing import List, Optional
import httpx
from backend.career_connectors.base import BaseCareerConnector, RawDiscoveredJob

class SmartRecruitersConnector(BaseCareerConnector):
    """
    Connector for SmartRecruiters job boards.
    Uses public API: https://api.smartrecruiters.com/v1/companies/{company}/postings
    """
    
    def _extract_token(self, url: str) -> Optional[str]:
        # Extract from URL e.g. careers.smartrecruiters.com/Spotify or smartrecruiters.com/company
        match = re.search(r"smartrecruiters\.com/([^/?#]+)", url)
        if match:
            return match.group(1).lower()
        return re.sub(r"[^a-zA-Z0-9_-]", "", self.company_name).lower()
        
    async def fetch_jobs(self, keywords: Optional[str] = None, location: Optional[str] = None) -> List[RawDiscoveredJob]:
        if not self.board_token:
            return []
            
        endpoint = f"https://api.smartrecruiters.com/v1/companies/{self.board_token}/postings?limit=100"
        jobs: List[RawDiscoveredJob] = []
        
        async with httpx.AsyncClient(timeout=8.0) as client:
            try:
                response = await client.get(endpoint)
                if response.status_code != 200:
                    return []
                data = response.json()
            except Exception as e:
                print(f"[SmartRecruitersConnector] Error fetching for {self.company_name}: {e}")
                return []
                
        raw_jobs = data.get("content", [])
        kw_list = [k.strip().lower() for k in keywords.split(",")] if keywords else []
        
        for item in raw_jobs:
            title = item.get("name", "").strip()
            loc_data = item.get("location", {})
            city = loc_data.get("city", "")
            country = loc_data.get("country", "")
            job_loc = f"{city}, {country}".strip(", ") or "Remote / Unspecified"
            
            job_id = item.get("id")
            dept = item.get("department", {}).get("label")
            emp_type = item.get("typeOfEmployment", {}).get("label", "Full-time")
            job_url = f"https://jobs.smartrecruiters.com/{self.board_token}/{job_id}"
            
            clean_desc = f"{title} at {self.company_name}. Department: {dept or 'Engineering'}. Location: {job_loc}."
            
            full_text = f"{title} {dept or ''}".lower()
            if kw_list and not any(kw in full_text for kw in kw_list):
                continue
                
            if location and location.lower() not in job_loc.lower():
                continue
                
            jobs.append(
                RawDiscoveredJob(
                    ats_job_id=str(job_id),
                    title=title,
                    location=job_loc,
                    department=dept,
                    employment_type=emp_type,
                    url=job_url,
                    description=clean_desc,
                    salary_range=None
                )
            )
            
        return jobs
