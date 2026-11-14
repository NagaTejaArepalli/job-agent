import re
import html
from typing import List, Optional
import httpx
from backend.career_connectors.base import BaseCareerConnector, RawDiscoveredJob

class GreenhouseConnector(BaseCareerConnector):
    """
    Connector for Greenhouse ATS job boards.
    Uses official public API: https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true
    """
    
    def _extract_token(self, url: str) -> Optional[str]:
        # Extract from URL e.g. boards.greenhouse.io/stripe or greenhouse.io/airbnb
        match = re.search(r"greenhouse\.io/(?:embed/job_board\?for=)?([^/?#]+)", url)
        if match:
            return match.group(1).lower()
        # Fallback to company name
        return re.sub(r"[^a-zA-Z0-9_-]", "", self.company_name).lower()
        
    async def fetch_jobs(self, keywords: Optional[str] = None, location: Optional[str] = None) -> List[RawDiscoveredJob]:
        if not self.board_token:
            return []
            
        endpoint = f"https://boards-api.greenhouse.io/v1/boards/{self.board_token}/jobs?content=true"
        jobs: List[RawDiscoveredJob] = []
        
        async with httpx.AsyncClient(timeout=8.0) as client:
            try:
                response = await client.get(endpoint)
                if response.status_code != 200:
                    return []
                data = response.json()
            except Exception as e:
                print(f"[GreenhouseConnector] Error fetching for {self.company_name}: {e}")
                return []
                
        raw_jobs = data.get("jobs", [])
        kw_list = [k.strip().lower() for k in keywords.split(",")] if keywords else []
        
        for item in raw_jobs:
            title = item.get("title", "").strip()
            job_loc = item.get("location", {}).get("name", "Remote / Unspecified")
            job_url = item.get("absolute_url") or f"https://boards.greenhouse.io/{self.board_token}/jobs/{item.get('id')}"
            raw_content = item.get("content", "")
            # Clean HTML tags
            clean_desc = re.sub(r"<[^>]+>", " ", raw_content)
            clean_desc = html.unescape(clean_desc)
            clean_desc = re.sub(r"\s+", " ", clean_desc).strip()
            
            # Departments
            departments = [d.get("name") for d in item.get("departments", []) if d.get("name")]
            dept_str = ", ".join(departments) if departments else None
            
            # Keyword filter if specified
            full_text = f"{title} {dept_str or ''} {clean_desc}".lower()
            if kw_list and not any(kw in full_text for kw in kw_list):
                continue
                
            if location and location.lower() not in job_loc.lower():
                continue
                
            jobs.append(
                RawDiscoveredJob(
                    ats_job_id=str(item.get("id")),
                    title=title,
                    location=job_loc,
                    department=dept_str,
                    employment_type="Full-time",
                    url=job_url,
                    description=clean_desc[:8000], # store up to 8k chars of JD
                    salary_range=None
                )
            )
            
        return jobs
