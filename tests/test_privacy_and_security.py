import io
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.storage.file_store import sanitize_filename, save_uploaded_file

client = TestClient(app)

def test_directory_traversal_sanitization():
    unsafe_name = "../../etc/passwd"
    clean = sanitize_filename(unsafe_name)
    assert ".." not in clean
    assert "/" not in clean
    assert "\\" not in clean

    windows_unsafe = "..\\..\\Windows\\System32\\calc.exe"
    clean_win = sanitize_filename(windows_unsafe)
    assert ".." not in clean_win
    assert "\\" not in clean_win

def test_unsupported_file_extension_rejection():
    fake_exe = b"MZ\x90\x00\x03\x00\x00\x00"
    files = {"file": ("malicious.exe", io.BytesIO(fake_exe), "application/octet-stream")}
    res = client.post("/api/documents/upload", files=files)
    assert res.status_code == 400
    assert "Unsupported file extension" in res.json()["detail"]

def test_empty_file_upload_rejection():
    files = {"file": ("empty.txt", io.BytesIO(b""), "text/plain")}
    res = client.post("/api/documents/upload", files=files)
    assert res.status_code == 400

def test_privacy_audit_zero_cloud_calls():
    # Execute several operations
    client.get("/api/health")
    client.post("/api/chat", json={"query": "Testing privacy audit logging."})

    res = client.get("/api/system/privacy")
    assert res.status_code == 200
    data = res.json()
    assert data["documents_uploaded_to_cloud"] == 0
    assert data["ai_api_calls"] == 0
    assert data["network_egress_bytes"] == 0
    # Audit events must all be marked is_local == True
    for evt in data["audit_events"]:
        assert evt["is_local"] is True
        assert evt["bytes_outbound"] == 0
        assert evt["external_api_calls"] == 0

def test_rag_empty_fallback_response():
    from backend.ai.local_llm_provider import LocalLLMProvider
    provider = LocalLLMProvider()
    res = provider.generate("non_existent_query", context_chunks=[])
    assert res["answer"] == "I couldn't find enough information in the indexed documents."
    assert res["citations"] == []

def test_cors_allowed_origins():
    # Verify allowed localhost origin headers
    res = client.options("/api/health", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"})
    assert res.headers.get("access-control-allow-origin") == "http://localhost:5173"

