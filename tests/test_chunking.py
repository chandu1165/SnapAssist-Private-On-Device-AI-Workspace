import pytest
from backend.ingestion.chunker import chunk_document_pages, split_into_sentences, estimate_tokens

def test_sentence_splitter():
    text = "Qualcomm develops Snapdragon processors. The Hexagon NPU delivers 45 TOPS! Is it power efficient? Yes, it is."
    sentences = split_into_sentences(text)
    assert len(sentences) == 4
    assert sentences[0] == "Qualcomm develops Snapdragon processors."
    assert sentences[1] == "The Hexagon NPU delivers 45 TOPS!"

def test_estimate_tokens():
    text = "Snapdragon X Elite on HP Copilot+ PC"
    tokens = estimate_tokens(text)
    assert tokens > 0

def test_chunk_document_pages():
    pages = [
        {
            "page_number": 1,
            "text": "The Qualcomm Snapdragon X Elite features 45 TOPS Hexagon NPU. " * 15
        },
        {
            "page_number": 2,
            "text": "Energy efficiency allows multi-day battery life on HP laptops. " * 15
        }
    ]
    chunks = chunk_document_pages("doc_123", pages, target_chunk_chars=300, overlap_chars=50)
    assert len(chunks) > 2
    # Verify metadata preservation
    assert chunks[0].doc_id == "doc_123"
    assert chunks[0].page_number == 1
    assert any(c.page_number == 2 for c in chunks)
    assert all(c.token_count > 0 for c in chunks)
