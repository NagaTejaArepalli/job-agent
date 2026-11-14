from sqlalchemy.orm import Session
from backend.database.models import Company, MasterResume, QAKnowledgeItem, Job, JobMatch
from config.settings import settings
import docx

def create_master_resume_docx(output_path: str, data: dict):
    doc = docx.Document()
    
    # Header
    h1 = doc.add_heading(data["name"], level=1)
    doc.add_paragraph(f"{data['email']} | {data['phone']} | {data['location']}\nLinkedIn: {data['linkedin']} | Portfolio: {data['portfolio']} | GitHub: {data['github']}")
    
    # Summary
    doc.add_heading("Professional Summary", level=2)
    doc.add_paragraph(data["summary"])
    
    # Skills
    doc.add_heading("Technical Skills", level=2)
    for cat, sk_list in data["categorized_skills"].items():
        doc.add_paragraph(f"• {cat}: {', '.join(sk_list)}")
        
    # Experience
    doc.add_heading("Professional Experience", level=2)
    for exp in data["experience_records"]:
        p = doc.add_paragraph()
        p.add_run(f"{exp['company']} – {exp['role']} ({exp['dates']}) - {exp['location']}\n").bold = True
        for b in exp["bullets"]:
            doc.add_paragraph(f"• {b}")
            
    # Certifications
    doc.add_heading("Certifications", level=2)
    for cert in data["certifications"]:
        doc.add_paragraph(f"• {cert}")
        
    # Education
    doc.add_heading("Education", level=2)
    doc.add_paragraph(data["education"])
    
    doc.save(output_path)

