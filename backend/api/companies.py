from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.database.models import Company
from backend.career_connectors.registry import detect_ats_provider
from backend.agents.discovery_agent.discovery_service import DiscoveryAgent

router = APIRouter(prefix="/companies", tags=["companies"])

class CompanyCreate(BaseModel):
    name: str
    career_url: str
    ats_provider: Optional[str] = None
    board_token: Optional[str] = None
    keywords: Optional[str] = "SDET, QA, Test Automation, Software Engineer in Test"
    location_preference: Optional[str] = None

class CompanyResponse(BaseModel):
    id: int
    name: str
    career_url: str
    ats_provider: str
    board_token: Optional[str]
    active: bool
    keywords: Optional[str]
    location_preference: Optional[str]
    last_scraped_at: Optional[str]
    job_count: int = 0

@router.get("", response_model=List[CompanyResponse])
def list_companies(db: Session = Depends(get_db)):
    companies = db.query(Company).all()
    results = []
    for c in companies:
        results.append(
            CompanyResponse(
                id=c.id,
                name=c.name,
                career_url=c.career_url,
                ats_provider=c.ats_provider or "generic",
                board_token=c.board_token,
                active=c.active,
                keywords=c.keywords,
                location_preference=c.location_preference,
                last_scraped_at=c.last_scraped_at.isoformat() if c.last_scraped_at else None,
                job_count=len(c.jobs)
            )
        )
    return results

@router.post("", response_model=CompanyResponse)
def add_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    existing = db.query(Company).filter(Company.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Company already exists")
        
    ats = payload.ats_provider or detect_ats_provider(payload.career_url)
    company = Company(
        name=payload.name,
        career_url=payload.career_url,
        ats_provider=ats,
        board_token=payload.board_token,
        keywords=payload.keywords,
        location_preference=payload.location_preference,
        active=True
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return CompanyResponse(
        id=company.id,
        name=company.name,
        career_url=company.career_url,
        ats_provider=company.ats_provider,
        board_token=company.board_token,
        active=company.active,
        keywords=company.keywords,
        location_preference=company.location_preference,
        last_scraped_at=None,
        job_count=0
    )

@router.post("/{company_id}/discover")
async def trigger_company_discovery(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    agent = DiscoveryAgent(db)
    res = await agent.discover_company_jobs(company)
    return res

@router.delete("/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    db.delete(company)
    db.commit()
    return {"status": "success", "message": f"Company {company.name} deleted"}
