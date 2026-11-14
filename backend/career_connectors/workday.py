import re
from typing import List, Optional
import httpx
from backend.career_connectors.base import BaseCareerConnector, RawDiscoveredJob

class WorkdayConnector(BaseCareerConnector):
    """
    Direct connector for Workday Career Portals (e.g. Walmart, Target, NVIDIA, Adobe, Salesforce, PayPal, etc.).
    Extracts jobs using Workday's public CXS API:
    POST https://<tenant>.wd<N>.myworkdayjobs.com/wday/cxs/<tenant>/<site_name>/jobs
    """
    
    def _extract_token(self, url: str) -> Optional[str]:
        # Extract tenant and site from URL: https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite
        match = re.search(r"https?://([^.]+)\.(wd\d+)\.myworkdayjobs\.com/(?:en-[A-Za-z]+/)?([^/?#]+)", url)
        if match:
            tenant, wd_num, site_name = match.groups()
            return f"{tenant}|{wd_num}|{site_name}"
        return None
        
    async def fetch_jobs(self, keywords: Optional[str] = None, location: Optional[str] = None) -> List[RawDiscoveredJob]:
        if not self.board_token:
            return []
            
        try:
            tenant, wd_num, site_name = self.board_token.split("|")
        except ValueError:
            return []
            
        endpoint = f"https://{tenant}.{wd_num}.myworkdayjobs.com/wday/cxs/{tenant}/{site_name}/jobs"
        search_query = keywords.split(",")[0].strip() if keywords else "SDET"
        
        payload = {
            "appliedFacets": {},
            "limit": 25,
            "offset": 0,
            "searchText": search_query
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        
        jobs: List[RawDiscoveredJob] = []
        
        async with httpx.AsyncClient(timeout=25.0, headers=headers) as client:
            try:
                response = await client.post(endpoint, json=payload)
                if response.status_code != 200:
                    # Retry with generic search if specific keyword returned empty or 400
                    payload["searchText"] = "Quality"
                    response = await client.post(endpoint, json=payload)
                    if response.status_code != 200:
                        return []
                        
                data = response.json()
            except Exception as e:
                print(f"[WorkdayConnector] Error querying {self.company_name} ({endpoint}): {e}")
                return []
                
        postings = data.get("jobPostings", [])
        for item in postings:
            title = item.get("title", "").strip()
            loc_text = item.get("locationsText", "Remote / Unspecified")
            ext_path = item.get("externalPath", "")
            job_url = f"https://{tenant}.{wd_num}.myworkdayjobs.com/{site_name}{ext_path}" if ext_path else self.career_url
            job_id = ext_path.split("/")[-1] if ext_path else str(hash(title))
            
            bullet_fields = item.get("bulletFields", [])
            desc = f"{title} at {self.company_name}. Location: {loc_text}. {', '.join(bullet_fields)}"
            
            jobs.append(
                RawDiscoveredJob(
                    ats_job_id=job_id,
                    title=title,
                    location=loc_text,
                    department=None,
                    employment_type="Full-time",
                    url=job_url,
                    description=desc,
                    salary_range=None
                )
            )
            
        return jobs
