from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.database.models import MasterResume, TailoredResume, Job
from backend.agents.resume_agent.resume_service import ResumeAgent
from config.settings import settings

router = APIRouter(prefix="/resumes", tags=["resumes"])

class MasterResumeResponse(BaseModel):
    id: int
    filename: str
    uploaded_at: str
    name: str
    email: str
    phone: str
    skills: list
    summary: str
    is_active: bool

class TailoredResumeResponse(BaseModel):
    id: int
    job_id: int
    tailored_title: str
    tailored_summary: str
    content_markdown: str
    highlighted_skills: list
    match_score: float
    zero_fabrication_verified: bool
    created_at: str
    file_path: Optional[str]

@router.get("/master")
def get_master_resume(db: Session = Depends(get_db)):
    resume = db.query(MasterResume).filter(MasterResume.is_active == True).order_by(MasterResume.uploaded_at.desc()).first()
    if not resume:
        return None
    parsed = resume.parsed_data or {}
    return {
        "id": resume.id,
        "filename": resume.filename,
        "uploaded_at": resume.uploaded_at.isoformat(),
        "name": parsed.get("name", "Candidate"),
        "email": parsed.get("email", ""),
        "phone": parsed.get("phone", ""),
        "linkedin": parsed.get("linkedin", ""),
        "github": parsed.get("github", ""),
        "skills": parsed.get("skills", []),
        "summary": parsed.get("summary", ""),
        "experience": parsed.get("experience_lines", []),
        "projects": parsed.get("project_lines", []),
        "education": parsed.get("education_lines", []),
        "is_active": resume.is_active,
        "raw_text": resume.raw_text
    }

@router.post("/master/upload")
async def upload_master_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    save_path = settings.MASTER_RESUME_DIR / file.filename
    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)
        
    parsed = ResumeAgent.parse_resume_file(str(save_path))
    
    # Mark old resumes inactive
    db.query(MasterResume).update({MasterResume.is_active: False})
    
    master = MasterResume(
        filename=file.filename,
        file_path=str(save_path),
        raw_text=parsed.get("raw_text", ""),
        parsed_data=parsed,
        is_active=True
    )
    db.add(master)
    db.commit()
    db.refresh(master)
    
    return {
        "status": "success",
        "id": master.id,
        "filename": master.filename,
        "skills_detected": len(parsed.get("skills", [])),
        "name": parsed.get("name")
    }

@router.post("/tailor/{job_id}")
def generate_tailored_resume(job_id: int, db: Session = Depends(get_db)):
    agent = ResumeAgent(db)
    try:
        tailored = agent.generate_tailored_resume(job_id)
        return {
            "id": tailored.id,
            "job_id": tailored.job_id,
            "tailored_title": tailored.tailored_title,
            "tailored_summary": tailored.tailored_summary,
            "highlighted_skills": tailored.highlighted_skills,
            "match_score": tailored.match_score,
            "zero_fabrication_verified": tailored.zero_fabrication_verified,
            "content_markdown": tailored.content_markdown,
            "created_at": tailored.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tailored/{job_id}")
def get_tailored_resume(job_id: int, db: Session = Depends(get_db)):
    tailored = db.query(TailoredResume).filter(TailoredResume.job_id == job_id).first()
    if not tailored:
        raise HTTPException(status_code=404, detail="Tailored resume not yet generated for this job")
        
    return {
        "id": tailored.id,
        "job_id": tailored.job_id,
        "tailored_title": tailored.tailored_title,
        "tailored_summary": tailored.tailored_summary,
        "highlighted_skills": tailored.highlighted_skills,
        "match_score": tailored.match_score,
        "zero_fabrication_verified": tailored.zero_fabrication_verified,
        "content_markdown": tailored.content_markdown,
        "created_at": tailored.created_at.isoformat(),
        "file_path": tailored.file_path
    }

@router.get("/download/{tailored_id}")
def download_tailored_doc(tailored_id: int, db: Session = Depends(get_db)):
    tailored = db.query(TailoredResume).filter(TailoredResume.id == tailored_id).first()
    if not tailored or not tailored.file_path:
        raise HTTPException(status_code=404, detail="Tailored document file not found")
    return FileResponse(
        path=tailored.file_path,
        filename=f"Tailored_Resume_Job_{tailored.job_id}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
