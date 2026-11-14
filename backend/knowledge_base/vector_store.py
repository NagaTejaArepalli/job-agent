import math
import re
from typing import List, Dict, Any, Tuple

INTENT_SYNONYMS = {
    "ctc": ["salary", "compensation", "pay", "remuneration", "package", "earnings", "ctc"],
    "salary": ["ctc", "compensation", "pay", "remuneration", "package"],
    "compensation": ["salary", "ctc", "pay", "remuneration", "package"],
    "notice": ["availability", "join", "start", "timeframe", "timeline", "notice period"],
    "join": ["notice", "availability", "start date", "how soon"],
    "automation": ["testing", "test", "selenium", "playwright", "cypress", "framework"],
    "api": ["rest", "assured", "postman", "endpoints", "microservices", "web services", "http"],
    "sponsorship": ["visa", "work authorization", "authorized", "legal", "citizen", "permanent resident"],
    "relocation": ["relocate", "remote", "onsite", "hybrid", "travel"]
}

class SemanticKnowledgeRetriever:
    """
    Semantic knowledge retrieval engine.
    Matches application questions to Q&A knowledge items by meaning, intent,
    and semantic token similarity.
    """
    
    @classmethod
    def _tokenize(cls, text: str) -> List[str]:
        # Lowercase, clean punctuation, tokenize
        tokens = re.findall(r"\b[a-zA-Z0-9_+#.-]+\b", text.lower())
        stop_words = {"what", "is", "your", "the", "a", "an", "and", "or", "in", "for", "to", "of", "do", "you", "have", "can", "how", "please", "describe"}
        return [t for t in tokens if t not in stop_words]

    @classmethod
    def _expand_synonyms(cls, tokens: List[str]) -> List[str]:
        expanded = list(tokens)
        for t in tokens:
            for key, syns in INTENT_SYNONYMS.items():
                if key == t or t in syns:
                    expanded.extend(syns[:3])
        return list(set(expanded))

    @classmethod
    def _compute_similarity(cls, query_tokens: List[str], target_text: str, target_category: str) -> float:
        target_tokens = cls._tokenize(target_text)
        if not target_tokens or not query_tokens:
            return 0.0
            
        target_expanded = cls._expand_synonyms(target_tokens)
        query_expanded = cls._expand_synonyms(query_tokens)
        
        # Jaccard / Cosine blend
        set_q = set(query_expanded)
        set_t = set(target_expanded)
        
        intersection = set_q.intersection(set_t)
        if not intersection:
            return 0.0
            
        overlap_score = len(intersection) / math.sqrt(len(set_q) * len(set_t))
        
        # Bonus for category alignment
        cat_tokens = cls._tokenize(target_category)
        if any(ct in set_q for ct in cat_tokens):
            overlap_score = min(1.0, overlap_score + 0.25)
            
        # Bonus if key direct nouns match
        for q in query_tokens:
            if q in target_tokens:
                overlap_score = min(1.0, overlap_score + 0.15)
                
        return round(overlap_score, 3)

    @classmethod
    def find_best_answer(cls, question: str, qa_items: List[Dict[str, Any]], threshold: float = 0.45) -> Dict[str, Any]:
        """
        Finds the most relevant answer for a given application question.
        Returns matched item, confidence score, and flag if user input is needed.
        """
        query_tokens = cls._tokenize(question)
        if not query_tokens or not qa_items:
            return {
                "matched": False,
                "confidence": 0.0,
                "answer": None,
                "question": question,
                "needs_user_input": True,
                "reason": "No knowledge base items available or empty question"
            }
            
        ranked = []
        for item in qa_items:
            q_text = item.get("question", "")
            ans_text = item.get("answer", "")
            cat = item.get("category", "")
            
            # Match against question + tags + category
            q_score = cls._compute_similarity(query_tokens, q_text, cat)
            # Secondary match against answer text
            ans_score = cls._compute_similarity(query_tokens, ans_text, cat) * 0.7
            
            combined_score = max(q_score, ans_score)
            ranked.append((combined_score, item))
            
        ranked.sort(key=lambda x: x[0], reverse=True)
        best_score, best_item = ranked[0] if ranked else (0.0, None)
        
        if not best_item or best_score < threshold:
            return {
                "matched": False,
                "confidence": best_score,
                "answer": None,
                "question": question,
                "category": "Unknown",
                "needs_user_input": True,
                "reason": f"No high-confidence answer found in knowledge base (Best match: {int(best_score*100)}%)"
            }
            
        is_sensitive = best_item.get("is_sensitive_declaration", False)
        
        return {
            "matched": True,
            "confidence": best_score,
            "matched_question": best_item.get("question"),
            "answer": best_item.get("answer"),
            "category": best_item.get("category"),
            "source_doc": best_item.get("source_doc"),
            "is_sensitive_declaration": is_sensitive,
            "needs_user_input": is_sensitive, # Always require user input for sensitive declarations!
            "reason": "Requires personal legal declaration sign-off" if is_sensitive else "Retrieved from Knowledge Base"
        }
