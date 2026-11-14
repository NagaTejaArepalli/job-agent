from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.database.models import Application, Job, TailoredResume, QAKnowledgeItem, MasterResume
from backend.knowledge_base.vector_store import SemanticKnowledgeRetriever

# Standard application fields common across Greenhouse, Lever, Workday, Ashby, SmartRecruiters
STANDARD_FIELDS = [
    {"field": "first_name", "label": "First Name", "type": "text", "standard": True},
    {"field": "last_name", "label": "Last Name", "type": "text", "standard": True},
    {"field": "email", "label": "Email Address", "type": "email", "standard": True},
    {"field": "phone", "label": "Phone Number", "type": "tel", "standard": True},
    {"field": "location", "label": "Current City / Location", "type": "text", "standard": True},
    {"field": "linkedin", "label": "LinkedIn Profile", "type": "url", "standard": True},
    {"field": "github", "label": "GitHub / Portfolio", "type": "url", "standard": True},
    {"field": "current_ctc", "label": "Current CTC / Salary", "type": "text", "question": "What is your current CTC?"},
    {"field": "expected_ctc", "label": "Expected CTC / Salary", "type": "text", "question": "What is your expected CTC?"},
    {"field": "notice_period", "label": "Notice Period / Earliest Start Date", "type": "text", "question": "How soon can you join? What is your notice period?"},
    {"field": "work_authorization", "label": "Are you legally authorized to work?", "type": "radio", "question": "Are you legally authorized to work in the country without sponsorship?"},
    {"field": "visa_sponsorship", "label": "Will you now or in the future require visa sponsorship?", "type": "radio", "question": "Will you require visa sponsorship?"},
    {"field": "automation_experience", "label": "Describe your test automation experience", "type": "textarea", "question": "Describe your automation testing experience with Playwright or Selenium."},
    {"field": "api_testing_experience", "label": "Have you worked with API automation?", "type": "textarea", "question": "Have you worked with API automation and REST Assured?"}
]

