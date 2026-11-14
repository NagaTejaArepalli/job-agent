from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.database.models import Job, JobMatch, Company
from backend.agents.discovery_agent.discovery_service import DiscoveryAgent
from backend.agents.matching_agent.matching_service import MatchingAgent

router = APIRouter(prefix="/jobs", tags=["jobs"])

class JobDetailResponse(BaseModel):
    id: int
    company_name: str
    ats_provider: str
    title: str
    location: str
    department: Optional[str]
    employment_type: str
    url: str
    description: Optional[str]
    salary_range: Optional[str]
    status: str
    first_seen: str
    match_score: Optional[float] = None
    technical_score: Optional[float] = None
    experience_score: Optional[float] = None
    reasoning: Optional[str] = None
    key_matches: List[str] = []
    missing_skills: List[str] = []
    application_status: Optional[str] = None

@router.get("", response_model=List[JobDetailResponse])
def list_jobs(
    query: Optional[str] = Query(None),
    min_score: Optional[float] = Query(0.0),
    company_id: Optional[int] = Query(None),
    status: Optional[str] = Query("active"),
    limit: int = Query(100),
    db: Session = Depends(get_db)
):
    q = db.query(Job)
    if status and status != "all":
        q = q.filter(Job.status == status)
    if company_id:
        q = q.filter(Job.company_id == company_id)
    if query:
        term = f"%{query}%"
        q = q.filter(Job.title.ilike(term) | Job.description.ilike(term))
        
    jobs = q.order_by(Job.first_seen.desc()).limit(limit).all()
    results = []
    
    for j in jobs:
        m = j.match
        score = m.match_score if m else 0.0
        if score < (min_score or 0.0):
            continue
            
        app_status = j.application.status if j.application else None
        
        results.append(
            JobDetailResponse(
                id=j.id,
                company_name=j.company.name if j.company else "Unknown",
                ats_provider=j.company.ats_provider if j.company else "generic",
                title=j.title,
                location=j.location or "Remote / Unspecified",
                department=j.department,
                employment_type=j.employment_type or "Full-time",
                url=j.url,
                description=j.description,
                salary_range=j.salary_range,
                status=j.status,
                first_seen=j.first_seen.isoformat() if j.first_seen else "",
                match_score=m.match_score if m else None,
                technical_score=m.technical_score if m else None,
                experience_score=m.experience_score if m else None,
                reasoning=m.reasoning if m else None,
                key_matches=m.key_matches or [] if m else [],
                missing_skills=m.missing_skills or [] if m else [],
                application_status=app_status
            )
        )
        
    # Sort by match score descending if scored
    results.sort(key=lambda x: (x.match_score or 0.0), reverse=True)
    return results

@router.get("/{job_id}", response_model=JobDetailResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    j = db.query(Job).filter(Job.id == job_id).first()
    if not j:
        raise HTTPException(status_code=404, detail="Job not found")
        
    m = j.match
    app_status = j.application.status if j.application else None
    
    return JobDetailResponse(
        id=j.id,
        company_name=j.company.name if j.company else "Unknown",
        ats_provider=j.company.ats_provider if j.company else "generic",
        title=j.title,
        location=j.location or "Remote / Unspecified",
        department=j.department,
        employment_type=j.employment_type or "Full-time",
        url=j.url,
        description=j.description,
        salary_range=j.salary_range,
        status=j.status,
        first_seen=j.first_seen.isoformat() if j.first_seen else "",
        match_score=m.match_score if m else None,
        technical_score=m.technical_score if m else None,
        experience_score=m.experience_score if m else None,
        reasoning=m.reasoning if m else None,
        key_matches=m.key_matches or [] if m else [],
        missing_skills=m.missing_skills or [] if m else [],
        application_status=app_status
    )

@router.post("/discover-all")
async def trigger_discovery_all(db: Session = Depends(get_db)):
    agent = DiscoveryAgent(db)
    res = await agent.run_discovery_all()
    # Auto-run matching on new jobs
    matcher = MatchingAgent(db)
    match_res = matcher.match_all_unmatched_jobs()
    return {"discovery": res, "matching": match_res}

@router.post("/match-all")
def trigger_matching_all(db: Session = Depends(get_db)):
    matcher = MatchingAgent(db)
    return matcher.match_all_unmatched_jobs()
