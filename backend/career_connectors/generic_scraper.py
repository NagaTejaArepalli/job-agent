import re
import html
import json
from typing import List, Optional
import httpx
from backend.career_connectors.base import BaseCareerConnector, RawDiscoveredJob

class GenericCareerScraper(BaseCareerConnector):
    """
    Generic scraper for company career sites that don't use standardized ATS APIs.
    Extracts jobs via Schema.org JobPosting JSON-LD or semantic HTML patterns.
    """
    
    def _extract_token(self, url: str) -> Optional[str]:
        return None
        
    async def fetch_jobs(self, keywords: Optional[str] = None, location: Optional[str] = None) -> List[RawDiscoveredJob]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        jobs: List[RawDiscoveredJob] = []
        
        async with httpx.AsyncClient(timeout=25.0, headers=headers, follow_redirects=True) as client:
            try:
                response = await client.get(self.career_url)
                if response.status_code != 200:
                    return []
                html_text = response.text
            except Exception as e:
                print(f"[GenericCareerScraper] Fetch error for {self.company_name} ({self.career_url}): {e}")
                return []
                
        # 1. Try to find Schema.org JobPosting JSON-LD
        json_ld_matches = re.findall(r'<script[^>]*type=[\'"]application/ld\+json[\'"][^>]*>(.*?)</script>', html_text, re.DOTALL | re.IGNORECASE)
        for match in json_ld_matches:
            try:
                data = json.loads(match.strip())
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if item.get("@type") == "JobPosting":
                        title = item.get("title", "").strip()
                        job_url = item.get("url") or self.career_url
                        desc = item.get("description", "")
                        clean_desc = re.sub(r"<[^>]+>", " ", desc)
                        clean_desc = html.unescape(clean_desc).strip()
                        
                        job_loc = "Remote / Unspecified"
                        if "jobLocation" in item:
                            loc_val = item["jobLocation"]
                            if isinstance(loc_val, dict):
                                address = loc_val.get("address", {})
                                if isinstance(address, dict):
                                    job_loc = address.get("addressLocality") or address.get("addressRegion") or "Remote / Unspecified"
                                    
                        jobs.append(
                            RawDiscoveredJob(
                                ats_job_id=str(hash(job_url)),
                                title=title,
                                location=job_loc,
                                department=item.get("occupationalCategory"),
                                employment_type=item.get("employmentType", "Full-time"),
                                url=job_url,
                                description=clean_desc[:8000],
                                salary_range=None
                            )
                        )
            except Exception:
                continue
                
        # 2. If no JSON-LD, try link heuristic extraction for career links
        if not jobs:
            # Look for <a> tags with job/career hrefs
            link_pattern = re.compile(r'<a[^>]+href=[\'"]([^\'"]*(?:job|career|position|opening|apply)[^\'"]*)[\'"][^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)
            found_urls = set()
            for m in link_pattern.finditer(html_text):
                href, link_text = m.groups()
                clean_text = re.sub(r"<[^>]+>", " ", link_text).strip()
                if 5 < len(clean_text) < 120 and not any(skip in clean_text.lower() for skip in ["cookie", "privacy", "contact", "about", "search"]):
                    full_url = href if href.startswith("http") else httpx.URL(self.career_url).join(href)
                    str_url = str(full_url)
                    if str_url not in found_urls:
                        found_urls.add(str_url)
                        jobs.append(
                            RawDiscoveredJob(
                                ats_job_id=str(hash(str_url)),
                                title=clean_text,
                                location="Remote / Unspecified",
                                department=None,
                                employment_type="Full-time",
                                url=str_url,
                                description=f"Position at {self.company_name}: {clean_text}",
                                salary_range=None
                            )
                        )
                        
        # Filter keywords
        if keywords:
            kw_list = [k.strip().lower() for k in keywords.split(",")]
            jobs = [j for j in jobs if any(kw in f"{j.title} {j.description}".lower() for kw in kw_list)]
            
        return jobs
