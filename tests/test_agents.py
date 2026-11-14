import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.session import Base
from backend.database.models import Company, Job, MasterResume, QAKnowledgeItem, JobMatch
from backend.document_processor.qa_extractor import QAExtractor
from backend.knowledge_base.vector_store import SemanticKnowledgeRetriever
from backend.agents.matching_agent.matching_service import MatchingAgent
from backend.agents.resume_agent.resume_service import ResumeAgent
from backend.agents.application_agent.application_service import ApplicationAgent

# In-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db_session():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    # Setup test master resume
    master = MasterResume(
        filename="Test_Resume.docx",
        file_path="dummy/path.docx",
        raw_text="Alex SDET with 6 years experience in Playwright, Selenium, Java, REST Assured, CI/CD",
        parsed_data={
            "name": "Alex Morgan",
            "email": "alex@example.com",
            "phone": "555-0199",
            "years_of_experience": 6,
            "skills": ["Playwright", "Selenium", "Java", "Python", "REST Assured", "CI/CD"],
            "experience_lines": ["Senior SDET at TechCorp leading Playwright automation frameworks."]
        },
        is_active=True
    )
    session.add(master)
    
    # Setup test company and job
    comp = Company(
        name="TestCorp",
        career_url="https://boards.greenhouse.io/testcorp",
        ats_provider="greenhouse"
    )
    session.add(comp)
    session.commit()
    
    job = Job(
        company_id=comp.id,
        ats_job_id="job-1",
        title="Senior SDET - Playwright & Java",
        location="Remote",
        url="https://boards.greenhouse.io/testcorp/jobs/1",
        description="We are seeking an SDET with Playwright, Java, and REST Assured experience.",
        hash_id="testhash123"
    )
    session.add(job)
    
    # Setup Q&A Knowledge items
    qa1 = QAKnowledgeItem(
        question="What is your current CTC?",
        answer="$135,000 base + bonus",
        category="Compensation & CTC",
        tags=["ctc", "salary"]
    )
    qa2 = QAKnowledgeItem(
        question="How soon can you join?",
        answer="Notice period is 2 weeks.",
        category="Notice Period & Availability",
        tags=["notice", "availability"]
    )
    qa3 = QAKnowledgeItem(
        question="Are you authorized to work in the US?",
        answer="Yes, permanent resident.",
        category="Work Authorization & Visa",
        tags=["work authorization"],
        is_sensitive_declaration=True,
        needs_user_confirmation=True
    )
    session.add_all([qa1, qa2, qa3])
    session.commit()
    
    yield session
    session.close()

def test_semantic_knowledge_retriever(db_session):
    qa_items = [
        {"question": "What is your current CTC?", "answer": "$135,000 base", "category": "Compensation & CTC"},
        {"question": "How soon can you join?", "answer": "Notice period 2 weeks", "category": "Notice Period & Availability"}
    ]
    
    # Test semantic match for compensation
    res = SemanticKnowledgeRetriever.find_best_answer("What is your salary expectation / current CTC?", qa_items)
    assert res["matched"] is True
    assert "$135,000" in res["answer"]
    
    # Test semantic match for notice period
    res2 = SemanticKnowledgeRetriever.find_best_answer("What is your notice period and when can you start?", qa_items)
    assert res2["matched"] is True
    assert "Notice period" in res2["answer"]

def test_matching_agent_evaluation(db_session):
    matcher = MatchingAgent(db_session)
    job = db_session.query(Job).first()
    master = db_session.query(MasterResume).first()
    
    result = matcher.evaluate_job(job, master)
    assert result["match_score"] >= 75.0
    assert "playwright" in result["key_matches"]
    assert "java" in result["key_matches"]

def test_tailored_resume_zero_fabrication(db_session):
    resume_agent = ResumeAgent(db_session)
    job = db_session.query(Job).first()
    
    tailored = resume_agent.generate_tailored_resume(job.id)
    assert tailored.zero_fabrication_verified is True
    assert "Playwright" in tailored.highlighted_skills
    assert "Playwright" in tailored.content_markdown
    # Verify no fabricated content: candidate name must match master
    assert "Alex Morgan" in tailored.content_markdown

def test_application_agent_workflow(db_session):
    app_agent = ApplicationAgent(db_session)
    job = db_session.query(Job).first()
    
    app = app_agent.prepare_application_packet(job.id)
    assert app.job_id == job.id
    assert "first_name" in app.prepared_answers
    assert app.prepared_answers["first_name"]["value"] == "Alex"
    assert "resume_file" in app.prepared_answers
    # Verify human checklist exists and contains manual submit requirement
    checklist_tasks = [item["id"] for item in app.submission_checklist]
    assert "manual_submit" in checklist_tasks
    assert "legal_declarations" in checklist_tasks
