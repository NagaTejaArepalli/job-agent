import re
from typing import Dict, Any, List, Set
from sqlalchemy.orm import Session
from backend.database.models import Job, JobMatch, MasterResume

COMMON_TECH_SKILLS = [
    "playwright", "selenium", "cypress", "appium", "java", "python", "javascript", "typescript",
    "c#", "rest assured", "postman", "api testing", "cucumber", "bdd", "tdd", "junit", "testng",
    "pytest", "jenkins", "github actions", "gitlab", "docker", "kubernetes", "aws", "azure", "gcp",
    "sql", "postgresql", "mysql", "mongodb", "git", "linux", "jira", "confluence", "performance testing",
    "jmeter", "k6", "ci/cd", "agile", "scrum", "microservices", "kafka", "selenium webdriver",
    "devin ai", "kiro ai", "mcp", "model context protocol", "microsoft graph api", "graphql", "serenity",
    "page object model", "pom", "parallel execution", "thread-safe", "gherkin", "maven"
]

class MatchingAgent:
    """
    Agent 2: Job Matching
    Compares job requirements with the candidate's master resume.
    Calculates technical skill match, experience alignment, and generates
    objective, transparent relevance scores and gap analysis.
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    def _extract_skills(self, text: str) -> Set[str]:
        text_lower = text.lower()
        found = set()
        for skill in COMMON_TECH_SKILLS:
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text_lower):
                found.add(skill)
        return found
        
    def _extract_years_experience(self, text: str) -> int:
        matches = re.findall(r"(\d+)\+?\s*(?:to\s*\d+\s*)?years?", text.lower())
        if matches:
            try:
                return max([int(m) for m in matches if int(m) < 40])
            except ValueError:
                pass
        return 3 # default estimated baseline
        
    def evaluate_job(self, job: Job, master_resume: MasterResume) -> Dict[str, Any]:
        from backend.utils.location_filter import is_india_location
        is_india, _ = is_india_location(job.location or "")
        if not is_india:
            return {
                "match_score": 0.0,
                "technical_score": 0.0,
                "experience_score": 0.0,
                "reasoning": f"Strictly excluded: Location '{job.location}' is outside India. Candidate requires opportunities within India only (Bangalore, Hyderabad, Chennai, Pune, Delhi NCR, or India Remote).",
                "key_matches": [],
                "missing_skills": []
            }

        resume_text = (master_resume.raw_text or "").lower()
        job_title = (job.title or "").lower()
        job_desc = (job.description or "").lower()
        full_job_text = f"{job_title} {job.department or ''} {job_desc}"
        
        # 1. Technical Skills Extraction
        job_skills = self._extract_skills(full_job_text)
        resume_skills = self._extract_skills(resume_text)
        
        # Additional custom skills from parsed_data if available
        if master_resume.parsed_data and "skills" in master_resume.parsed_data:
            parsed_skills = master_resume.parsed_data.get("skills", [])
            for s in parsed_skills:
                resume_skills.add(s.lower().strip())
                
        matched_skills = sorted(list(job_skills.intersection(resume_skills)))
        missing_skills = sorted(list(job_skills - resume_skills))
        
        # Technical score
        if job_skills:
            tech_score = (len(matched_skills) / len(job_skills)) * 100
        else:
            tech_score = 75.0 # baseline if JD is terse
            
        # 2. Title & Role Alignment
        role_score = 50.0
        sdet_keywords = ["sdet", "qa", "quality", "test", "automation", "engineer in test", "software engineer"]
        title_matches = [k for k in sdet_keywords if k in job_title]
        if title_matches:
            role_score = 90.0 if any(k in ["sdet", "automation"] for k in title_matches) else 80.0
            
        # 3. Experience alignment
        req_exp = self._extract_years_experience(job_desc)
        candidate_exp = master_resume.parsed_data.get("years_of_experience", 5) if master_resume.parsed_data else 5
        if candidate_exp >= req_exp:
            exp_score = 95.0
        elif candidate_exp >= req_exp - 1:
            exp_score = 80.0
        else:
            exp_score = 60.0
            
        # Overall weighted composite score
        composite_score = round((tech_score * 0.55) + (role_score * 0.25) + (exp_score * 0.20), 1)
        composite_score = min(99.0, max(15.0, composite_score))
        
        # Generate clear reasoning
        reasons = []
        if matched_skills:
            reasons.append(f"Strong overlap on key technologies: {', '.join(matched_skills[:6])}.")
        if missing_skills:
            reasons.append(f"Missing or unlisted keywords in master resume: {', '.join(missing_skills[:5])}.")
        if "sdet" in job_title or "automation" in job_title:
            reasons.append("High title alignment with core SDET / Automation specialization.")
        reasons.append(f"Estimated required experience: ~{req_exp} yrs (Profile matches: ~{candidate_exp} yrs).")
        
        return {
            "match_score": composite_score,
            "technical_score": round(tech_score, 1),
            "experience_score": round(exp_score, 1),
            "reasoning": " ".join(reasons),
            "key_matches": matched_skills,
            "missing_skills": missing_skills
        }
        
    def match_all_unmatched_jobs(self) -> Dict[str, Any]:
        master_resume = self.db.query(MasterResume).filter(MasterResume.is_active == True).order_by(MasterResume.uploaded_at.desc()).first()
        if not master_resume:
            return {"status": "error", "message": "No active master resume found. Please upload a master resume first."}
            
        unmatched_jobs = self.db.query(Job).filter(Job.match == None).all()
        matched_count = 0
        
        for job in unmatched_jobs:
            eval_res = self.evaluate_job(job, master_resume)
            match_record = JobMatch(
                job_id=job.id,
                match_score=eval_res["match_score"],
                technical_score=eval_res["technical_score"],
                experience_score=eval_res["experience_score"],
                reasoning=eval_res["reasoning"],
                key_matches=eval_res["key_matches"],
                missing_skills=eval_res["missing_skills"],
                status="new"
            )
            self.db.add(match_record)
            matched_count += 1
            
        self.db.commit()
        return {
            "status": "success",
            "evaluated_jobs": matched_count
        }
