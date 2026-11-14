import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.database.models import Company, Job
from backend.career_connectors.registry import get_connector
from backend.agents.discovery_agent.verifier import JobVerifier

class DiscoveryAgent:
    """
    Agent 1: Job Discovery
    Extracts jobs from official company career sites and ATS integrations,
    verifies active links, detects duplicates, and syncs into database.
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    async def _fetch_single_company(self, comp_info: tuple, semaphore: asyncio.Semaphore):
        """Fetch raw jobs for one company with rate-limiting and error isolation."""
        comp_id, comp_name, career_url, ats_provider, board_token, keywords, location_pref = comp_info
        
        # STRICT EXCLUSION: Infor and Accenture are permanently blocked
        EXCLUDED_EMPLOYERS = ["infor", "accenture"]
        if any(exc in (comp_name or "").lower() for exc in EXCLUDED_EMPLOYERS):
            return comp_id, comp_name, [], "excluded_current_past_employer"
            
        async with semaphore:
            try:
                connector = get_connector(
                    company_name=comp_name,
                    career_url=career_url,
                    ats_provider=ats_provider,
                    board_token=board_token
                )
                raw_jobs = await asyncio.wait_for(
                    connector.fetch_jobs(
                        keywords=keywords,
                        location=location_pref
                    ),
                    timeout=10.0
                )
                return comp_id, comp_name, raw_jobs, "success"
            except Exception as e:
                return comp_id, comp_name, [], f"error: {str(e)[:60]}"

    async def discover_company_jobs(self, company: Company) -> Dict[str, Any]:
        """Discovers jobs for a single company."""
        from backend.utils.location_filter import is_india_location
        
        comp_info = (
            company.id, company.name, company.career_url, 
            company.ats_provider, company.board_token, 
            company.keywords, company.location_preference
        )
        semaphore = asyncio.Semaphore(1)
        _, _, raw_jobs, status = await self._fetch_single_company(comp_info, semaphore)
        
        discovered_count = len(raw_jobs)
        new_jobs = 0
        updated_jobs = 0
        
        for raw in raw_jobs:
            is_india, normalized_loc = is_india_location(raw.location)
            if not is_india:
                continue
                
            raw.location = normalized_loc
            existing_job = self.db.query(Job).filter(
                (Job.hash_id == raw.hash_id) | 
                ((Job.company_id == company.id) & (Job.ats_job_id == raw.ats_job_id) & (Job.ats_job_id.isnot(None)))
            ).first()
            
            if existing_job:
                existing_job.last_verified = datetime.utcnow()
                existing_job.status = "active"
                if raw.description and len(raw.description) > len(existing_job.description or ""):
                    existing_job.description = raw.description
                updated_jobs += 1
            else:
                new_job = Job(
                    company_id=company.id,
                    ats_job_id=raw.ats_job_id,
                    title=raw.title,
                    location=raw.location,
                    department=raw.department,
                    employment_type=raw.employment_type,
                    url=raw.url,
                    description=raw.description,
                    salary_range=raw.salary_range,
                    hash_id=raw.hash_id,
                    status="active",
                    first_seen=datetime.utcnow(),
                    last_verified=datetime.utcnow()
                )
                self.db.add(new_job)
                new_jobs += 1
                
        company.last_scraped_at = datetime.utcnow()
        self.db.commit()
        
        return {
            "company_name": company.name,
            "total_found": discovered_count,
            "new_added": new_jobs,
            "updated": updated_jobs,
            "status": status
        }
        
    async def run_discovery_all(self, concurrency: int = 15) -> Dict[str, Any]:
        """
        Scans all target companies in parallel batches with rate limiting and database isolation.
        Guarantees that every single company is checked without blocking or locking.
        """
        from backend.utils.location_filter import is_india_location

        companies = self.db.query(Company).filter(Company.active == True).all()
        comp_infos = [
            (c.id, c.name, c.career_url, c.ats_provider, c.board_token, c.keywords, c.location_preference)
            for c in companies
        ]
        
        semaphore = asyncio.Semaphore(concurrency)
        tasks = [self._fetch_single_company(info, semaphore) for info in comp_infos]
        fetched_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_new = 0
        total_found = 0
        details = []
        
        # Database synchronization in single thread
        for item in fetched_results:
            if not isinstance(item, tuple):
                continue
            comp_id, comp_name, raw_jobs, status = item
            discovered_count = len(raw_jobs)
            total_found += discovered_count
            new_jobs = 0
            updated_jobs = 0
            
            for raw in raw_jobs:
                is_india, normalized_loc = is_india_location(raw.location)
                if not is_india:
                    continue
                    
                raw.location = normalized_loc
                existing_job = self.db.query(Job).filter(
                    (Job.hash_id == raw.hash_id) | 
                    ((Job.company_id == comp_id) & (Job.ats_job_id == raw.ats_job_id) & (Job.ats_job_id.isnot(None)))
                ).first()
                
                if existing_job:
                    existing_job.last_verified = datetime.utcnow()
                    existing_job.status = "active"
                    if raw.description and len(raw.description) > len(existing_job.description or ""):
                        existing_job.description = raw.description
                    updated_jobs += 1
                else:
                    new_job = Job(
                        company_id=comp_id,
                        ats_job_id=raw.ats_job_id,
                        title=raw.title,
                        location=raw.location,
                        department=raw.department,
                        employment_type=raw.employment_type,
                        url=raw.url,
                        description=raw.description,
                        salary_range=raw.salary_range,
                        hash_id=raw.hash_id,
                        status="active",
                        first_seen=datetime.utcnow(),
                        last_verified=datetime.utcnow()
                    )
                    self.db.add(new_job)
                    new_jobs += 1
                    
            comp_obj = self.db.query(Company).get(comp_id)
            if comp_obj:
                comp_obj.last_scraped_at = datetime.utcnow()
                
            total_new += new_jobs
            details.append({
                "company_name": comp_name,
                "total_found": discovered_count,
                "new_added": new_jobs,
                "updated": updated_jobs,
                "status": status
            })
            
        self.db.commit()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "companies_scanned": len(companies),
            "total_jobs_found": total_found,
            "new_jobs_added": total_new,
            "details": details
        }
        
    async def verify_active_jobs(self, limit: int = 50) -> Dict[str, Any]:
        """Verify active jobs in parallel to check if any have been closed or taken down."""
        jobs = self.db.query(Job).filter(Job.status == "active").order_by(Job.last_verified.asc()).limit(limit).all()
        if not jobs:
            return {"checked": 0, "deactivated": 0}

        sem = asyncio.Semaphore(10)
        async def verify_single(job_id, url):
            async with sem:
                try:
                    return job_id, await asyncio.wait_for(JobVerifier.verify_job_url(url), timeout=6.0)
                except Exception:
                    return job_id, (True, "Timeout/Skipped")

        results = await asyncio.gather(*(verify_single(j.id, j.url) for j in jobs), return_exceptions=True)
        job_map = {j.id: j for j in jobs}
        checked = 0
        deactivated = 0
        for res in results:
            if not isinstance(res, tuple):
                continue
            job_id, (is_active, reason) = res
            j = job_map.get(job_id)
            if j:
                j.last_verified = datetime.utcnow()
                if not is_active:
                    j.status = "expired"
                    deactivated += 1
                checked += 1

        self.db.commit()
        return {
            "checked": checked,
            "deactivated": deactivated
        }
