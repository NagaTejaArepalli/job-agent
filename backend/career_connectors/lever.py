import re
import html
from typing import List, Optional
import httpx
from backend.career_connectors.base import BaseCareerConnector, RawDiscoveredJob

class LeverConnector(BaseCareerConnector):
    """
    Connector for Lever ATS job boards.
    Uses official public API: https://api.lever.co/v0/postings/{company}?mode=json
    """
    
    def _extract_token(self, url: str) -> Optional[str]:
        # Extract from URL e.g. jobs.lever.co/netflix
        match = re.search(r"lever\.co/([^/?#]+)", url)
        if match:
            return match.group(1).lower()
        return re.sub(r"[^a-zA-Z0-9_-]", "", self.company_name).lower()
        
    async def fetch_jobs(self, keywords: Optional[str] = None, location: Optional[str] = None) -> List[RawDiscoveredJob]:
        if not self.board_token:
            return []
            
        endpoint = f"https://api.lever.co/v0/postings/{self.board_token}?mode=json"
        jobs: List[RawDiscoveredJob] = []
        
        async with httpx.AsyncClient(timeout=8.0) as client:
            try:
                response = await client.get(endpoint)
                if response.status_code != 200:
                    return []
                data = response.json()
            except Exception as e:
                print(f"[LeverConnector] Error fetching for {self.company_name}: {e}")
                return []
                
        if not isinstance(data, list):
            return []
            
        kw_list = [k.strip().lower() for k in keywords.split(",")] if keywords else []
        
        for item in data:
            title = item.get("text", "").strip()
            categories = item.get("categories", {})
            job_loc = categories.get("location", "Remote / Unspecified")
            dept = categories.get("department") or categories.get("team")
            emp_type = categories.get("commitment", "Full-time")
            job_url = item.get("hostedUrl", "")
            
            raw_desc = item.get("descriptionPlain", "") or ""
            lists = item.get("lists", [])
            for list_item in lists:
                list_title = list_item.get("text", "")
                list_content = list_item.get("content", "")
                raw_desc += f"\n{list_title}:\n{list_content}"
                
            clean_desc = re.sub(r"<[^>]+>", " ", raw_desc)
            clean_desc = html.unescape(clean_desc)
            clean_desc = re.sub(r"\s+", " ", clean_desc).strip()
            
            salary = item.get("salaryRange", {})
            salary_str = None
            if salary and isinstance(salary, dict):
                min_s = salary.get("min")
                max_s = salary.get("max")
                curr = salary.get("currency", "$")
                if min_s and max_s:
                    salary_str = f"{curr}{min_s:,.0f} - {curr}{max_s:,.0f}"
                    
            full_text = f"{title} {dept or ''} {clean_desc}".lower()
            if kw_list and not any(kw in full_text for kw in kw_list):
                continue
                
            if location and location.lower() not in job_loc.lower():
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
                    salary_range=salary_str
                )
            )
            
        return jobs
