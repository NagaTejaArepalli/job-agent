from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.database.models import QAKnowledgeItem
from backend.document_processor.qa_extractor import QAExtractor
from backend.knowledge_base.vector_store import SemanticKnowledgeRetriever
from config.settings import settings

router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])

class QAItemCreate(BaseModel):
    question: str
    answer: str
    category: Optional[str] = "General"
    tags: Optional[List[str]] = []
    is_sensitive_declaration: Optional[bool] = False

class QAItemResponse(BaseModel):
    id: int
    question: str
    answer: str
    category: str
    source_doc: Optional[str]
    tags: List[str]
    is_sensitive_declaration: bool
    needs_user_confirmation: bool
    times_used: int

class SemanticSearchQuery(BaseModel):
    query: str
    threshold: Optional[float] = 0.40

@router.get("", response_model=List[QAItemResponse])
def get_all_qa_items(category: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(QAKnowledgeItem)
    if category and category != "all":
        q = q.filter(QAKnowledgeItem.category == category)
    items = q.order_by(QAKnowledgeItem.category.asc(), QAKnowledgeItem.id.asc()).all()
    
    return [
        QAItemResponse(
            id=item.id,
            question=item.question,
            answer=item.answer,
            category=item.category,
            source_doc=item.source_doc,
            tags=item.tags or [],
            is_sensitive_declaration=item.is_sensitive_declaration or False,
            needs_user_confirmation=item.needs_user_confirmation or False,
            times_used=item.times_used or 0
        )
        for item in items
    ]

@router.post("/upload")
async def upload_qa_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Save file to knowledge_docs dir
    save_path = settings.KNOWLEDGE_DOCS_DIR / file.filename
    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)
        
    extracted_pairs = QAExtractor.extract_from_file(str(save_path))
    added_count = 0
    updated_count = 0
    
    for pair in extracted_pairs:
        existing = db.query(QAKnowledgeItem).filter(
            QAKnowledgeItem.question == pair["question"]
        ).first()
        
        if existing:
            existing.answer = pair["answer"]
            existing.category = pair["category"]
            existing.tags = pair["tags"]
            existing.source_doc = pair["source_doc"]
            existing.is_sensitive_declaration = pair["is_sensitive_declaration"]
            updated_count += 1
        else:
            item = QAKnowledgeItem(
                question=pair["question"],
                answer=pair["answer"],
                category=pair["category"],
                source_doc=pair["source_doc"],
                tags=pair["tags"],
                is_sensitive_declaration=pair["is_sensitive_declaration"],
                needs_user_confirmation=pair["needs_user_confirmation"]
            )
            db.add(item)
            added_count += 1
            
    db.commit()
    return {
        "status": "success",
        "filename": file.filename,
        "extracted_total": len(extracted_pairs),
        "added": added_count,
        "updated": updated_count
    }

@router.post("/item", response_model=QAItemResponse)
def add_qa_item(payload: QAItemCreate, db: Session = Depends(get_db)):
    item = QAKnowledgeItem(
        question=payload.question,
        answer=payload.answer,
        category=payload.category or "General",
        tags=payload.tags or [],
        is_sensitive_declaration=payload.is_sensitive_declaration or False,
        source_doc="Manual Entry"
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return QAItemResponse(
        id=item.id,
        question=item.question,
        answer=item.answer,
        category=item.category,
        source_doc=item.source_doc,
        tags=item.tags or [],
        is_sensitive_declaration=item.is_sensitive_declaration or False,
        needs_user_confirmation=item.needs_user_confirmation or False,
        times_used=0
    )

@router.put("/item/{item_id}", response_model=QAItemResponse)
def update_qa_item(item_id: int, payload: QAItemCreate, db: Session = Depends(get_db)):
    item = db.query(QAKnowledgeItem).filter(QAKnowledgeItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Q&A item not found")
        
    item.question = payload.question
    item.answer = payload.answer
    item.category = payload.category
    item.tags = payload.tags or []
    item.is_sensitive_declaration = payload.is_sensitive_declaration
    db.commit()
    db.refresh(item)
    return QAItemResponse(
        id=item.id,
        question=item.question,
        answer=item.answer,
        category=item.category,
        source_doc=item.source_doc,
        tags=item.tags or [],
        is_sensitive_declaration=item.is_sensitive_declaration,
        needs_user_confirmation=item.needs_user_confirmation,
        times_used=item.times_used
    )

@router.delete("/item/{item_id}")
def delete_qa_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(QAKnowledgeItem).filter(QAKnowledgeItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Q&A item not found")
    db.delete(item)
    db.commit()
    return {"status": "success", "message": "Q&A item deleted"}

@router.post("/query")
def semantic_query(payload: SemanticSearchQuery, db: Session = Depends(get_db)):
    items = db.query(QAKnowledgeItem).all()
    qa_list = [
        {
            "id": i.id,
            "question": i.question,
            "answer": i.answer,
            "category": i.category,
            "source_doc": i.source_doc,
            "is_sensitive_declaration": i.is_sensitive_declaration
        }
        for i in items
    ]
    result = SemanticKnowledgeRetriever.find_best_answer(
        question=payload.query,
        qa_items=qa_list,
        threshold=payload.threshold or 0.40
    )
    return result
