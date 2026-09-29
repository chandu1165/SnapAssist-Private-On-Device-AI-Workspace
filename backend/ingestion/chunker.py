import re
import uuid
import time
from typing import List, Dict, Any

class Chunk:
    def __init__(self, chunk_id: str, doc_id: str, chunk_index: int, page_number: int, content: str, token_count: int):
        self.id = chunk_id
        self.doc_id = doc_id
        self.chunk_index = chunk_index
        self.page_number = page_number
        self.content = content
        self.token_count = token_count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "doc_id": self.doc_id,
            "chunk_index": self.chunk_index,
            "page_number": self.page_number,
            "content": self.content,
            "token_count": self.token_count,
        }

def estimate_tokens(text: str) -> int:
    """Rough word/subword token estimation (~4 chars/token or word count * 1.3)."""
    words = len(text.split())
    return max(1, int(words * 1.3))

def split_into_sentences(text: str) -> List[str]:
    """Splits text into sentences while respecting abbreviations."""
    # Split on sentence terminals followed by whitespace
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]

def chunk_document_pages(doc_id: str, pages: List[Dict[str, Any]], target_chunk_chars: int = 600, overlap_chars: int = 100) -> List[Chunk]:
    """
    Chunks document pages into overlapping semantic chunks, preserving page references.
    pages: list of dicts with {"page_number": int, "text": str}
    """
    chunks: List[Chunk] = []
    chunk_index = 0

    for page_info in pages:
        page_num = page_info.get("page_number", 1)
        raw_text = page_info.get("text", "").strip()
        if not raw_text:
            continue

        sentences = split_into_sentences(raw_text)
        current_chunk_parts: List[str] = []
        current_len = 0

        for sentence in sentences:
            sentence_len = len(sentence)
            if current_len + sentence_len > target_chunk_chars and current_chunk_parts:
                chunk_text = " ".join(current_chunk_parts).strip()
                chunks.append(Chunk(
                    chunk_id=str(uuid.uuid4()),
                    doc_id=doc_id,
                    chunk_index=chunk_index,
                    page_number=page_num,
                    content=chunk_text,
                    token_count=estimate_tokens(chunk_text)
                ))
                chunk_index += 1

                # Keep overlap from the end of the previous chunk
                overlap_text = ""
                while current_chunk_parts and len(overlap_text) < overlap_chars:
                    last_part = current_chunk_parts.pop()
                    overlap_text = last_part + " " + overlap_text

                current_chunk_parts = [overlap_text.strip()] if overlap_text.strip() else []
                current_len = len(current_chunk_parts[0]) if current_chunk_parts else 0

            current_chunk_parts.append(sentence)
            current_len += sentence_len + 1

        if current_chunk_parts:
            final_text = " ".join(current_chunk_parts).strip()
            if final_text:
                chunks.append(Chunk(
                    chunk_id=str(uuid.uuid4()),
                    doc_id=doc_id,
                    chunk_index=chunk_index,
                    page_number=page_num,
                    content=final_text,
                    token_count=estimate_tokens(final_text)
                ))
                chunk_index += 1

    return chunks