class ApplicationAgent:
    """
    Agent 3: Application Assistant
    Prepares complete application packets, extracts & retrieves verified answers
    from the personal Q&A knowledge base, flags missing or sensitive questions,
    and stages everything for the user's manual review & submission.
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    def prepare_application_packet(self, job_id: int, custom_questions: Optional[List[str]] = None) -> Application:
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise ValueError(f"Job with ID {job_id} not found")
            
        # Get or create tailored resume
        tailored_resume = self.db.query(TailoredResume).filter(TailoredResume.job_id == job_id).first()
        if not tailored_resume:
            from backend.agents.resume_agent.resume_service import ResumeAgent
            resume_agent = ResumeAgent(self.db)
            tailored_resume = resume_agent.generate_tailored_resume(job_id)
            
        # Get all Q&A knowledge items from DB
        qa_records = self.db.query(QAKnowledgeItem).all()
        qa_items = [
            {
                "id": q.id,
                "question": q.question,
                "answer": q.answer,
                "category": q.category,
                "source_doc": q.source_doc,
                "is_sensitive_declaration": q.is_sensitive_declaration
            }
            for q in qa_records
        ]
        
        # Candidate master profile
        master = self.db.query(MasterResume).filter(MasterResume.is_active == True).order_by(MasterResume.uploaded_at.desc()).first()
        profile_data = master.parsed_data if master else {}
        
        prepared_answers: Dict[str, Any] = {}
        missing_answers: List[Dict[str, Any]] = []
        submission_checklist: List[Dict[str, Any]] = []
        
        # 1. Fill standard contact fields from master resume profile
        prepared_answers["first_name"] = {
            "label": "First Name",
            "value": profile_data.get("name", "Candidate").split()[0],
            "source": "Master Profile",
            "confidence": 1.0,
            "verified": True
        }
        prepared_answers["last_name"] = {
            "label": "Last Name",
            "value": " ".join(profile_data.get("name", "Candidate").split()[1:]) or "Candidate",
            "source": "Master Profile",
            "confidence": 1.0,
            "verified": True
        }
        prepared_answers["email"] = {
            "label": "Email Address",
            "value": profile_data.get("email", ""),
            "source": "Master Profile",
            "confidence": 1.0,
            "verified": True
        }
        prepared_answers["phone"] = {
            "label": "Phone Number",
            "value": profile_data.get("phone", ""),
            "source": "Master Profile",
            "confidence": 1.0,
            "verified": True
        }
        prepared_answers["linkedin"] = {
            "label": "LinkedIn Profile",
            "value": profile_data.get("linkedin", ""),
            "source": "Master Profile",
            "confidence": 1.0,
            "verified": True
        }
        prepared_answers["github"] = {
            "label": "GitHub / Portfolio",
            "value": profile_data.get("github", ""),
            "source": "Master Profile",
            "confidence": 1.0,
            "verified": True
        }
        prepared_answers["resume_file"] = {
            "label": "Attached Resume",
            "value": tailored_resume.file_path or f"tailored_resume_job_{job.id}.docx",
            "source": "Tailored Resume Generator",
            "confidence": 1.0,
            "verified": True
        }
        
        # 2. Process QA application questions
        questions_to_process = [
            ("Current CTC", "What is your current CTC?"),
            ("Expected CTC", "What is your expected CTC?"),
            ("Notice Period", "How soon can you join? What is your notice period?"),
            ("Work Authorization", "Are you legally authorized to work in the country without sponsorship?"),
            ("Visa Sponsorship", "Will you require visa sponsorship now or in the future?"),
            ("Automation Experience", "Describe your automation testing experience with Playwright, Selenium or frameworks."),
            ("API Testing", "Have you worked with API automation and REST Assured?")
        ]
        
        if custom_questions:
            for cq in custom_questions:
                questions_to_process.append((cq[:30], cq))
                
        for key, q_text in questions_to_process:
            retrieval = SemanticKnowledgeRetriever.find_best_answer(q_text, qa_items)
            field_key = key.lower().replace(" ", "_")
            
            if retrieval["matched"] and not retrieval["needs_user_input"]:
                prepared_answers[field_key] = {
                    "label": key,
                    "question": q_text,
                    "value": retrieval["answer"],
                    "matched_kb_question": retrieval["matched_question"],
                    "source": f"Knowledge Base ({retrieval.get('source_doc', 'Consolidated Document')})",
                    "category": retrieval.get("category"),
                    "confidence": retrieval["confidence"],
                    "verified": True
                }
            else:
                missing_answers.append({
                    "field_key": field_key,
                    "label": key,
                    "question": q_text,
                    "suggested_answer": retrieval.get("answer"),
                    "confidence": retrieval["confidence"],
                    "reason": retrieval["reason"],
                    "is_sensitive_declaration": retrieval.get("is_sensitive_declaration", False)
                })
                
        # 3. Build mandatory Pre-Submission Human Checklist
        submission_checklist = [
            {
                "id": "review_fields",
                "task": "Review pre-filled contact details and personal answers",
                "completed": False,
                "required": True
            },
            {
                "id": "check_tailored_resume",
                "task": f"Confirm tailored resume attachments ({tailored_resume.tailored_title})",
                "completed": False,
                "required": True
            },
            {
                "id": "legal_declarations",
                "task": "Personally review and sign off any company legal disclaimers, background checks or consent checkboxes",
                "completed": False,
                "required": True
            },
            {
                "id": "manual_submit",
                "task": "Manually click 'Submit Application' on the employer's official career portal",
                "completed": False,
                "required": True
            }
        ]
        
        # Save or update Application record
        existing_app = self.db.query(Application).filter(Application.job_id == job_id).first()
        if existing_app:
            existing_app.tailored_resume_id = tailored_resume.id
            existing_app.prepared_answers = prepared_answers
            existing_app.missing_answers = missing_answers
            existing_app.submission_checklist = submission_checklist
            existing_app.submission_url = job.url
            existing_app.status = "ready_for_review" if not missing_answers else "prepared"
            self.db.commit()
            return existing_app
            
        app = Application(
            job_id=job.id,
            tailored_resume_id=tailored_resume.id,
            status="ready_for_review" if not missing_answers else "prepared",
            prepared_answers=prepared_answers,
            missing_answers=missing_answers,
            submission_checklist=submission_checklist,
            submission_url=job.url
        )
        self.db.add(app)
        self.db.commit()
        self.db.refresh(app)
        return app
