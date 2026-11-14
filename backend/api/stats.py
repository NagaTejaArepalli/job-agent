from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.database.models import Company, Job, JobMatch, Application, QAKnowledgeItem, MasterResume

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_companies = db.query(Company).filter(Company.active == True).count()
    total_jobs = db.query(Job).filter(Job.status == "active").count()
    
    # Jobs discovered in last 24h
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    new_jobs_today = db.query(Job).filter(Job.first_seen >= one_day_ago).count()
    
    # High matches (score >= 80)
    high_matches = db.query(JobMatch).filter(JobMatch.match_score >= 80.0).count()
    good_matches = db.query(JobMatch).filter(JobMatch.match_score >= 65.0, JobMatch.match_score < 80.0).count()
    
    # Applications
    prepared_apps = db.query(Application).filter(Application.status.in_(["prepared", "ready_for_review"])).count()
    submitted_apps = db.query(Application).filter(Application.status == "submitted").count()
    interview_apps = db.query(Application).filter(Application.status == "interview").count()
    
    # KB & Resume stats
    qa_count = db.query(QAKnowledgeItem).count()
    master_resume = db.query(MasterResume).filter(MasterResume.is_active == True).first()
    has_master_resume = master_resume is not None
    
    return {
        "total_companies": total_companies,
        "total_active_jobs": total_jobs,
        "new_jobs_today": new_jobs_today,
        "high_matches": high_matches,
        "good_matches": good_matches,
        "prepared_applications": prepared_apps,
        "submitted_applications": submitted_apps,
        "interview_applications": interview_apps,
        "qa_knowledge_items": qa_count,
        "has_master_resume": has_master_resume,
        "candidate_name": master_resume.parsed_data.get("name", "Candidate") if master_resume else "Candidate"
    }
