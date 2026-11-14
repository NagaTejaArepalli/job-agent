# AI Job Search & Application Agent (Everyday Automated Discovery)

An intelligent, multi-agent system that runs every day to discover verified job openings across company career portals (Greenhouse, Lever, Ashby, SmartRecruiters), matches requirements against your master profile, generates ATS-tailored resumes with **strict zero fabrication**, retrieves verified answers from your consolidated personal Q&A document, and automatically prepares application forms via browser automation with **mandatory human-in-the-loop review before submission**.

---

## 1. System Architecture

```
                          ┌───────────────────────────────────────────────┐
                          │    AI Job Search & Application Agent          │
                          │     Central Orchestration & Dashboard         │
                          └──────────────────────┬────────────────────────┘
                                                 │
         ┌───────────────────┬───────────────────┴───────────────────┬───────────────────┐
         ▼                   ▼                                       ▼                   ▼
┌──────────────────┐┌──────────────────┐                   ┌──────────────────┐┌──────────────────┐
│     Agent 1      ││     Agent 2      │                   │     Agent 3      ││     Agent 4      │
│  Job Discovery   ││   Job Matching   │                   │  Application     ││  Resume          │
│                  ││                  │                   │  Assistant       ││  Assistant       │
│ • ATS Connectors ││ • Resume Profile │                   │ • Q&A Retrieval  ││ • Master Resume  │
│ • Link Verifier  ││ • Skill Matching │                   │ • Form Mapping   ││ • Zero-Fab Tailor│
│ • Expired Detect ││ • Gap Analysis   │                   │ • Missing Flags  ││ • DOCX Export    │
└────────┬─────────┘└────────┬─────────┘                   └────────┬─────────┘└────────┬─────────┘
         │                   │                                      │                   │
         └───────────────────┴──────────────────┬───────────────────┴───────────────────┘
                                                │
                                                ▼
                              ┌───────────────────────────────────┐
                              │        Application Manager        │
                              │ • Playwright Form Filling         │
                              │ • Human Verification Checklist    │
                              │ • Manual Submission Protocol      │
                              └─────────────────┬─────────────────┘
                                                │
                                                ▼
                              ┌───────────────────────────────────┐
                              │  Central Database & Knowledge Base│
                              │  PostgreSQL / SQLite + Q&A Store  │
                              └───────────────────────────────────┘
```

---

## 2. Core Operational Principles

### 1. Consolidated Q&A Knowledge Base
- Upload your single Word (`.docx`) or PDF document containing all your questions and answers.
- Automatically extracts Q&A pairs, tags keywords, and categorizes into:
  - `Compensation & CTC`
  - `Notice Period & Availability`
  - `Automation & SDET`
  - `API Testing & Tools`
  - `Frameworks & CI/CD`
  - `Work Authorization & Visa`
  - `Behavioral & Culture`
- **Semantic Matching**: Matches questions by meaning rather than exact wording (e.g. *"What is your current remuneration?"* correctly maps to your compensation answer).
- **Declaration Flagging**: Questions requiring personal declarations (e.g., criminal background, non-compete, consent checkboxes) are flagged for your explicit sign-off rather than guessed.

### 2. Two-Tier Resume Architecture (Zero-Fabrication Guaranteed)
- **Master Resume**: Single source of truth containing your complete experience, projects, skills, education, and certifications.
- **Tailored Resumes**: Dynamically prioritized versions optimized for individual job descriptions (e.g. highlighting Playwright, Java, REST Assured for Playwright SDET roles).
- **Strict Factual Accuracy**: The agent only elevates, reorders, and highlights verified experiences already present in your master resume. It is architecturally prevented from inventing fake employers, dates, or unverified skills.

### 3. Human-Controlled Submission Protocol
- The browser automation (Playwright) navigates to the official application form, maps fields, fills contact information and custom questions, and attaches your tailored resume.
- **The agent strictly stops before clicking Submit.**
- A mandatory pre-submission checklist prompts you to personally review all fields, confirm consent checkboxes, and click the final "Submit Application" button.

---

