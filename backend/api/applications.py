from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from backend.database.session import get_db
from backend.database.models import Application, Job, TailoredResume
from backend.agents.application_agent.application_service import ApplicationAgent
from backend.browser_automation.form_filler import BrowserFormFiller
from config.settings import settings

router = APIRouter(prefix="/applications", tags=["applications"])

class ChecklistUpdate(BaseModel):
    task_id: str
    completed: bool

class StatusUpdate(BaseModel):
    status: str # prepared, ready_for_review, submitted, interview, offer, rejected
    notes: Optional[str] = None

class FormFillRequest(BaseModel):
    headed: Optional[bool] = False

@router.get("")
def list_applications(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Application)
    if status and status != "all":
        q = q.filter(Application.status == status)
    apps = q.order_by(Application.updated_at.desc()).all()
    
    results = []
    for a in apps:
        j = a.job
        results.append({
            "id": a.id,
            "job_id": a.job_id,
            "company_name": j.company.name if j and j.company else "Unknown",
            "job_title": j.title if j else "Unknown",
            "job_url": j.url if j else "",
            "status": a.status,
            "match_score": j.match.match_score if j and j.match else 0.0,
            "missing_answers_count": len(a.missing_answers or []),
            "checklist_items": a.submission_checklist or [],
            "created_at": a.created_at.isoformat(),
            "updated_at": a.updated_at.isoformat()
        })
    return results

@router.get("/{job_id}")
def get_application(job_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.job_id == job_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application packet not yet prepared for this job")
        
    j = app.job
    return {
        "id": app.id,
        "job_id": app.job_id,
        "company_name": j.company.name if j and j.company else "Unknown",
        "job_title": j.title if j else "Unknown",
        "job_url": j.url if j else "",
        "status": app.status,
        "prepared_answers": app.prepared_answers or {},
        "missing_answers": app.missing_answers or [],
        "submission_checklist": app.submission_checklist or [],
        "notes": app.notes,
        "submission_url": app.submission_url,
        "applied_at": app.applied_at.isoformat() if app.applied_at else None,
        "tailored_resume_id": app.tailored_resume_id
    }

@router.post("/prepare/{job_id}")
def prepare_application(job_id: int, db: Session = Depends(get_db)):
    agent = ApplicationAgent(db)
    try:
        app = agent.prepare_application_packet(job_id)
        return {
            "status": "success",
            "application_id": app.id,
            "application_status": app.status,
            "prepared_fields_count": len(app.prepared_answers or {}),
            "missing_answers_count": len(app.missing_answers or []),
            "checklist": app.submission_checklist
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{job_id}/fill-form")
async def fill_application_form(job_id: int, payload: FormFillRequest, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.job_id == job_id).first()
    if not app:
        agent = ApplicationAgent(db)
        app = agent.prepare_application_packet(job_id)
        
    tailored = db.query(TailoredResume).filter(TailoredResume.id == app.tailored_resume_id).first()
    resume_path = tailored.file_path if tailored else None
    
    result = await BrowserFormFiller.fill_application(
        application_url=app.submission_url or app.job.url,
        form_data=app.prepared_answers or {},
        resume_file_path=resume_path,
        headed=payload.headed or settings.HEADLESS_BROWSER is False
    )
    
    return result

@router.put("/{job_id}/checklist")
def update_checklist_item(job_id: int, payload: ChecklistUpdate, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.job_id == job_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    checklist = app.submission_checklist or []
    for item in checklist:
        if item.get("id") == payload.task_id:
            item["completed"] = payload.completed
            
    app.submission_checklist = checklist
    
    # If all items are completed, status can be ready_for_review
    all_done = all(i.get("completed", False) for i in checklist)
    if all_done and app.status == "prepared":
        app.status = "ready_for_review"
        
    db.commit()
    return {"status": "success", "checklist": app.submission_checklist}

@router.put("/{job_id}/status")
def update_application_status(job_id: int, payload: StatusUpdate, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.job_id == job_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    app.status = payload.status
    if payload.notes:
        app.notes = payload.notes
    if payload.status == "submitted" and not app.applied_at:
        app.applied_at = datetime.utcnow()
        
    db.commit()
    return {"status": "success", "current_status": app.status}
