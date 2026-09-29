import time
from typing import Optional, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.retrieval.vector_store import get_vector_store
from backend.storage.database import record_audit, record_performance

router = APIRouter(prefix="/api/search", tags=["search"])

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 6
    doc_id: Optional[str] = None

@router.post("")
def semantic_search(request: SearchRequest):
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")

    start_time = time.time()
    vector_store = get_vector_store()
    results = vector_store.search(
        query=request.query.strip(),
        top_k=request.top_k or 6,
        filter_doc_id=request.doc_id
    )

    elapsed_ms = (time.time() - start_time) * 1000
    record_audit("semantic_search", details=f"Query: {request.query[:50]}, Results: {len(results)}")
    record_performance("semantic_search", "Local-Vector-Engine", "Vector Dot-Product", "CPU/NPU Matrix SIMD", elapsed_ms)

    return {
        "query": request.query,
        "total_results": len(results),
        "search_latency_ms": round(elapsed_ms, 2),
        "results": results
    }
