import time
import json
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pydantic import BaseModel

from backend.storage.database import get_db, record_audit, record_performance
from backend.storage.file_store import save_uploaded_file, delete_stored_file
from backend.ingestion.document_parser import DocumentParser
from backend.ingestion.chunker import chunk_document_pages
from backend.retrieval.vector_store import get_vector_store
from backend.ai.provider_manager import get_provider_manager

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    start_time = time.time()
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file provided.")

        # 1. Save locally with sanitization and validation
        doc_id, filename, file_path, file_size = save_uploaded_file(file.filename, content)

        # 2. Parse text locally
        pages, page_count, doc_type = DocumentParser.parse(file_path, filename)
        if not pages or all(not p.get("text", "").strip() for p in pages):
            raise HTTPException(status_code=400, detail="Could not extract text from file. Please ensure it contains readable text.")

        # 3. Chunk text locally
        chunks = chunk_document_pages(doc_id, pages)

        # 4. Insert into DB
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO documents (id, filename, file_type, file_size, file_path, page_count, chunk_count, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'indexed', ?, ?)
        """, (doc_id, filename, doc_type, file_size, file_path, page_count, len(chunks), time.time(), time.time()))
        conn.commit()

        # 5. Embed and store in vector store
        vector_store = get_vector_store()
        vector_store.add_chunks(doc_id, chunks)

        # 6. Generate initial quick summary
        all_text = " ".join([p.get("text", "") for p in pages])
        provider = get_provider_manager().get_active_provider()
        summary_result = provider.summarize(all_text[:4000], summary_type="comprehensive")

        cursor.execute("UPDATE documents SET summary_json = ? WHERE id = ?", (json.dumps(summary_result), doc_id))
        conn.commit()

        elapsed_ms = (time.time() - start_time) * 1000
        record_audit("document_ingest", target=filename, details=f"Pages: {page_count}, Chunks: {len(chunks)}, Size: {file_size}B")
        record_performance("document_ingest", "Local-Ingestion-Pipeline", "Local PyMuPDF/VectorEngine", "Local CPU/Memory", elapsed_ms)

        return {
            "id": doc_id,
            "filename": filename,
            "file_type": doc_type,
            "file_size": file_size,
            "page_count": page_count,
            "chunk_count": len(chunks),
            "status": "indexed",
            "ingestion_latency_ms": round(elapsed_ms, 2),
            "summary": summary_result
        }
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.get("")
def list_documents():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, file_type, file_size, page_count, chunk_count, status, summary_json, created_at FROM documents ORDER BY created_at DESC")
    rows = cursor.fetchall()
    
    docs = []
    for r in rows:
        summary_data = None
        if r["summary_json"]:
            try:
                summary_data = json.loads(r["summary_json"])
            except Exception:
                pass
        docs.append({
            "id": r["id"],
            "filename": r["filename"],
            "file_type": r["file_type"],
            "file_size": r["file_size"],
            "page_count": r["page_count"],
            "chunk_count": r["chunk_count"],
            "status": r["status"],
            "summary": summary_data,
            "created_at": r["created_at"]
        })
    return docs

@router.get("/{doc_id}")
def get_document(doc_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")

    summary_data = None
    if row["summary_json"]:
        try:
            summary_data = json.loads(row["summary_json"])
        except Exception:
            pass

    return {
        "id": row["id"],
        "filename": row["filename"],
        "file_type": row["file_type"],
        "file_size": row["file_size"],
        "page_count": row["page_count"],
        "chunk_count": row["chunk_count"],
        "status": row["status"],
        "summary": summary_data,
        "created_at": row["created_at"],
        "updated_at": row["updated_at"]
    }

@router.get("/{doc_id}/chunks")
def get_document_chunks(doc_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, chunk_index, page_number, content, token_count FROM chunks WHERE doc_id = ? ORDER BY chunk_index ASC", (doc_id,))
    rows = cursor.fetchall()
    return [{
        "id": r["id"],
        "chunk_index": r["chunk_index"],
        "page_number": r["page_number"],
        "content": r["content"],
        "token_count": r["token_count"]
    } for r in rows]

@router.delete("/{doc_id}")
def delete_document(doc_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT file_path, filename FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = row["file_path"]
    filename = row["filename"]

    # Delete physical file
    delete_stored_file(file_path)

    # Delete from DB and vector index
    vector_store = get_vector_store()
    vector_store.delete_document(doc_id)

    record_audit("document_delete", target=filename, details=f"Removed document {doc_id}")
    return {"success": True, "message": f"Document '{filename}' deleted."}
