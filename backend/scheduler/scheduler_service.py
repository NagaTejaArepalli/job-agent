import asyncio
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from backend.database.session import SessionLocal
from backend.database.models import SchedulerRun
from backend.agents.discovery_agent.discovery_service import DiscoveryAgent
from backend.agents.matching_agent.matching_service import MatchingAgent
from config.settings import settings

class DailyJobScheduler:
    """
    Orchestrates automated daily runs of the AI Job Search & Application system:
    1. Discovers new postings across all configured company career sites & ATS APIs
    2. Verifies active links and marks closed jobs as expired
    3. Runs Job Matching Agent to score postings against the Master Resume
    4. Logs execution metrics and error states
    """
    
    def __init__(self):
        self.scheduler = BackgroundScheduler(daemon=True)
        self.is_running = False
        
    def start(self):
        if not settings.SCHEDULER_ENABLED:
            print("[Scheduler] Daily scheduler is disabled in settings.")
            return
            
        # Trigger daily at configured hour and minute
        trigger = CronTrigger(hour=settings.DAILY_RUN_HOUR, minute=settings.DAILY_RUN_MINUTE)
        self.scheduler.add_job(
            self.execute_daily_pipeline,
            trigger=trigger,
            id="daily_job_discovery",
            name="Daily Job Discovery & Matching",
            replace_existing=True
        )
        self.scheduler.start()
        self.is_running = True
        print(f"[Scheduler] Daily job scheduler started. Next run scheduled for {settings.DAILY_RUN_HOUR:02d}:{settings.DAILY_RUN_MINUTE:02d} daily.")
        
    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            
    def execute_daily_pipeline(self) -> dict:
        """Runs the entire end-to-end discovery and matching pipeline synchronously or inside event loop."""
        print(f"[{datetime.utcnow().isoformat()}] Starting scheduled daily job discovery pipeline...")
        db: Session = SessionLocal()
        run_record = SchedulerRun(
            run_time=datetime.utcnow(),
            status="running"
        )
        db.add(run_record)
        db.commit()
        
        try:
            # 1. Run Discovery Agent
            discovery_agent = DiscoveryAgent(db)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            discovery_result = loop.run_until_complete(discovery_agent.run_discovery_all())
            
            # 2. Run Job Verifier
            verify_result = loop.run_until_complete(discovery_agent.verify_active_jobs(limit=100))
            loop.close()
            
            # 3. Run Matching Agent
            matching_agent = MatchingAgent(db)
            matching_result = matching_agent.match_all_unmatched_jobs()
            
            # Update record
            run_record.status = "completed"
            run_record.jobs_discovered = discovery_result.get("new_jobs_added", 0)
            run_record.jobs_matched = matching_result.get("evaluated_jobs", 0)
            run_record.summary = (
                f"Discovered: {discovery_result.get('total_jobs_found', 0)} total, "
                f"{discovery_result.get('new_jobs_added', 0)} new. "
                f"Deactivated: {verify_result.get('deactivated', 0)}. "
                f"Matched: {matching_result.get('evaluated_jobs', 0)}."
            )
            db.commit()
            
            print(f"[Scheduler] Pipeline completed successfully: {run_record.summary}")
            return {
                "status": "completed",
                "summary": run_record.summary,
                "discovery": discovery_result,
                "matching": matching_result
            }
        except Exception as e:
            db.rollback()
            run_record.status = "failed"
            run_record.errors = [str(e)]
            db.commit()
            print(f"[Scheduler] Daily pipeline failed: {e}")
            return {"status": "failed", "error": str(e)}
        finally:
            db.close()

scheduler_instance = DailyJobScheduler()
