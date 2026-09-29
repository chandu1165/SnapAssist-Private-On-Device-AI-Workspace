import sqlite3
import numpy as np
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from backend.storage.database import get_db
from backend.ai.embedding_engine import get_embedding_engine

class LocalVectorStore:
    """
    Lightweight, high-performance on-device vector store.
    Uses numpy vectorized matrix dot-product for cosine similarity search.
    Requires no heavy external C++ binaries, runs seamlessly across Windows ARM64 and x86_64.
    """
    def __init__(self):
        self.embedding_engine = get_embedding_engine()
        # In-memory index cache
        self.chunk_ids: List[str] = []
        self.doc_ids: List[str] = []
        self.page_numbers: List[int] = []
        self.chunk_contents: List[str] = []
        self.embedding_matrix: Optional[np.ndarray] = None
        self._load_from_db()

    def _load_from_db(self):
        """Loads existing chunks and embeddings into memory for fast similarity search."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, doc_id, page_number, content, embedding_blob FROM chunks WHERE embedding_blob IS NOT NULL")
        rows = cursor.fetchall()

        if not rows:
            self.chunk_ids = []
            self.doc_ids = []
            self.page_numbers = []
            self.chunk_contents = []
            self.embedding_matrix = None
            return

        chunk_ids = []
        doc_ids = []
        pages = []
        contents = []
        vectors = []

        for row in rows:
            c_id, d_id, page, content, blob = row["id"], row["doc_id"], row["page_number"], row["content"], row["embedding_blob"]
            vec = np.frombuffer(blob, dtype=np.float32)
            if vec.shape[0] == self.embedding_engine.vector_dim:
                chunk_ids.append(c_id)
                doc_ids.append(d_id)
                pages.append(page)
                contents.append(content)
                vectors.append(vec)

        if vectors:
            self.chunk_ids = chunk_ids
            self.doc_ids = doc_ids
            self.page_numbers = pages
            self.chunk_contents = contents
            self.embedding_matrix = np.vstack(vectors)

    def add_chunks(self, doc_id: str, chunks: List[Any]):
        """
        Embeds chunks and persists them into the database and active memory index.
        """
        if not chunks:
            return

        conn = get_db()
        cursor = conn.cursor()

        texts = [c.content for c in chunks]
        embeddings = self.embedding_engine.embed_batch(texts)

        for i, c in enumerate(chunks):
            emb = embeddings[i]
            blob = emb.tobytes()
            cursor.execute("""
                INSERT OR REPLACE INTO chunks (id, doc_id, chunk_index, page_number, content, token_count, embedding_blob, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (c.id, c.doc_id, c.chunk_index, c.page_number, c.content, c.token_count, blob, time.time()))

        conn.commit()
        # Reload index cache
        self._load_from_db()

    def delete_document(self, doc_id: str):
        """Removes document and its chunks from DB and index."""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
        self._load_from_db()

    def search(self, query: str, top_k: int = 4, filter_doc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Performs semantic vector search using cosine similarity.
        """
        if self.embedding_matrix is None or len(self.chunk_ids) == 0:
            return []

        query_vec = self.embedding_engine.embed_text(query)
        # Vectorized cosine similarity
        similarities = np.dot(self.embedding_matrix, query_vec)

        # Filter indices if filter_doc_id provided
        if filter_doc_id:
            valid_indices = [i for i, d in enumerate(self.doc_ids) if d == filter_doc_id]
        else:
            valid_indices = list(range(len(self.chunk_ids)))

        if not valid_indices:
            return []

        sub_similarities = similarities[valid_indices]
        # Top-k indices
        top_sub_idx = np.argsort(sub_similarities)[::-1][:top_k]

        results = []
        conn = get_db()
        cursor = conn.cursor()

        # Cache document filenames for fast lookup
        doc_names = {}
        for sub_i in top_sub_idx:
            idx = valid_indices[sub_i]
            d_id = self.doc_ids[idx]
            if d_id not in doc_names:
                cursor.execute("SELECT filename FROM documents WHERE id = ?", (d_id,))
                row = cursor.fetchone()
                doc_names[d_id] = row["filename"] if row else "Unknown Document"

            score = float(sub_similarities[sub_i])
            results.append({
                "chunk_id": self.chunk_ids[idx],
                "doc_id": d_id,
                "document_name": doc_names[d_id],
                "page_number": self.page_numbers[idx],
                "content": self.chunk_contents[idx],
                "score": round(score, 4)
            })

        return results

_vector_store_instance = None
def get_vector_store() -> LocalVectorStore:
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = LocalVectorStore()
    return _vector_store_instance
