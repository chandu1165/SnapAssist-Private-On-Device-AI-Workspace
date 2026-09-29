import json
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.retrieval.rag_engine import get_rag_engine
from backend.storage.database import get_db, record_audit

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    query: str
    doc_id: Optional[str] = None
    top_k: Optional[int] = 4
    session_id: Optional[str] = "default"

@router.post("")
def chat_with_docs(request: ChatRequest):
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    rag = get_rag_engine()
    result = rag.query(
        user_query=request.query.strip(),
        doc_id=request.doc_id,
        top_k=request.top_k or 4,
        session_id=request.session_id or "default"
    )
    return result

@router.get("/history")
def get_chat_history(session_id: str = "default", doc_id: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()
    
    if doc_id:
        cursor.execute("""
            SELECT id, session_id, doc_id, role, message, citations_json, latency_ms, tokens_used, created_at
            FROM chat_history
            WHERE session_id = ? AND doc_id = ?
            ORDER BY created_at ASC
        """, (session_id, doc_id))
    else:
        cursor.execute("""
            SELECT id, session_id, doc_id, role, message, citations_json, latency_ms, tokens_used, created_at
            FROM chat_history
            WHERE session_id = ?
            ORDER BY created_at ASC
        """, (session_id,))
        
    rows = cursor.fetchall()
    messages = []
    for r in rows:
        citations = []
        if r["citations_json"]:
            try:
                citations = json.loads(r["citations_json"])
            except Exception:
                pass
        messages.append({
            "id": r["id"],
            "session_id": r["session_id"],
            "doc_id": r["doc_id"],
            "role": r["role"],
            "message": r["message"],
            "citations": citations,
            "latency_ms": r["latency_ms"],
            "tokens_used": r["tokens_used"],
            "created_at": r["created_at"]
        })
    return messages

@router.delete("/history")
def clear_chat_history(session_id: str = "default"):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
    conn.commit()
    record_audit("clear_chat_history", target=session_id, details="Conversation history cleared")
    return {"success": True, "message": "Chat history cleared."}