## 3. Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Tailwind CSS v4, Lucide Icons, Vite |
| **Backend** | Python 3.14, FastAPI, Uvicorn, Pydantic v2 |
| **Database** | SQLite / PostgreSQL with SQLAlchemy ORM |
| **Browser Automation** | Playwright (headed / headless mode) |
| **ATS Integrations** | Greenhouse API, Lever API, Ashby API, SmartRecruiters API, Generic Scraper |
| **Document Processing** | python-docx, PyMuPDF, pypdf, openpyxl |
| **Daily Scheduler** | APScheduler (runs discovery & matching daily at 08:00 UTC) |
| **Reporting** | Excel (.xlsx), CSV, PDF |

---

## 4. Codebase Structure

```
CompanyCarrierSiteJobDiscovery/
├── backend/
│   ├── api/                      # REST API endpoints (companies, jobs, resumes, applications, kb, stats)
│   ├── agents/
│   │   ├── discovery_agent/      # Agent 1: ATS extraction, active link verification
│   │   ├── matching_agent/       # Agent 2: Technical & experience scoring, gap analysis
│   │   ├── application_agent/    # Agent 3: Q&A answer retrieval, form field preparation
│   │   └── resume_agent/         # Agent 4: Master resume parsing, zero-fabrication tailoring
│   ├── career_connectors/        # Greenhouse, Lever, Ashby, SmartRecruiters connectors
│   ├── browser_automation/       # Playwright browser automation
│   ├── document_processor/       # Word (.docx) & PDF Q&A and resume extractor
│   ├── knowledge_base/           # Semantic similarity retrieval engine
│   ├── database/                 # SQLAlchemy models, session, seed data
│   ├── scheduler/                # APScheduler daily runner & Excel reporting
│   └── main.py                   # FastAPI server entry point
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── JobDiscovery.jsx
│   │   │   ├── JobMatching.jsx
│   │   │   ├── ApplicationManager.jsx
│   │   │   ├── ResumeManager.jsx
│   │   │   └── KnowledgeBase.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
├── data/
│   ├── company_config/           # Saved companies
│   ├── master_resume/            # Master resume documents
│   ├── tailored_resumes/         # Generated tailored DOCX resumes
│   ├── knowledge_docs/           # Uploaded Q&A files
│   └── reports/                  # Generated Excel/CSV export reports
├── tests/
│   └── test_agents.py            # Pytest test suite for all agents
├── config/
│   └── settings.py               # Pydantic environment configuration
└── README.md
```

---

## 5. Quick Start Instructions

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Node.js 18+ and npm

### 1. Start the Backend API
From the root directory:
```bash
python -m uvicorn backend.main:app --port 8000 --reload
```
The backend initializes the database, seeds default companies (Stripe, Netflix, OpenAI, Spotify, Datadog), loads the candidate profile, indexes the default Q&A knowledge base, and starts the background daily scheduler.

### 2. Start the Frontend Dashboard
In a separate terminal:
```bash
cd frontend
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

*(Note: The backend also serves the built static frontend directly at [http://localhost:8000](http://localhost:8000) when `frontend/dist` is built via `npm run build`.)*

### 3. Run the Automated Tests
```bash
python -m pytest tests/ -v
```

---

## 6. Application Workflow (Day-to-Day Operation)

1. **Daily Discovery**: The agent crawls configured ATS boards every morning at 08:00 UTC (or instantly when you click *"Run Discovery Now"* on the Dashboard).
2. **Relevance Scoring**: Agent 2 scores each job against your master resume, generating technical overlap percentages, matched skills, and gap analysis.
3. **Tailored Resume Preparation**: Selecting a job generates an ATS-aligned resume emphasizing the job's key technologies (e.g. Playwright, Java, REST Assured).
4. **Answer Formulation**: Agent 3 queries your Q&A document to retrieve exact compensation details, notice period, and project answers. Any question requiring a legal declaration is highlighted for your input.
5. **Form Pre-Filling**: Click *"Fill Form in Browser"* to launch Playwright. It inputs your details, uploads the tailored resume, and opens the page for you.
6. **Manual Submission**: Complete any employer-specific legal checkboxes, inspect the pre-filled fields, and click **Submit**.
