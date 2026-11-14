import sys
import os
from pathlib import Path

# Add project root to sys.path so it works directly from any runner / GitHub Actions
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import asyncio
from datetime import datetime
from backend.database.session import SessionLocal, init_db
from backend.database.models import SchedulerRun
from backend.agents.discovery_agent.discovery_service import DiscoveryAgent
from backend.agents.matching_agent.matching_service import MatchingAgent
from backend.scheduler.reporting_service import ReportingService

def run_daily_pipeline_standalone():
    """
    Executes the complete everyday job discovery and matching pipeline.
    Can be run:
    1. By APScheduler while the backend is running.
    2. Directly via Windows Task Scheduler every morning at a scheduled time.
    3. Manually via 'python backend/run_daily.py'.
    
    Operates 100% locally on your machine with NO cloud publishing or external site needed.
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting daily job pipeline...", flush=True)
    init_db()
    db = SessionLocal()

    from backend.database.models import Company, Job
    company_count = db.query(Company).filter(Company.active == True).count()
    if company_count == 0:
        print("-> Fresh database detected. Seeding 148 target companies, Master Resume, and 41 Q&A items...", flush=True)
        from backend.database.seed import seed_initial_data
        seed_initial_data(db)
        company_count = db.query(Company).filter(Company.active == True).count()
        print(f"   Successfully initialized {company_count} target companies in database.", flush=True)
    else:
        print(f"   Loaded {company_count} target companies from database.", flush=True)

    from backend.agents.llm_client import gemini_client
    if gemini_client.is_available:
        print(f"-> Gemini AI Engine: ACTIVE (Model: {gemini_client.model})", flush=True)
    else:
        print("-> Gemini AI Engine: Running in fast heuristic matching mode (GEMINI_API_KEY optional)", flush=True)
    
    run_record = SchedulerRun(
        run_time=datetime.utcnow(),
        status="running"
    )
    db.add(run_record)
    db.commit()
    
    try:
        # 1. Discover jobs across all 148 target companies
        print(f"-> Step 1: Discovering new jobs across {company_count} official career portals in parallel (India only)...", flush=True)
        discovery_agent = DiscoveryAgent(db)
        discovery_res = asyncio.run(discovery_agent.run_discovery_all())
        total_active_jobs = db.query(Job).filter(Job.status == "active").count()
        print(f"   Scanned {discovery_res.get('companies_scanned', company_count)} companies: {discovery_res.get('new_jobs_added', 0)} new jobs added. Total active India jobs: {total_active_jobs}.", flush=True)
        
        # 2. Verify active job links
        print("-> Step 2: Verifying active links and expiring closed postings...", flush=True)
        verify_res = asyncio.run(discovery_agent.verify_active_jobs(limit=100))
        print(f"   Checked: {verify_res.get('checked', 0)}, Deactivated: {verify_res.get('deactivated', 0)}.", flush=True)
        
        # 3. Match new jobs against Naga Teja Arepalli's Master Resume
        print("-> Step 3: Running relevance matching against Master Resume...", flush=True)
        matching_agent = MatchingAgent(db)
        matching_res = matching_agent.match_all_unmatched_jobs()
        print(f"   Evaluated: {matching_res.get('evaluated_jobs', 0)} jobs.", flush=True)
        
        # 4. Generate daily summary Excel report
        print("-> Step 4: Generating daily summary Excel report...", flush=True)
        from backend.api.reports import get_job_report_payload
        from backend.scheduler.email_service import send_email_alert
        report_data = get_job_report_payload(db)
        report_path = None
        if report_data:
            report_path = ReportingService.generate_excel_report(report_data)
            print(f"   Daily report saved locally to: {report_path}", flush=True)

        # 5. Send Email Alert with HTML Report & Attached Excel
        print("-> Step 5: Sending Email Notification with HTML report and Excel attachment...", flush=True)
        recipient = os.getenv("ALERT_EMAIL_TO", "naga.teja.are@gmail.com").strip()
        candidate_name = "Naga Teja Arepalli"
        matched_jobs = [j for j in report_data if j.get("match_score", 0) >= 50] if report_data else []
        if not matched_jobs and report_data:
            matched_jobs = report_data[:10]

        email_sent = send_email_alert(
            candidate_name=candidate_name,
            recipient_email=recipient,
            jobs_data=matched_jobs,
            excel_attachment_path=report_path
        )
        if email_sent:
            print(f"   HTML report & Excel attachment sent to {recipient}!", flush=True)
        else:
            print("   Email alert skipped/failed (check SMTP_USER and SMTP_PASS secrets).", flush=True)
            
        # Update Scheduler log
        run_record.status = "completed"
        run_record.jobs_discovered = discovery_res.get("new_jobs_added", 0)
        run_record.jobs_matched = matching_res.get("evaluated_jobs", 0)
        run_record.summary = (
            f"Discovered: {discovery_res.get('new_jobs_added', 0)} new. "
            f"Matched: {matching_res.get('evaluated_jobs', 0)}. "
            f"Active: {len(report_data) if report_data else 0} India postings."
        )
        db.commit()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Daily pipeline completed successfully!\n", flush=True)
        return run_record.summary
        
    except Exception as e:
        db.rollback()
        run_record.status = "failed"
        run_record.errors = [str(e)]
        db.commit()
        print(f"Pipeline error: {e}")
        return str(e)
    finally:
        db.close()

if __name__ == "__main__":
    run_daily_pipeline_standalone()
