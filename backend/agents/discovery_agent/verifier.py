import httpx
from datetime import datetime
from typing import Tuple

class JobVerifier:
    """
    Verifies that a job's link is still active and reachable,
    detecting 404s, redirects to expired landing pages, or deactivated postings.
    """
    
    @staticmethod
    async def verify_job_url(url: str) -> Tuple[bool, str]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
        }
        try:
            async with httpx.AsyncClient(timeout=15.0, headers=headers, follow_redirects=True) as client:
                response = await client.get(url)
                if response.status_code == 404:
                    return False, "404 Not Found"
                if response.status_code >= 400:
                    return False, f"HTTP {response.status_code}"
                    
                body = response.text.lower()
                # Check typical expiration text patterns
                expired_indicators = [
                    "this job has expired",
                    "this position has been closed",
                    "job posting is no longer available",
                    "this job is no longer accepting applications",
                    "the role you are looking for is closed",
                    "no longer open"
                ]
                for ind in expired_indicators:
                    if ind in body:
                        return False, f"Expired message detected: '{ind}'"
                        
                return True, "Active"
        except Exception as e:
            return True, f"Check skipped ({str(e)[:50]})" # Don't mark expired on network transient error
