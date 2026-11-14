import re
import html
from typing import List, Optional
import httpx
from backend.career_connectors.base import BaseCareerConnector, RawDiscoveredJob

class AshbyConnector(BaseCareerConnector):
    """
    Connector for Ashby job boards.
    Uses public API: https://api.ashbyhq.com/posting-api/job-board/{company}
    """
    
    def _extract_token(self, url: str) -> Optional[str]:
        # Extract from URL e.g. jobs.ashbyhq.com/openai or ashbyhq.com/linear
        match = re.search(r"ashbyhq\.com/([^/?#]+)", url)
        if match:
            return match.group(1).lower()
        return re.sub(r"[^a-zA-Z0-9_-]", "", self.company_name).lower()
        
    async def fetch_jobs(self, keywords: Optional[str] = None, location: Optional[str] = None) -> List[RawDiscoveredJob]:
        if not self.board_token:
            return []
            
        endpoint = f"https://api.ashbyhq.com/posting-api/job-board/{self.board_token}"
        jobs: List[RawDiscoveredJob] = []
        
        async with httpx.AsyncClient(timeout=8.0) as client:
            try:
                response = await client.get(endpoint)
                if response.status_code != 200:
                    return []
                data = response.json()
            except Exception as e:
                print(f"[AshbyConnector] Error fetching for {self.company_name}: {e}")
                return []
                
        raw_jobs = data.get("jobs", [])
        kw_list = [k.strip().lower() for k in keywords.split(",")] if keywords else []
        
        for item in raw_jobs:
            title = item.get("title", "").strip()
            job_loc = item.get("location", "Remote / Unspecified")
            if item.get("isRemote"):
                job_loc += " (Remote)"
            job_url = item.get("jobUrl") or f"https://jobs.ashbyhq.com/{self.board_token}/{item.get('id')}"
            dept = item.get("department")
            emp_type = item.get("employmentType", "Full-time")
            
            # Plain text description
            clean_desc = item.get("descriptionPlain", "") or ""
            if not clean_desc and item.get("descriptionHtml"):
                clean_desc = re.sub(r"<[^>]+>", " ", item.get("descriptionHtml", ""))
                clean_desc = html.unescape(clean_desc)
                clean_desc = re.sub(r"\s+", " ", clean_desc).strip()
                
            full_text = f"{title} {dept or ''} {clean_desc}".lower()
            if kw_list and not any(kw in full_text for kw in kw_list):
                continue
                
            jobs.append(
                RawDiscoveredJob(
                    ats_job_id=str(item.get("id")),
                    title=title,
                    location=job_loc,
                    department=dept,
                    employment_type=emp_type,
                    url=job_url,
                    description=clean_desc[:8000],
                    salary_range=None
                )
            )
            
        return jobs
