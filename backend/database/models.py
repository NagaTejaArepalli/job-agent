import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database.session import Base

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    career_url = Column(String(1024), nullable=False)
    ats_provider = Column(String(50), default="generic") # greenhouse, lever, ashby, smartrecruiters, workday, generic
    board_token = Column(String(255), nullable=True) # e.g. 'stripe' for greenhouse or lever identifier
    active = Column(Boolean, default=True)
    keywords = Column(Text, nullable=True) # comma separated or custom search query
    location_preference = Column(String(255), nullable=True)
    last_scraped_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    ats_job_id = Column(String(255), nullable=True)
    title = Column(String(512), nullable=False, index=True)
    location = Column(String(255), default="Remote / Unspecified")
    department = Column(String(255), nullable=True)
    employment_type = Column(String(100), default="Full-time")
    url = Column(String(1024), nullable=False)
    description = Column(Text, nullable=True)
    salary_range = Column(String(255), nullable=True)
    hash_id = Column(String(64), unique=True, index=True)
    status = Column(String(50), default="active") # active, expired, hidden
    first_seen = Column(DateTime, default=datetime.datetime.utcnow)
    last_verified = Column(DateTime, default=datetime.datetime.utcnow)
    
    company = relationship("Company", back_populates="jobs")
    match = relationship("JobMatch", back_populates="job", uselist=False, cascade="all, delete-orphan")
    application = relationship("Application", back_populates="job", uselist=False, cascade="all, delete-orphan")
    tailored_resumes = relationship("TailoredResume", back_populates="job", cascade="all, delete-orphan")

class JobMatch(Base):
    __tablename__ = "job_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, unique=True)
    match_score = Column(Float, default=0.0) # 0 to 100
    technical_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    reasoning = Column(Text, nullable=True)
    key_matches = Column(JSON, default=list) # Matched skills / tech
    missing_skills = Column(JSON, default=list) # Missing keywords
    status = Column(String(50), default="new") # new, interested, applying, applied, rejected
    evaluated_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    job = relationship("Job", back_populates="match")

class MasterResume(Base):
    __tablename__ = "master_resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(1024), nullable=False)
    raw_text = Column(Text, nullable=False)
    parsed_data = Column(JSON, default=dict) # contact, summary, skills, experience, projects, education, certs
    is_active = Column(Boolean, default=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

class TailoredResume(Base):
    __tablename__ = "tailored_resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    master_resume_id = Column(Integer, ForeignKey("master_resumes.id"), nullable=False)
    tailored_title = Column(String(255), nullable=False)
    tailored_summary = Column(Text, nullable=False)
    content_markdown = Column(Text, nullable=False)
    highlighted_skills = Column(JSON, default=list)
    highlighted_projects = Column(JSON, default=list)
    file_path = Column(String(1024), nullable=True)
    match_score = Column(Float, default=0.0)
    zero_fabrication_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    job = relationship("Job", back_populates="tailored_resumes")
    master_resume = relationship("MasterResume")

class QAKnowledgeItem(Base):
    __tablename__ = "qa_knowledge_items"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False, index=True)
    answer = Column(Text, nullable=False)
    category = Column(String(100), default="General", index=True) 
    # Categories: Compensation & CTC, Notice Period & Availability, Automation & SDET, API Testing & Tools, Frameworks & CI/CD, Work Authorization & Visa, Behavioral & Culture, General
    source_doc = Column(String(255), nullable=True)
    tags = Column(JSON, default=list)
    times_used = Column(Integer, default=0)
    is_sensitive_declaration = Column(Boolean, default=False) # e.g. legal declaration, criminal background, non-compete
    needs_user_confirmation = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, unique=True)
    tailored_resume_id = Column(Integer, ForeignKey("tailored_resumes.id"), nullable=True)
    status = Column(String(50), default="draft") # draft, prepared, ready_for_review, submitted, rejected, interview, offer
    prepared_answers = Column(JSON, default=dict) # {"field_name": {"answer": "...", "source": "knowledge_base", "confidence": 0.95}}
    missing_answers = Column(JSON, default=list) # list of questions that need user attention
    submission_checklist = Column(JSON, default=list) # checklist of items user must verify before submitting
    notes = Column(Text, nullable=True)
    submission_url = Column(String(1024), nullable=True)
    applied_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    job = relationship("Job", back_populates="application")
    tailored_resume = relationship("TailoredResume")

class SchedulerRun(Base):
    __tablename__ = "scheduler_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    run_time = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(50), default="completed") # running, completed, failed
    jobs_discovered = Column(Integer, default=0)
    jobs_matched = Column(Integer, default=0)
    errors = Column(JSON, default=list)
    summary = Column(Text, nullable=True)