def seed_initial_data(db: Session):
    # 1. Seed Company Configurations from target_companies.json (excluding current/past employers: Infor, Accenture)
    import json
    from backend.career_connectors.registry import detect_ats_provider
    
    EXCLUDED_COMPANIES = ["infor", "accenture", "accenture in india"]
    
    # Clean up any existing Infor or Accenture records from DB
    for exc in EXCLUDED_COMPANIES:
        exc_comps = db.query(Company).filter(Company.name.ilike(f"%{exc}%")).all()
        for ec in exc_comps:
            db.delete(ec)
    db.commit()
    
    target_file = settings.COMPANY_CONFIG_DIR / "target_companies.json"
    if target_file.exists():
        with open(target_file, "r", encoding="utf-8") as f:
            comps_data = json.load(f)
            
        for item in comps_data:
            if any(exc in item["name"].lower() for exc in EXCLUDED_COMPANIES):
                continue
                
            norm_name = item["name"].lower().strip()
            from backend.career_connectors.registry import KNOWN_ATS_MAPPINGS
            if norm_name in KNOWN_ATS_MAPPINGS:
                ats = KNOWN_ATS_MAPPINGS[norm_name][0]
                token = KNOWN_ATS_MAPPINGS[norm_name][1]
            else:
                ats = item.get("ats_provider") or detect_ats_provider(item["career_url"])
                token = item.get("board_token")

            existing = db.query(Company).filter(Company.name == item["name"]).first()
            if not existing:
                db.add(Company(
                    name=item["name"],
                    career_url=item["career_url"],
                    ats_provider=ats,
                    board_token=token,
                    keywords=item.get("keywords", "QA, SDET, Test Automation, Software Engineer in Test, Quality Engineer"),
                    location_preference=item.get("location_preference", "Bangalore, Hyderabad, Chennai, India / Remote"),
                    active=True
                ))
            else:
                existing.career_url = item["career_url"]
                existing.ats_provider = ats
                if token:
                    existing.board_token = token
        db.commit()
        print(f"[Seed] Successfully synced {len(comps_data)} official target company career portals.")

    # 2. Master Resume: Naga Teja Arepalli
    naga_resume_data = {
        "name": "Naga Teja Arepalli",
        "email": "naga.teja.are@gmail.com",
        "phone": "+91 9347763464",
        "location": "Bangalore, India",
        "linkedin": "https://www.linkedin.com/in/naga-teja-arepalli",
        "portfolio": "https://nagatejaarepalli.github.io/PortfolioPage/",
        "github": "https://github.com/NagaTejaArepalli/",
        "years_of_experience": 3.4,
        "summary": "Senior QA Automation Engineer & SDET specializing in enterprise test framework architecture, thread-safe parallel execution, and cutting-edge autonomous AI testing. Proven track record of pioneering Devin AI, KIRO AI, and Model Context Protocol (MCP) integrations across the QA lifecycle—scaling automated coverage to 85%+ across mission-critical enterprise workflows. Expertise in authoring large-scale BDD suites (375+ scenarios), deep API/web-service validation, automated failure triage, and proactive defect prevention across continuous delivery CI/CD pipelines.",
        "skills": [
            "Playwright", "Selenium WebDriver", "BDD (Cucumber)", "Thread-Safe Parallel Execution", 
            "Page Object Model (POM)", "TestNG", "Java", "Gherkin", "Devin AI", "KIRO AI", 
            "Model Context Protocol (MCP)", "Automated Root-Cause Diagnostics", "REST Assured", 
            "Microsoft Graph API", "Web Services/REST APIs", "GraphQL", "GitLab CI/CD", "Maven", "Git", "Jira"
        ],
        "categorized_skills": {
            "Automation & Architecture": ["Playwright", "Selenium WebDriver", "BDD (Cucumber)", "Thread-Safe Parallel Execution", "Page Object Model (POM)", "TestNG", "Java", "Gherkin"],
            "AI & Autonomous Testing": ["Devin AI", "KIRO AI", "Model Context Protocol (MCP – Playwright, GitLab, Jira)", "Automated Root-Cause Diagnostics"],
            "API & Integration": ["REST Assured", "Microsoft Graph API", "Web Services/REST APIs", "GraphQL"],
            "Tools & CI/CD": ["GitLab CI/CD", "Maven", "Git", "Jira"]
        },
        "experience_records": [
            {
                "company": "Infor",
                "role": "QA Engineer (SDET)",
                "dates": "Aug 2025 – Present",
                "location": "Bangalore, India",
                "bullets": [
                    "Pioneered autonomous feature testing using Devin AI across the complete lifecycle: parsing use cases, synthesizing manual test plans, conducting functional validation, and auto-generating robust automation scripts.",
                    "Architected a high-throughput, thread-safe parallel execution framework with per-request base configuration and isolated state management, substantially cutting CI/CD regression durations.",
                    "Authored and maintained 375+ high-rigor BDD scenarios across complex enterprise workflows (financial calculations, inventory planning, booking flows, and accounting), driving coverage over 85%.",
                    "Integrated Model Context Protocol (MCP) servers across Playwright, GitLab, and Jira, streamlining branch management, automated test runs, and issue triage.",
                    "Engineered custom Failure-Analyzer hooks to automatically parse runtime traces and stack logs, slashing manual triage overhead and accelerating root-cause remediation.",
                    "Hardened asynchronous email and report testing via Microsoft Graph API using regex matching and temporal run-scoping, eliminating test flakiness from stale artifacts.",
                    "Identified and resolved 27 pre-production defects (including 1 Blocker and 15+ Major issues) across revenue engines and integrations, directly safeguarding production release quality."
                ]
            },
            {
                "company": "Accenture in India",
                "role": "Packaged Application Development Analyst & Associate",
                "dates": "Jun 2023 – Jul 2025",
                "location": "Bangalore, India",
                "bullets": [
                    "Spearheaded automation for Wealth Management systems, ensuring strict transactional reliability for high-stakes financial operations.",
                    "Developed and scaled a Serenity-Cucumber BDD framework in Java; implemented POM and reusable utility wrappers to improve framework longevity.",
                    "Managed end-to-end defect lifecycles in Jira, significantly mitigating production leakage through rigorous cross-browser and cross-platform validation.",
                    "Automated dynamic test data generation and teardown pipelines, cutting manual prep overhead during high-velocity sprint cycles."
                ]
            }
        ],
        "experience_lines": [
            "Infor – QA Engineer (SDET) (Aug 2025 – Present): Pioneered autonomous feature testing using Devin AI; architected high-throughput thread-safe parallel execution framework; authored 375+ BDD scenarios (>85% coverage); integrated MCP servers across Playwright, GitLab, Jira; built Failure-Analyzer hooks and Microsoft Graph API async validation; resolved 27 pre-production defects.",
            "Accenture in India – Packaged Application Development Analyst & Associate (Jun 2023 – Jul 2025): Spearheaded Wealth Management automation; built Serenity-Cucumber BDD framework in Java with POM; automated test data generation pipelines in Jira/GitLab CI."
        ],
        "project_lines": [
            "Thread-Safe Parallel Execution Architecture: Led team of 3 engineers to architect isolated parallel execution framework reducing regression run times significantly.",
            "AI-Assisted Autonomous QA: Pioneered Devin AI & KIRO AI workflows for test case generation and MCP server integration with Playwright and Jira.",
            "Microsoft Graph API Testing Framework: Hardened asynchronous email and reporting validation eliminating stale test artifacts."
        ],
        "certifications": [
            "Generative AI Leader Certification",
            "GitHub Copilot",
            "Essentials Automation Certification - 2024 Automation Anywhere"
        ],
        "education": "B.Tech in Computer Science, Vel Tech Rangarajan Dr. Sagunthala R&D Institute, Chennai (2019 – 2023), First Class with Distinction, 9.43 CGPA",
        "education_lines": [
            "Bachelor of Technology (B.Tech) in Computer Science, Vel Tech Rangarajan Dr. Sagunthala R&D Institute (2019 – 2023) - 9.43 CGPA, First Class with Distinction"
        ]
    }

    # Generate master resume file on disk
    resume_doc_path = settings.MASTER_RESUME_DIR / "Naga_Teja_Arepalli_Master_Resume.docx"
    create_master_resume_docx(str(resume_doc_path), naga_resume_data)

    # Upsert Master Resume in DB
    existing_master = db.query(MasterResume).filter(MasterResume.is_active == True).first()
    if existing_master:
        existing_master.filename = "Naga_Teja_Arepalli_Master_Resume.docx"
        existing_master.file_path = str(resume_doc_path)
        existing_master.parsed_data = naga_resume_data
        existing_master.raw_text = str(naga_resume_data)
        db.commit()
    else:
        new_master = MasterResume(
            filename="Naga_Teja_Arepalli_Master_Resume.docx",
            file_path=str(resume_doc_path),
            raw_text=str(naga_resume_data),
            parsed_data=naga_resume_data,
            is_active=True
        )
        db.add(new_master)
        db.commit()
    print("[Seed] Master Resume configured for Naga Teja Arepalli.")

    # 3. Consolidated Q&A Knowledge Base
    qa_data = [
        # Compensation
        ("What is your current CTC?", "₹9.75 LPA (₹8.75 LPA Fixed + ₹1.00 LPA Variable)", "Compensation & CTC", ["ctc", "salary", "compensation", "current ctc"], False),
        ("What is your current fixed compensation?", "₹8.75 LPA", "Compensation & CTC", ["fixed ctc", "fixed salary", "base pay"], False),
        ("What is your current variable compensation?", "₹1.00 LPA", "Compensation & CTC", ["variable", "bonus", "incentive"], False),
        ("What is your expected CTC?", "₹14.00 – ₹15.00 LPA (Minimum acceptable: ₹13.5 LPA)", "Compensation & CTC", ["expected ctc", "expected salary", "salary expectation"], False),
        ("Are you open to negotiating the offered compensation?", "Yes, open to discussion based on overall scope, team, and benefits.", "Compensation & CTC", ["negotiate", "compensation"], False),
        ("Do you have any other offers in hand?", "No other offers in hand currently.", "Compensation & CTC", ["offers in hand", "competing offers"], False),
        
        # Notice & Availability
        ("What is your official notice period?", "60 days official notice period with Infor.", "Notice Period & Availability", ["notice period", "notice", "contractual notice"], False),
        ("How soon can you join? When can you start?", "Can join after completing the applicable 60-day notice period.", "Notice Period & Availability", ["availability", "how soon", "joining date", "start date"], False),
        ("Have you already resigned?", "No, I am currently employed with Infor and have not yet resigned.", "Notice Period & Availability", ["resigned", "serving notice"], False),
        ("Can your notice period be negotiated or shortened?", "No, notice period is standard 60 days.", "Notice Period & Availability", ["notice buyout", "shorten notice"], False),
        ("Can you join immediately?", "No, the standard 60-day notice period applies.", "Notice Period & Availability", ["immediate joiner"], False),
        ("Are you available for interviews during working hours?", "Yes, available for virtual or in-person interviews with prior schedule.", "Notice Period & Availability", ["interview availability"], False),
        
        # Automation & SDET
        ("Which automation tools have you used?", "Playwright and Selenium WebDriver with Java and TypeScript. Also experienced with Cucumber BDD, TestNG, and Serenity.", "Automation & SDET", ["playwright", "selenium", "automation tools", "cucumber", "testng"], False),
        ("Which programming language do you use for automation?", "Java is my primary language for test automation frameworks and BDD. Also experienced with Gherkin and TypeScript.", "Automation & SDET", ["programming language", "java", "coding"], False),
        ("Describe your automation testing experience.", "Over 3+ years of enterprise SDET experience architecting Playwright and Selenium WebDriver frameworks with BDD (Cucumber), TestNG, Page Object Model (POM), and thread-safe parallel execution. Scaled automated test coverage to 85%+ across 375+ scenarios.", "Automation & SDET", ["automation experience", "sdet", "framework architecture"], False),
        ("Have you built or architected automation frameworks?", "Yes. At Infor, architected a high-throughput thread-safe parallel execution framework with per-request base configuration. At Accenture, developed and scaled a Serenity-Cucumber BDD framework in Java with Page Object Model.", "Automation & SDET", ["framework design", "architected framework", "parallel execution"], False),
        ("Have you implemented parallel test execution?", "Yes. Architected thread-safe parallel test execution with isolated state management and per-request configuration, significantly reducing CI/CD regression durations. Led a team of 3 to implement this.", "Automation & SDET", ["parallel execution", "thread-safe", "parallel"], False),
        ("How many automated scenarios have you authored/maintained?", "Authored and maintained 375+ high-rigor BDD scenarios covering financial calculations, inventory planning, booking flows, and accounting.", "Automation & SDET", ["scenarios", "test suite size", "bdd scenarios"], False),
        ("What automation coverage have you achieved?", "Achieved over 85% automated test coverage across mission-critical enterprise workflows.", "Automation & SDET", ["test coverage", "automation coverage"], False),
        
        # AI-Assisted Testing
        ("Have you worked with AI-assisted testing or autonomous agents?", "Yes. Pioneered autonomous feature testing using Devin AI across the complete lifecycle (parsing use cases, synthesizing test plans, auto-generating automation scripts). Integrated Model Context Protocol (MCP) servers across Playwright, GitLab, and Jira.", "Automation & SDET", ["devin ai", "mcp", "model context protocol", "ai testing", "kiro ai"], False),
        ("Have you implemented automated failure analysis?", "Yes. Engineered custom Failure-Analyzer hooks to automatically parse runtime traces and stack logs, slashing manual failure triage overhead.", "Automation & SDET", ["failure analysis", "triage", "root cause"], False),
        
        # API Testing
        ("Which API testing technologies have you used?", "REST Assured, Microsoft Graph API, RESTful Web Services, and GraphQL. Experienced with request validation, JSON assertions, and auth token handling.", "API Testing & Tools", ["rest assured", "api testing", "microsoft graph api", "graphql"], False),
        ("Have you tested asynchronous APIs, emails, or reports?", "Yes. Hardened asynchronous email and report testing via Microsoft Graph API using regex matching and temporal run-scoping, preventing stale artifacts and flaky tests.", "API Testing & Tools", ["async api", "microsoft graph api", "email testing"], False),
        
        # CI/CD & DevOps
        ("Which CI/CD and source control tools have you used?", "GitLab CI/CD, Git, Maven, and Jira for end-to-end defect lifecycle and automated regression pipelines.", "Frameworks & CI/CD", ["gitlab ci", "maven", "git", "ci/cd"], False),
        
        # Work Authorization & Location
        ("Are you legally authorized to work in India?", "Yes, I am an Indian citizen fully authorized to work in India.", "Work Authorization & Visa", ["work authorization india", "authorized india"], False),
        ("Are you authorized to work in the country where this role is located?", "For India-based roles: Yes. For roles outside India: No, will require visa sponsorship.", "Work Authorization & Visa", ["work authorization", "visa", "eligibility"], True),
        ("Will you now or in the future require visa sponsorship?", "For India-based roles: No. For roles outside India: Yes, sponsorship required.", "Work Authorization & Visa", ["visa sponsorship", "sponsorship"], True),
        ("What is your citizenship?", "Indian.", "Work Authorization & Visa", ["citizenship", "nationality"], False),
        ("Where are you currently based?", "Bangalore, India.", "Personal & Contact", ["location", "city", "residence"], False),
        ("What are your preferred work locations?", "Bangalore, Hyderabad, Chennai (also willing to relocate within India).", "Personal & Contact", ["preferred location", "relocation"], False),
        ("Are you willing to relocate?", "Yes, willing to relocate within India (Bangalore, Hyderabad, Chennai).", "Personal & Contact", ["relocation", "relocate"], False),
        ("Are you comfortable with a hybrid work model?", "Yes, comfortable working from the office, hybrid, or remote.", "Personal & Contact", ["hybrid", "work from office", "remote"], False),
        
        # Education & Certifications
        ("What is your highest educational qualification?", "B.Tech in Computer Science from Vel Tech Rangarajan Dr. Sagunthala R&D Institute, Chennai (2019 – 2023), First Class with Distinction, 9.43 CGPA.", "Personal & Contact", ["degree", "education", "btech", "cgpa"], False),
        ("What is your CGPA?", "9.43 CGPA out of 10 (First Class with Distinction).", "Personal & Contact", ["cgpa", "grades", "percentage"], False),
        ("Do you hold any certifications?", "Generative AI Leader Certification, GitHub Copilot, and Essentials Automation Certification - 2024 (Automation Anywhere).", "Personal & Contact", ["certifications", "copilot", "generative ai"], False),
        
        # Behavioral & Leadership
        ("Have you led or mentored a team?", "Yes. For implementing the thread-safe parallel test execution framework, I led a team of 3 engineers to successfully deliver the initiative.", "Behavioral & Culture", ["leadership", "led team", "mentoring"], False),
        ("Tell me about yourself.", "I am a Senior QA Automation Engineer & SDET with 3+ years of experience in enterprise software quality engineering. I specialize in Playwright, Selenium, Java, BDD (Cucumber), REST Assured, and CI/CD pipelines, and have pioneered autonomous AI testing with Devin AI and Model Context Protocol (MCP). Previously worked on Wealth Management systems at Accenture and currently at Infor.", "Behavioral & Culture", ["tell me about yourself", "summary", "elevator pitch"], False),
        
        # Compliance & Company
        ("Who is your current employer and title?", "Infor – QA Engineer (SDET), since August 2025.", "Personal & Contact", ["current employer", "current title", "designation"], False),
        ("Who was your previous employer?", "Accenture in India – Packaged Application Development Analyst & Associate (June 2023 – July 2025).", "Personal & Contact", ["previous employer", "accenture"], False),
        ("Are you subject to any non-compete or conflict of interest?", "No non-compete agreements, non-solicitation restrictions, or conflicts of interest.", "Work Authorization & Visa", ["non-compete", "conflict of interest"], True),
        ("Can the employer conduct background verification?", "Yes, authorized for employment and educational background verification.", "Work Authorization & Visa", ["background check", "verification"], True)
    ]

    # Clear and repopulate Q&A items to ensure 100% freshness
    db.query(QAKnowledgeItem).delete()
    for q, a, cat, tags, is_sens in qa_data:
        item = QAKnowledgeItem(
            question=q,
            answer=a,
            category=cat,
            source_doc="Naga_Teja_Arepalli_Application_Report.pdf",
            tags=tags,
            is_sensitive_declaration=is_sens,
            needs_user_confirmation=is_sens
        )
        db.add(item)
    db.commit()
    print(f"[Seed] Seeded {len(qa_data)} verified Q&A Knowledge items for Naga Teja Arepalli.")

    # 4. Seed India-based active jobs for immediate testing
    if db.query(Job).count() == 0 or True: # refresh seed jobs to ensure strict India locations
        # Clean existing non-India or excluded employer jobs
        db.query(Job).delete()
        c_cred = db.query(Company).filter(Company.name == "CRED").first()
        c_razorpay = db.query(Company).filter(Company.name == "Razorpay").first()
        c_swiggy = db.query(Company).filter(Company.name == "Swiggy").first()
        c_flipkart = db.query(Company).filter(Company.name == "Flipkart").first()
        c_browserstack = db.query(Company).filter(Company.name == "BrowserStack").first()
        
        india_jobs = [
            Job(
                company_id=c_cred.id if c_cred else 1,
                ats_job_id="cred-sdet-blr-01",
                title="Senior SDET - Automation Architecture & Backend Quality",
                location="Bangalore, Karnataka, India",
                department="Core Infrastructure Quality",
                employment_type="Full-time",
                url="https://careers.cred.club/jobs/sdet-blr",
                description="CRED Bangalore is seeking a Senior SDET with deep expertise in Java/TypeScript, Playwright/Selenium, thread-safe parallel test execution, and REST Assured API automation.",
                salary_range="₹18,00,000 - ₹26,00,000",
                hash_id="seed_cred_blr_01",
                status="active"
            ),
            Job(
                company_id=c_razorpay.id if c_razorpay else 2,
                ats_job_id="rzp-sdet-playwright-02",
                title="Software Development Engineer in Test (SDET II) - Payments Platform",
                location="Bangalore, India",
                department="Core Payments Engineering",
                employment_type="Full-time",
                url="https://job-boards.greenhouse.io/razorpay/jobs/sdet2-blr",
                description="Razorpay Bangalore is hiring an SDET II with deep expertise in Java/TypeScript, Playwright/Selenium, BDD Cucumber, REST Assured API automation, and parallel test execution.",
                salary_range="₹16,00,000 - ₹22,00,000",
                hash_id="seed_rzp_blr_02",
                status="active"
            ),
            Job(
                company_id=c_swiggy.id if c_swiggy else 3,
                ats_job_id="swiggy-sdet-infra-03",
                title="Lead SDET - Automation Infrastructure & Microservices",
                location="Bangalore, India (Hybrid)",
                department="Supply & Delivery Engineering",
                employment_type="Full-time",
                url="https://careers.swiggy.com/jobs/sdet-infra-blr",
                description="Swiggy Bangalore is seeking an experienced SDET with strong Java, TestNG, Playwright/Selenium, thread-safe parallel architecture, and API regression testing.",
                salary_range="₹18,00,000 - ₹25,00,000",
                hash_id="seed_swiggy_blr_03",
                status="active"
            ),
            Job(
                company_id=c_flipkart.id if c_flipkart else 4,
                ats_job_id="fk-sdet-supplychain-04",
                title="Software Development Engineer in Test - Enterprise Workflows",
                location="Bangalore, India",
                department="Supply Chain Quality",
                employment_type="Full-time",
                url="https://www.flipkartcareers.com/jobs/sdet-supply-chain",
                description="Join Flipkart Bangalore to automate end-to-end booking, financial calculations, and inventory planning using Java, Cucumber BDD, and REST APIs.",
                salary_range="₹17,00,000 - ₹24,00,000",
                hash_id="seed_fk_blr_04",
                status="active"
            ),
            Job(
                company_id=c_browserstack.id if c_browserstack else 5,
                ats_job_id="bs-sdet-platform-05",
                title="Senior SDET - Cloud Test Platform & Autonomous Tools",
                location="Mumbai / Bangalore, India",
                department="Core Quality & Developer Tools",
                employment_type="Full-time",
                url="https://boards.greenhouse.io/browserstack/jobs/sdet-mumbai",
                description="BrowserStack is seeking an SDET in Mumbai/Bangalore with hands-on Playwright, Selenium, Java, AI-assisted testing (Devin/MCP), and GitLab CI/CD experience.",
                salary_range="₹18,00,000 - ₹26,00,000",
                hash_id="seed_bs_india_05",
                status="active"
            )
        ]
        db.add_all(india_jobs)
        db.commit()
        print(f"[Seed] Seeded {len(india_jobs)} verified India-exclusive job postings.")

    # 5. Re-evaluate jobs against Naga Teja's Master Resume
    from backend.agents.matching_agent.matching_service import MatchingAgent
    matcher = MatchingAgent(db)
    matcher.match_all_unmatched_jobs()
    print("[Seed] Successfully matched all India jobs against Naga Teja Arepalli's Master Resume.")
