import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import docx
from pypdf import PdfReader

CATEGORIES = {
    "Compensation & CTC": [
        "ctc", "salary", "compensation", "remuneration", "package", "expected ctc", "current ctc", "base pay", "bonus"
    ],
    "Notice Period & Availability": [
        "notice", "availability", "how soon", "joining date", "start date", "can you join", "notice period", "buyout"
    ],
    "Automation & SDET": [
        "automation", "playwright", "selenium", "cypress", "appium", "test automation", "sdet", "ui automation", "bdd", "cucumber"
    ],
    "API Testing & Tools": [
        "api", "rest assured", "postman", "soap", "swagger", "http", "api testing", "endpoint", "graphql"
    ],
    "Frameworks & CI/CD": [
        "framework", "ci/cd", "jenkins", "github actions", "gitlab", "docker", "pipeline", "maven", "gradle", "testng", "junit"
    ],
    "Work Authorization & Visa": [
        "visa", "work authorization", "citizenship", "sponsorship", "require sponsorship", "legally authorized", "h1b", "greencard"
    ],
    "Behavioral & Culture": [
        "conflict", "challenge", "strength", "weakness", "leadership", "teamwork", "proud of", "tell me about a time", "situation"
    ],
    "Personal & Contact": [
        "name", "email", "phone", "linkedin", "github", "portfolio", "address", "city", "location", "residence"
    ]
}

SENSITIVE_KEYWORDS = [
    "felony", "criminal", "misdemeanor", "convicted", "background check",
    "drug test", "non-compete", "nda", "legal agreement", "declaration",
    "consent to terms", "swear", "under penalty of perjury", "disability", "veteran status"
]

class QAExtractor:
    """
    Extracts structured Question & Answer pairs from Word documents, PDFs, or text files.
    Identifies question intent, categorizes into domains, and flags sensitive declarations.
    """
    
    @classmethod
    def extract_from_file(cls, file_path: str) -> List[Dict[str, Any]]:
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext in [".docx", ".doc"]:
            return cls.extract_from_docx(file_path)
        elif ext == ".pdf":
            return cls.extract_from_pdf(file_path)
        else:
            return cls.extract_from_text_file(file_path)
            
    @classmethod
    def extract_from_docx(cls, file_path: str) -> List[Dict[str, Any]]:
        doc = docx.Document(file_path)
        qa_pairs = []
        
        # 1. Check tables first (many Q&A docs use tables: Col 0 = Question, Col 1 = Answer)
        for table in doc.tables:
            for row in table.rows:
                cells = [c.text.strip() for c in row.cells]
                if len(cells) >= 2 and cells[0] and cells[1]:
                    # Exclude header row if matches 'Question' / 'Answer'
                    if cells[0].lower() in ["question", "q", "topic"] and cells[1].lower() in ["answer", "a", "response"]:
                        continue
                    qa_pairs.append(cls._build_qa_item(cells[0], cells[1], Path(file_path).name))
                    
        # 2. Check paragraphs
        lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        qa_from_text = cls._parse_lines(lines, Path(file_path).name)
        qa_pairs.extend(qa_from_text)
        
        return cls._deduplicate_pairs(qa_pairs)
        
    @classmethod
    def extract_from_pdf(cls, file_path: str) -> List[Dict[str, Any]]:
        reader = PdfReader(file_path)
        lines = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                for line in text.split("\n"):
                    clean = line.strip()
                    if clean:
                        lines.append(clean)
                        
        return cls._parse_lines(lines, Path(file_path).name)
        
    @classmethod
    def extract_from_text_file(cls, file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        return cls._parse_lines(lines, Path(file_path).name)

    @classmethod
    def _parse_lines(cls, lines: List[str], source_name: str) -> List[Dict[str, Any]]:
        qa_pairs: List[Dict[str, Any]] = []
        current_q: Optional[str] = None
        current_a_parts: List[str] = []
        
        q_pattern = re.compile(r"^(?:Q\d*[:.]|\d+[\).]|Question\s*\d*[:.]|\?)(.*)$", re.IGNORECASE)
        a_pattern = re.compile(r"^(?:A\d*[:.]|Answer\s*\d*[:.]|Ans[:.])(.*)$", re.IGNORECASE)
        
        for line in lines:
            # Check if this line is explicitly an Answer marker
            a_match = a_pattern.match(line)
            if a_match:
                if current_q:
                    ans_text = a_match.group(1).strip()
                    if ans_text:
                        current_a_parts.append(ans_text)
                continue
                
            # Check if this line is a question
            q_match = q_pattern.match(line)
            is_question = bool(q_match) or line.endswith("?")
            
            if is_question:
                # Save previous pair if exists
                if current_q and current_a_parts:
                    qa_pairs.append(cls._build_qa_item(current_q, "\n".join(current_a_parts), source_name))
                
                # Start new question
                current_q = q_match.group(1).strip() if q_match else line
                if not current_q and q_match:
                    current_q = line
                current_a_parts = []
            else:
                if current_q:
                    current_a_parts.append(line)
                elif line.endswith(":") and len(line) < 100:
                    # Possible question heading
                    current_q = line[:-1]
                    current_a_parts = []
                    
        # Add final pair
        if current_q and current_a_parts:
            qa_pairs.append(cls._build_qa_item(current_q, "\n".join(current_a_parts), source_name))
            
        return cls._deduplicate_pairs(qa_pairs)
        
    @classmethod
    def _categorize(cls, question: str, answer: str) -> str:
        text = f"{question} {answer}".lower()
        for cat, keywords in CATEGORIES.items():
            if any(kw in text for kw in keywords):
                return cat
        return "General"
        
    @classmethod
    def _is_sensitive(cls, question: str) -> bool:
        q_lower = question.lower()
        return any(term in q_lower for term in SENSITIVE_KEYWORDS)
        
    @classmethod
    def _build_qa_item(cls, question: str, answer: str, source_name: str) -> Dict[str, Any]:
        clean_q = question.strip().lstrip("0123456789.-) ").strip()
        clean_a = answer.strip()
        category = cls._categorize(clean_q, clean_a)
        is_sensitive = cls._is_sensitive(clean_q)
        
        # Tags
        tags = []
        for cat, kw_list in CATEGORIES.items():
            for kw in kw_list:
                if kw in clean_q.lower() or kw in clean_a.lower():
                    tags.append(kw)
                    
        return {
            "question": clean_q,
            "answer": clean_a,
            "category": category,
            "source_doc": source_name,
            "tags": list(set(tags)),
            "is_sensitive_declaration": is_sensitive,
            "needs_user_confirmation": is_sensitive
        }
        
    @classmethod
    def _deduplicate_pairs(cls, pairs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = {}
        for p in pairs:
            norm_q = re.sub(r"[^a-zA-Z0-9]", "", p["question"].lower())
            if norm_q and (norm_q not in seen or len(p["answer"]) > len(seen[norm_q]["answer"])):
                seen[norm_q] = p
        return list(seen.values())
