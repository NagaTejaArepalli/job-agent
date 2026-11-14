from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.database.models import Company, Job
from backend.career_connectors.registry import get_connector
from backend.agents.discovery_agent.verifier import JobVerifier

class DiscoveryAgent:
    """
    Agent 1: Job Discovery
    Extracts jobs from company career sites and ATS integrations,
    verifies active links, detects duplicates, and syncs into database.
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    async def discover_company_jobs(self, company: Company) -> Dict[str, Any]:
        connector = get_connector(
            company_name=company.name,
            career_url=company.career_url,
            ats_provider=company.ats_provider,
            board_token=company.board_token
        )
        
        raw_jobs = await connector.fetch_jobs(
            keywords=company.keywords,
            location=company.location_preference
        )
        
        discovered_count = len(raw_jobs)
        new_jobs = 0
        updated_jobs = 0
        
        from backend.utils.location_filter import is_india_location
        
        for raw in raw_jobs:
            is_india, normalized_loc = is_india_location(raw.location)
            # STRICT FILTER: User requires India opportunities only
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
            "updated": updated_jobs
        }
        
    async def run_discovery_all(self) -> Dict[str, Any]:
        companies = self.db.query(Company).filter(Company.active == True).all()
        results = []
        total_new = 0
        total_found = 0
        
        for comp in companies:
            res = await self.discover_company_jobs(comp)
            results.append(res)
            total_new += res["new_added"]
            total_found += res["total_found"]
            
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "companies_scanned": len(companies),
            "total_jobs_found": total_found,
            "new_jobs_added": total_new,
            "details": results
        }
        
    async def verify_active_jobs(self, limit: int = 50) -> Dict[str, Any]:
        """Verify active jobs to check if any have been closed or taken down."""
        jobs = self.db.query(Job).filter(Job.status == "active").order_by(Job.last_verified.asc()).limit(limit).all()
        checked = 0
        deactivated = 0
        
        for job in jobs:
            is_active, reason = await JobVerifier.verify_job_url(job.url)
            job.last_verified = datetime.utcnow()
            if not is_active:
                job.status = "expired"
                deactivated += 1
            checked += 1
            
        self.db.commit()
        return {
            "checked": checked,
            "deactivated": deactivated
        }
