import pytest
from backend.ingestion.chunker import Chunk
from backend.retrieval.vector_store import get_vector_store
from backend.ai.embedding_engine import get_embedding_engine

def test_embedding_engine():
    engine = get_embedding_engine()
    vec1 = engine.embed_text("Snapdragon Hexagon NPU 45 TOPS")
    vec2 = engine.embed_text("Qualcomm Snapdragon neural accelerator")
    vec3 = engine.embed_text("Completely unrelated baking recipe for chocolate cake")

    assert vec1.shape == (384,)
    # Similarity between related concepts should be higher than unrelated
    sim_related = float(vec1 @ vec2)
    sim_unrelated = float(vec1 @ vec3)
    assert sim_related > sim_unrelated

def test_vector_store_operations():
    vstore = get_vector_store()
    test_chunks = [
        Chunk("c1", "doc_test_1", 0, 1, "Snapdragon X Elite delivers 45 TOPS on the Hexagon NPU.", 15),
        Chunk("c2", "doc_test_1", 1, 1, "HP OmniBook laptops offer extraordinary battery life.", 12),
        Chunk("c3", "doc_test_2", 0, 1, "Submission deadline for Qualcomm AI Lab Challenge is October 2026.", 16),
    ]

    vstore.add_chunks("doc_test_1", test_chunks[:2])
    vstore.add_chunks("doc_test_2", [test_chunks[2]])

    # Query search
    res = vstore.search("How many TOPS does Snapdragon provide?", top_k=2)
    assert len(res) > 0
    assert "45 TOPS" in res[0]["content"]

    # Filtered search
    res_filtered = vstore.search("deadline", filter_doc_id="doc_test_2")
    assert len(res_filtered) == 1
    assert "deadline" in res_filtered[0]["content"].lower()

    # Clean up
    vstore.delete_document("doc_test_1")
    vstore.delete_document("doc_test_2")
