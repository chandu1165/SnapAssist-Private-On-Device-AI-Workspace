import json
import time
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.storage.database import get_db, record_audit
from backend.ai.provider_manager import get_provider_manager

router = APIRouter(prefix="/api/summarize", tags=["summarize"])

class SummarizeRequest(BaseModel):
    summary_type: Optional[str] = "comprehensive"

@router.post("/{doc_id}")
def summarize_document(doc_id: str, request: Optional[SummarizeRequest] = None):
    summary_type = request.summary_type if request else "comprehensive"
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT filename, file_path FROM documents WHERE id = ?", (doc_id,))
    doc_row = cursor.fetchone()
    if not doc_row:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Retrieve all chunks for document
    cursor.execute("SELECT content FROM chunks WHERE doc_id = ? ORDER BY chunk_index ASC", (doc_id,))
    chunks = cursor.fetchall()
    if not chunks:
        raise HTTPException(status_code=400, detail="Document has no text content to summarize.")

    combined_text = " ".join([c["content"] for c in chunks])
    provider = get_provider_manager().get_active_provider()
    summary_result = provider.summarize(combined_text, summary_type=summary_type)

    # Cache summary in document record
    cursor.execute("UPDATE documents SET summary_json = ? WHERE id = ?", (json.dumps(summary_result), doc_id))
    conn.commit()

    record_audit("document_summarize", target=doc_row["filename"], details=f"Type: {summary_type}")
    return {
        "doc_id": doc_id,
        "filename": doc_row["filename"],
        "summary": summary_result
    }
