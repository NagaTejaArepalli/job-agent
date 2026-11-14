import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

class Settings(BaseModel):
    PROJECT_NAME: str = "AI Job Search & Application Agent"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Storage directories
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = DATA_DIR
    MASTER_RESUME_DIR: Path = DATA_DIR / "master_resume"
    TAILORED_RESUME_DIR: Path = DATA_DIR / "tailored_resumes"
    COMPANY_CONFIG_DIR: Path = DATA_DIR / "company_config"
    KNOWLEDGE_DOCS_DIR: Path = DATA_DIR / "knowledge_docs"
    APPLICATION_RECORDS_DIR: Path = DATA_DIR / "application_records"
    REPORTS_DIR: Path = DATA_DIR / "reports"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/job_agent.db")
    
    # Scheduler
    DAILY_RUN_HOUR: int = int(os.getenv("DAILY_RUN_HOUR", "8"))
    DAILY_RUN_MINUTE: int = int(os.getenv("DAILY_RUN_MINUTE", "0"))
    SCHEDULER_ENABLED: bool = os.getenv("SCHEDULER_ENABLED", "True").lower() == "true"
    
    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "heuristic") # options: heuristic, openai, gemini, ollama
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Automation & Browser
    HEADLESS_BROWSER: bool = os.getenv("HEADLESS_BROWSER", "False").lower() == "true"
    HUMAN_SUBMISSION_REQUIRED: bool = True # Crucial rule: Always stop before submit!

    def init_directories(self):
        for directory in [
            self.DATA_DIR,
            self.MASTER_RESUME_DIR,
            self.TAILORED_RESUME_DIR,
            self.COMPANY_CONFIG_DIR,
            self.KNOWLEDGE_DOCS_DIR,
            self.APPLICATION_RECORDS_DIR,
            self.REPORTS_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.init_directories()
