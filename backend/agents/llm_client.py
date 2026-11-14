import os
import json
from typing import Dict, Any, Optional, List
import httpx
from config.settings import settings

class GeminiAIClient:
    """
    Client for Google Gemini API.
    Provides structured LLM intelligence for the 4 agents:
    - Agent 1: Deep JD parsing from unstructured HTML
    - Agent 2: Deep semantic matching & reasoning
    - Agent 3: Synthesis of behavioral & situational answers from verified Q&A
    - Agent 4: Resume summary tailoring & keyword elevation
    
    If no GEMINI_API_KEY is provided, it gracefully delegates to the local heuristic engine.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.model = "gemini-2.5-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        
    @property
    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 10)
        
    async def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
        if not self.is_available:
            return None
            
        endpoint = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        
        payload: Dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 2048
            }
        }
        
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(endpoint, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
                else:
                    print(f"[GeminiAIClient] API returned status {response.status_code}: {response.text[:120]}")
            except Exception as e:
                print(f"[GeminiAIClient] Request error: {e}")
                
        return None

    async def analyze_job_match(self, job_title: str, job_desc: str, resume_skills: List[str], resume_exp: str) -> Optional[Dict[str, Any]]:
        """Uses Gemini to evaluate job relevance with structured reasoning."""
        if not self.is_available:
            return None
            
        system_prompt = (
            "You are an expert SDET and Technical Recruiter evaluating candidate-job alignment. "
            "Output valid JSON ONLY with keys: match_score (integer 0-100), technical_score (0-100), "
            "matched_skills (list of strings), missing_skills (list of strings), reasoning (2-3 sentences)."
        )
        
        user_prompt = f"""
Candidate Verified Skills: {', '.join(resume_skills)}
Candidate Experience: {resume_exp}

Job Title: {job_title}
Job Description: {job_desc[:3000]}
"""
        raw_text = await self.generate_text(user_prompt, system_prompt)
        if raw_text:
            try:
                # Clean code fences if any
                clean_json = raw_text.strip().lstrip("```json").rstrip("```").strip()
                return json.loads(clean_json)
            except Exception:
                pass
        return None

    async def draft_application_answer(self, question: str, kb_context: str, resume_context: str) -> Optional[str]:
        """Synthesizes high-fidelity application answers grounded strictly in candidate verified data."""
        if not self.is_available:
            return None
            
        system_prompt = (
            "You are an AI Application Assistant writing tailored job application answers for Naga Teja Arepalli. "
            "CRITICAL RULE: You must ONLY use facts from the candidate's verified Q&A knowledge base and resume. "
            "NEVER invent, exaggerate, or fabricate facts, figures, tools, or dates. Keep responses professional, direct, and persuasive."
        )
        
        user_prompt = f"""
Application Question: {question}

Candidate Verified Q&A Knowledge Context:
{kb_context}

Candidate Resume Summary:
{resume_context}

Write a concise, professional answer (2-4 sentences) addressing the question.
"""
        return await self.generate_text(user_prompt, system_prompt)

gemini_client = GeminiAIClient()
