import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from config.settings import settings
from backend.database.session import init_db, SessionLocal
from backend.database.seed import seed_initial_data
from backend.scheduler.scheduler_service import scheduler_instance

# Import routers
from backend.api.companies import router as companies_router
from backend.api.jobs import router as jobs_router
from backend.api.knowledge_base import router as kb_router
from backend.api.resumes import router as resumes_router
from backend.api.applications import router as applications_router
from backend.api.scheduler import router as scheduler_router
from backend.api.reports import router as reports_router
from backend.api.stats import router as stats_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB tables and seed data
    print("[Main] Initializing database...")
    init_db()
    db = SessionLocal()
    try:
        seed_initial_data(db)
    finally:
        db.close()
        
    # Start APScheduler
    print("[Main] Starting daily background scheduler...")
    scheduler_instance.start()
    
    yield
    
    # Shutdown
    print("[Main] Shutting down scheduler...")
    scheduler_instance.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Central orchestration backend for everyday AI Job Discovery, Profile Matching, Knowledge-Based Application Assistant, and Resume Tailoring.",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(companies_router, prefix=settings.API_V1_STR)
app.include_router(jobs_router, prefix=settings.API_V1_STR)
app.include_router(kb_router, prefix=settings.API_V1_STR)
app.include_router(resumes_router, prefix=settings.API_V1_STR)
app.include_router(applications_router, prefix=settings.API_V1_STR)
app.include_router(scheduler_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(stats_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "scheduler_running": scheduler_instance.is_running
    }

# Mount static frontend if dist folder exists
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
