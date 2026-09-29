import time
import json
import uuid
from typing import List, Dict, Any, Optional

from backend.retrieval.vector_store import get_vector_store
from backend.ai.provider_manager import get_provider_manager
from backend.storage.database import get_db, record_audit

class RAGEngine:
    """
    On-device Retrieval-Augmented Generation (RAG) engine.
    Fetches grounded semantic context from local vector store and sends to active AI Provider.
    """
    def __init__(self):
        self.vector_store = get_vector_store()
        self.provider_manager = get_provider_manager()

    def query(self, user_query: str, doc_id: Optional[str] = None, top_k: int = 4, session_id: str = "default") -> Dict[str, Any]:
        start_time = time.time()
        record_audit("rag_query", target=doc_id or "all_documents", details=f"Query: {user_query}")

        # 1. Retrieve top-k context chunks from local vector store
        context_chunks = self.vector_store.search(user_query, top_k=top_k, filter_doc_id=doc_id)

        # 2. Query active provider
        provider = self.provider_manager.get_active_provider()
        response = provider.generate(user_query, context_chunks)

        total_latency = (time.time() - start_time) * 1000
        response["total_pipeline_latency_ms"] = round(total_latency, 2)

        # 3. Save to chat history table in SQLite
        conn = get_db()
        cursor = conn.cursor()
        chat_id = str(uuid.uuid4())
        citations_json = json.dumps(response.get("citations", []))
        
        # Save user message
        cursor.execute("""
            INSERT INTO chat_history (id, session_id, doc_id, role, message, citations_json, latency_ms, created_at)
            VALUES (?, ?, ?, 'user', ?, NULL, 0, ?)
        """, (str(uuid.uuid4()), session_id, doc_id, user_query, time.time() - 0.1))

        # Save assistant message
        cursor.execute("""
            INSERT INTO chat_history (id, session_id, doc_id, role, message, citations_json, latency_ms, tokens_used, created_at)
            VALUES (?, ?, ?, 'assistant', ?, ?, ?, ?, ?)
        """, (chat_id, session_id, doc_id, response.get("answer", ""), citations_json, total_latency, response.get("tokens_generated", 0), time.time()))
        conn.commit()

        response["message_id"] = chat_id
        return response

_rag_instance = None
def get_rag_engine() -> RAGEngine:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGEngine()
    return _rag_instance
