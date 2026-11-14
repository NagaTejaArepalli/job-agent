from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.database.models import Job
from backend.scheduler.reporting_service import ReportingService

router = APIRouter(prefix="/reports", tags=["reports"])

def get_job_report_payload(db: Session):
    jobs = db.query(Job).filter(Job.status == "active").all()
    payload = []
    for j in jobs:
        m = j.match
        payload.append({
            "company_name": j.company.name if j.company else "",
            "title": j.title,
            "location": j.location,
            "ats_provider": j.company.ats_provider if j.company else "",
            "match_score": m.match_score if m else 0.0,
            "tech_score": m.technical_score if m else 0.0,
            "key_matches": m.key_matches if m else [],
            "missing_skills": m.missing_skills if m else [],
            "url": j.url,
            "status": j.status
        })
    return payload

@router.get("/excel")
def download_excel(db: Session = Depends(get_db)):
    data = get_job_report_payload(db)
    if not data:
        raise HTTPException(status_code=400, detail="No active jobs to export")
    filepath = ReportingService.generate_excel_report(data)
    return FileResponse(
        path=filepath,
        filename="Job_Discovery_Report.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.get("/csv")
def download_csv(db: Session = Depends(get_db)):
    data = get_job_report_payload(db)
    if not data:
        raise HTTPException(status_code=400, detail="No active jobs to export")
    filepath = ReportingService.generate_csv_report(data)
    return FileResponse(
        path=filepath,
        filename="Job_Discovery_Report.csv",
        media_type="text/csv"
    )
