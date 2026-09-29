import os
import io
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["privacy"] == "100% On-Device"

def test_api_system_privacy():
    res = client.get("/api/system/privacy")
    assert res.status_code == 200
    data = res.json()
    assert data["documents_uploaded_to_cloud"] == 0
    assert data["ai_api_calls"] == 0
    assert data["network_egress_bytes"] == 0

def test_api_system_performance():
    res = client.get("/api/system/performance")
    assert res.status_code == 200
    data = res.json()
    assert "hardware" in data
    assert "active_model" in data

def test_document_lifecycle_and_chat():
    # 1. Upload sample text
    sample_content = b"The Qualcomm Snapdragon X Elite processor features 45 TOPS Hexagon NPU. HP PCs achieve multi-day battery life."
    files = {"file": ("test_doc.txt", io.BytesIO(sample_content), "text/plain")}
    res = client.post("/api/documents/upload", files=files)
    assert res.status_code == 200
    doc_id = res.json()["id"]

    # 2. List documents
    res_list = client.get("/api/documents")
    assert res_list.status_code == 200
    assert any(d["id"] == doc_id for d in res_list.json())

    # 3. Semantic search
    res_search = client.post("/api/search", json={"query": "Snapdragon TOPS"})
    assert res_search.status_code == 200
    assert len(res_search.json()["results"]) > 0

    # 4. Chat query with grounding
    res_chat = client.post("/api/chat", json={"query": "What TOPS does Snapdragon feature?", "doc_id": doc_id})
    assert res_chat.status_code == 200
    assert "answer" in res_chat.json()
    assert len(res_chat.json()["citations"]) > 0

    # 5. Summarize
    res_summary = client.post(f"/api/summarize/{doc_id}", json={"summary_type": "comprehensive"})
    assert res_summary.status_code == 200
    assert "tldr" in res_summary.json()["summary"]

    # 6. Delete
    res_del = client.delete(f"/api/documents/{doc_id}")
    assert res_del.status_code == 200
