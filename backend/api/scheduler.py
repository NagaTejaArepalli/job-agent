from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.database.models import SchedulerRun
from backend.scheduler.scheduler_service import scheduler_instance
from config.settings import settings

router = APIRouter(prefix="/scheduler", tags=["scheduler"])

class SchedulerStatusResponse(BaseModel):
    is_running: bool
    enabled: bool
    daily_run_time: str
    recent_runs: List[dict] = []

@router.get("/status", response_model=SchedulerStatusResponse)
def get_scheduler_status(db: Session = Depends(get_db)):
    recent = db.query(SchedulerRun).order_by(SchedulerRun.run_time.desc()).limit(10).all()
    runs_data = [
        {
            "id": r.id,
            "run_time": r.run_time.isoformat() if r.run_time else "",
            "status": r.status,
            "jobs_discovered": r.jobs_discovered,
            "jobs_matched": r.jobs_matched,
            "summary": r.summary
        }
        for r in recent
    ]
    
    return SchedulerStatusResponse(
        is_running=scheduler_instance.is_running,
        enabled=settings.SCHEDULER_ENABLED,
        daily_run_time=f"{settings.DAILY_RUN_HOUR:02d}:{settings.DAILY_RUN_MINUTE:02d} UTC",
        recent_runs=runs_data
    )

@router.post("/trigger")
def trigger_now():
    """Manually triggers the daily discovery & matching pipeline immediately."""
    result = scheduler_instance.execute_daily_pipeline()
    return result
