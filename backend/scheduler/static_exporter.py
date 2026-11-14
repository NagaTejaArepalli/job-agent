from datetime import datetime
from typing import Optional
import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.database.models import Job, Company, MasterResume, QAKnowledgeItem, Application, SchedulerRun

def export_static_data(db: Session, output_dir: Optional[Path] = None):
    """
    Exports the current database state into static JSON files in frontend/public/data/
    so that Firebase Hosting (or any static CDN host) can render all discovered jobs,
    companies, match scores, resumes, and Q&A items without requiring a local backend server.
    """
    if output_dir is None:
        root_dir = Path(__file__).resolve().parent.parent.parent
        output_dir = root_dir / "frontend" / "public" / "data"
        
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Jobs & Matches
    jobs = db.query(Job).filter(Job.status == "active").all()
    jobs_data = []
    for j in jobs:
        m = j.match
        app_status = j.application.status if j.application else None
        jobs_data.append({
            "id": j.id,
            "company_name": j.company.name if j.company else "Company",
            "company": {"name": j.company.name if j.company else "Company"},
            "ats_provider": j.company.ats_provider if j.company else "portal",
            "title": j.title,
            "location": j.location or "India",
            "department": j.department,
            "employment_type": j.employment_type or "Full-time",
            "url": j.url,
            "description": j.description,
            "salary_range": j.salary_range,
            "status": j.status,
            "first_seen": j.first_seen.isoformat() if j.first_seen else "",
            "match_score": m.match_score if m else 0.0,
            "technical_score": m.technical_score if m else 0.0,
            "experience_score": m.experience_score if m else 0.0,
            "reasoning": m.reasoning if m else "",
            "match_details": {
                "key_matches": m.key_matches if m else [],
                "missing_skills": m.missing_skills if m else []
            },
            "key_matches": m.key_matches if m else [],
            "missing_skills": m.missing_skills if m else [],
            "application_status": app_status
        })
    jobs_data.sort(key=lambda x: x["match_score"], reverse=True)
    with open(output_dir / "jobs.json", "w", encoding="utf-8") as f:
        json.dump(jobs_data, f, indent=2)

    # 2. Companies
    companies = db.query(Company).filter(Company.active == True).all()
    comps_data = [
        {
            "id": c.id,
            "name": c.name,
            "career_url": c.career_url,
            "ats_provider": c.ats_provider,
            "board_token": c.board_token,
            "keywords": c.keywords,
            "location_preference": c.location_preference,
            "active": c.active,
            "last_scraped_at": c.last_scraped_at.isoformat() if c.last_scraped_at else None
        }
        for c in companies
    ]
    with open(output_dir / "companies.json", "w", encoding="utf-8") as f:
        json.dump(comps_data, f, indent=2)

    # 3. Stats
    total_comps = len(companies)
    total_jobs = len(jobs_data)
    matched_jobs = sum(1 for j in jobs_data if j["match_score"] >= 60)
    apps_count = db.query(Application).count()
    stats_data = {
        "candidate_name": "Naga Teja Arepalli",
        "total_companies": total_comps,
        "total_jobs": total_jobs,
        "matched_jobs": matched_jobs,
        "applications_in_progress": apps_count,
        "last_updated": datetime.utcnow().isoformat()
    }
    with open(output_dir / "stats.json", "w", encoding="utf-8") as f:
        json.dump(stats_data, f, indent=2)

    # 4. Q&A Knowledge Base
    qa_items = db.query(QAKnowledgeItem).all()
    qa_data = [
        {
            "id": q.id,
            "question": q.question,
            "answer": q.answer,
            "category": q.category,
            "is_sensitive": q.is_sensitive_declaration,
            "needs_confirmation": q.needs_user_confirmation
        }
        for q in qa_items
    ]
    with open(output_dir / "knowledge_base.json", "w", encoding="utf-8") as f:
        json.dump(qa_data, f, indent=2)

    # 5. Master Resume
    mr = db.query(MasterResume).filter(MasterResume.is_active == True).first()
    if mr:
        mr_data = {
            "id": mr.id,
            "filename": mr.filename,
            "uploaded_at": mr.uploaded_at.isoformat() if mr.uploaded_at else "",
            "parsed_data": mr.parsed_data or {}
        }
    else:
        mr_data = {}
    with open(output_dir / "master_resume.json", "w", encoding="utf-8") as f:
        json.dump(mr_data, f, indent=2)

    # 6. Applications
    apps = db.query(Application).all()
    apps_data = [
        {
            "id": a.id,
            "job_id": a.job_id,
            "status": a.status,
            "notes": a.notes,
            "submission_checklist": a.submission_checklist or []
        }
        for a in apps
    ]
    with open(output_dir / "applications.json", "w", encoding="utf-8") as f:
        json.dump(apps_data, f, indent=2)

    print(f"[StaticExporter] Successfully exported {total_jobs} jobs, {total_comps} companies to {output_dir}")
