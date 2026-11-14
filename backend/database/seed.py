from sqlalchemy.orm import Session
from backend.database.models import Company, MasterResume, QAKnowledgeItem, Job, JobMatch
from config.settings import settings

def seed_initial_data(db: Session):
    # 1. Seed Company Configurations if empty
    if db.query(Company).count() == 0:
        companies = [
            Company(
                name="Stripe",
                career_url="https://boards.greenhouse.io/stripe",
                ats_provider="greenhouse",
                board_token="stripe",
                keywords="SDET, QA, Test Automation, Software Engineer in Test, Quality",
                location_preference="Remote"
            ),
            Company(
                name="Netflix",
                career_url="https://jobs.lever.co/netflix",
                ats_provider="lever",
                board_token="netflix",
                keywords="Test, Quality, Automation, SDET, Engineer",
                location_preference="Remote"
            ),
            Company(
                name="OpenAI",
                career_url="https://jobs.ashbyhq.com/openai",
                ats_provider="ashby",
                board_token="openai",
                keywords="Quality, Test, Systems, Infrastructure, Automation",
                location_preference="Remote"
            ),
            Company(
                name="Spotify",
                career_url="https://jobs.smartrecruiters.com/Spotify",
                ats_provider="smartrecruiters",
                board_token="Spotify",
                keywords="Quality, Test, SDET, Automation, Backend",
                location_preference="Remote"
            ),
            Company(
                name="Datadog",
                career_url="https://boards.greenhouse.io/datadog",
                ats_provider="greenhouse",
                board_token="datadog",
                keywords="SDET, QA, Automation, Test, Reliability",
                location_preference="Remote"
            )
        ]
        db.add_all(companies)
        db.commit()
        print("[Seed] Seeded initial companies.")

    # 2. Seed Master Resume if empty
    if db.query(MasterResume).count() == 0:
        master_resume_data = {
            "name": "Alex Morgan",
            "email": "alex.morgan.sdet@example.com",
            "phone": "+1 (555) 234-5678",
            "linkedin": "https://linkedin.com/in/alexmorgansdet",
            "github": "https://github.com/alexmorgansdet",
            "years_of_experience": 6,
            "summary": "Senior Software Development Engineer in Test (SDET) with 6+ years of expertise designing modern test automation frameworks, accelerating CI/CD deployment pipelines, and scaling web, API, and microservice testing suites.",
            "skills": [
                "Playwright", "Selenium WebDriver", "Java", "Python", "TypeScript", 
                "REST Assured", "Postman", "TestNG", "JUnit", "Cucumber (BDD)", 
                "Jenkins", "GitHub Actions", "Docker", "AWS", "SQL", "Git", "JIRA"
            ],
            "experience_lines": [
                "Senior SDET at CloudTech Solutions (2021 - Present): Architected end-to-end web test automation suite using Playwright with TypeScript and Java REST Assured; slashed regression testing cycle from 14 hours to 45 minutes across 80+ microservices.",
                "SDET II at FinEdge Software (2018 - 2021): Built enterprise Selenium WebDriver + Java framework with TestNG and Dockerized parallel execution in Jenkins CI/CD pipeline.",
                "QA Automation Engineer at Alpha Systems (2016 - 2018): Developed API automation suites with Postman and REST Assured; conducted load and contract testing."
            ],
            "project_lines": [
                "Cloud-Native E2E Test Platform: Scalable Playwright testing infrastructure integrated with GitHub Actions and AWS Fargate, running 2,500+ parallel test scenarios daily.",
                "REST Assured Microservices Framework: Reusable Java library for automated contract and API schema verification with automated Slack alerts."
            ],
            "education_lines": [
                "Bachelor of Science in Computer Science, State University (2016)",
                "AWS Certified Solutions Architect – Associate",
                "ISTQB Certified Tester – Advanced Level (Test Automation Engineer)"
            ],
            "raw_text": """
Alex Morgan
alex.morgan.sdet@example.com | +1 (555) 234-5678 | San Francisco, CA | https://linkedin.com/in/alexmorgansdet | https://github.com/alexmorgansdet

Professional Summary:
Senior Software Development Engineer in Test (SDET) with 6+ years of expertise designing modern test automation frameworks, accelerating CI/CD deployment pipelines, and scaling web, API, and microservice testing suites.

Core Skills:
Playwright, Selenium WebDriver, Java, Python, TypeScript, REST Assured, Postman, TestNG, JUnit, Cucumber (BDD), Jenkins, GitHub Actions, Docker, AWS, SQL, Git, JIRA

Professional Experience:
Senior SDET at CloudTech Solutions (2021 - Present):
- Architected end-to-end web test automation suite using Playwright with TypeScript and Java REST Assured.
- Slashed regression testing cycle from 14 hours to 45 minutes across 80+ microservices.
- Implemented comprehensive mock server and contract tests reducing production escaped bugs by 42%.

SDET II at FinEdge Software (2018 - 2021):
- Built enterprise Selenium WebDriver + Java framework with TestNG and Dockerized parallel execution in Jenkins CI/CD pipeline.
- Mentored junior QA engineers in writing maintainable Page Object Model (POM) automation code.

QA Automation Engineer at Alpha Systems (2016 - 2018):
- Developed API automation suites with Postman and REST Assured; conducted load and contract testing.

Education & Certifications:
- Bachelor of Science in Computer Science, State University (2016)
- AWS Certified Solutions Architect – Associate
- ISTQB Certified Tester – Advanced Level (Test Automation Engineer)
"""
        }
        
        master = MasterResume(
            filename="Alex_Morgan_Master_Resume.docx",
            file_path=str(settings.MASTER_RESUME_DIR / "Alex_Morgan_Master_Resume.docx"),
            raw_text=master_resume_data["raw_text"],
            parsed_data=master_resume_data,
            is_active=True
        )
        db.add(master)
        db.commit()
        print("[Seed] Seeded default Master Resume.")

    # 3. Seed Consolidated Q&A Knowledge Base
    if db.query(QAKnowledgeItem).count() == 0:
        qa_items = [
            QAKnowledgeItem(
                question="What is your current CTC?",
                answer="My current compensation package is $135,000 base salary plus annual performance bonus and equity.",
                category="Compensation & CTC",
                source_doc="Master_QA_Document.docx",
                tags=["ctc", "salary", "compensation", "current ctc"],
                is_sensitive_declaration=False
            ),
            QAKnowledgeItem(
                question="What is your expected CTC?",
                answer="My target compensation is $155,000 - $175,000 total compensation, open to discussing based on team scope, equity, and overall benefits.",
                category="Compensation & CTC",
                source_doc="Master_QA_Document.docx",
                tags=["ctc", "salary", "expected ctc", "compensation"],
                is_sensitive_declaration=False
            ),
            QAKnowledgeItem(
                question="How soon can you join? What is your notice period?",
                answer="I have a standard 2 to 3 weeks notice period with my current employer and can join immediately upon completion of notice.",
                category="Notice Period & Availability",
                source_doc="Master_QA_Document.docx",
                tags=["notice", "availability", "start date", "how soon"],
                is_sensitive_declaration=False
            ),
            QAKnowledgeItem(
                question="Describe your automation experience.",
                answer="Over 6 years of hands-on experience building robust UI and API automation frameworks from scratch using Playwright, Selenium WebDriver, Java, TypeScript, and Python. Designed Page Object Models and integrated tests into Jenkins and GitHub Actions CI/CD pipelines.",
                category="Automation & SDET",
                source_doc="Master_QA_Document.docx",
                tags=["automation", "playwright", "selenium", "frameworks", "sdet"],
                is_sensitive_declaration=False
            ),
            QAKnowledgeItem(
                question="Have you worked with API automation?",
                answer="Yes, extensive experience with API test automation using REST Assured (Java), Requests/pytest (Python), and Postman/Newman. Experienced with JSON schema validation, OAuth2/JWT token flows, payload assertions, and mock API servers.",
                category="API Testing & Tools",
                source_doc="Master_QA_Document.docx",
                tags=["api", "rest assured", "postman", "api automation"],
                is_sensitive_declaration=False
            ),
            QAKnowledgeItem(
                question="Are you legally authorized to work in the country without sponsorship?",
                answer="Yes, I am a permanent resident and fully authorized to work in the United States for any employer without requiring sponsorship.",
                category="Work Authorization & Visa",
                source_doc="Master_QA_Document.docx",
                tags=["work authorization", "visa", "sponsorship", "authorized"],
                is_sensitive_declaration=True,
                needs_user_confirmation=True
            ),
            QAKnowledgeItem(
                question="Will you now or in the future require visa sponsorship?",
                answer="No, I do not require current or future visa sponsorship.",
                category="Work Authorization & Visa",
                source_doc="Master_QA_Document.docx",
                tags=["visa", "sponsorship", "require sponsorship"],
                is_sensitive_declaration=True,
                needs_user_confirmation=True
            ),
            QAKnowledgeItem(
                question="Describe your experience with CI/CD and DevOps pipelines.",
                answer="Configured headless test executions in Jenkins, GitHub Actions, and GitLab CI. Containerized automated tests using Docker for cross-browser parallel runs, and integrated test result reporting with Allure and Slack webhooks.",
                category="Frameworks & CI/CD",
                source_doc="Master_QA_Document.docx",
                tags=["ci/cd", "jenkins", "github actions", "docker", "pipeline"],
                is_sensitive_declaration=False
            ),
            QAKnowledgeItem(
                question="Tell me about a time you identified a critical bug before production.",
                answer="During an API microservice refactor, our automated REST Assured regression suite caught a concurrency race condition in token expiration that would have logged out thousands of active users. We isolated the root cause, worked directly with backend devs, and deployed a fix before staging sign-off.",
                category="Behavioral & Culture",
                source_doc="Master_QA_Document.docx",
                tags=["behavioral", "bug", "challenge", "critical"],
                is_sensitive_declaration=False
            )
        ]
        db.add_all(qa_items)
        db.commit()
        print("[Seed] Seeded Consolidated Q&A Knowledge Base.")
        
    # 4. Seed initial verified jobs so the user can immediately test matching and application workflow!
    if db.query(Job).count() == 0:
        c_stripe = db.query(Company).filter(Company.name == "Stripe").first()
        c_netflix = db.query(Company).filter(Company.name == "Netflix").first()
        c_openai = db.query(Company).filter(Company.name == "OpenAI").first()
        
        jobs = [
            Job(
                company_id=c_stripe.id if c_stripe else 1,
                ats_job_id="stripe-sdet-playwright-01",
                title="Senior Software Engineer in Test - Playwright & Web Infrastructure",
                location="Remote - US / Global",
                department="Engineering - Quality & Infrastructure",
                employment_type="Full-time",
                url="https://boards.greenhouse.io/stripe/jobs/sdet-playwright-01",
                description="We are seeking an experienced SDET to design and scale our Playwright test automation framework. You will partner with web engineering to create high-reliability UI and API automated suites using TypeScript/Java, build Dockerized CI/CD test pipelines in GitHub Actions, and ensure flawless developer tooling.",
                salary_range="$150,000 - $185,000",
                hash_id="seed_stripe_sdet_01",
                status="active"
            ),
            Job(
                company_id=c_netflix.id if c_netflix else 2,
                ats_job_id="netflix-qa-automation-02",
                title="Software Development Engineer in Test (SDET) - Core Platforms",
                location="Los Gatos, CA / Remote",
                department="Core Quality Engineering",
                employment_type="Full-time",
                url="https://jobs.lever.co/netflix/sdet-core-02",
                description="Netflix is looking for an SDET to drive automated testing across our backend microservices and streaming clients. Key requirements: expertise in Java, REST Assured, Selenium/Playwright, TestNG, Docker, and distributed systems validation.",
                salary_range="$160,000 - $200,000",
                hash_id="seed_netflix_sdet_02",
                status="active"
            ),
            Job(
                company_id=c_openai.id if c_openai else 3,
                ats_job_id="openai-eval-sdet-03",
                title="Quality & Test Automation Engineer - Systems Reliability",
                location="San Francisco, CA / Remote",
                department="Applied AI & Systems",
                employment_type="Full-time",
                url="https://jobs.ashbyhq.com/openai/eval-sdet-03",
                description="Join OpenAI to build rigorous test automation frameworks for web applications, inference APIs, and evaluation harnesses. Requirements: strong coding in Python or TypeScript, experience with automated testing tools (Playwright/Selenium), and CI/CD pipelines.",
                salary_range="$170,000 - $220,000",
                hash_id="seed_openai_sdet_03",
                status="active"
            )
        ]
        db.add_all(jobs)
        db.commit()
        print("[Seed] Seeded sample active jobs.")
        
        # Run matching on these jobs
        from backend.agents.matching_agent.matching_service import MatchingAgent
        matcher = MatchingAgent(db)
        matcher.match_all_unmatched_jobs()
        print("[Seed] Evaluated and matched seed jobs against Master Resume.")
