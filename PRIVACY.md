# SnapAssist Privacy & Data Sovereignty Architecture

> *"Your files. Your AI. Your device."*

## 1. Executive Summary

SnapAssist is built on a local-first philosophy: **Users should never be forced to send confidential documents, financial reports, proprietary code, or personal study notes to third-party cloud servers.**

SnapAssist executes document ingestion, vector storage, semantic search, and AI reasoning on the local machine (`localhost`).

---

## 2. Privacy Architecture & Telemetry Disambiguation

To maintain absolute technical truthfulness, SnapAssist distinguishes between **Architecture Guarantees** and **Measured Telemetry**:

| Dimension | Cloud AI Services | SnapAssist Architecture Guarantee |
| :--- | :--- | :--- |
| **Document Storage** | Remote Cloud Buckets | Local Disk (`backend/data/uploads`) |
| **Text Parsing** | Remote Server APIs | Local PyMuPDF & python-docx |
| **Vector Storage** | Cloud Vector DB | Local SQLite Vector Table |
| **Embedding Generation** | Cloud API Calls | Local On-Device Vector Embeddings |
| **AI Inference** | Remote Cloud LLMs | On-Device Qualcomm Hexagon NPU / ONNX Runtime |
| **Outbound Payload Egress** | Continuous transmission | **0 Bytes Outbound by Architecture** |
| **Local IPC** | N/A | Frontend/Backend communicate strictly over `127.0.0.1` |
| **Offline Functionality** | Unavailable | **Fully Functional at Runtime** |

---

## 3. Local Audit Logging

Every document ingestion, chunking, search, and inference operation is recorded in a local SQLite audit table:

```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    target TEXT,
    is_local INTEGER DEFAULT 1,
    bytes_outbound INTEGER DEFAULT 0,
    external_api_calls INTEGER DEFAULT 0,
    timestamp REAL NOT NULL,
    details TEXT
);
```

- `is_local`: Set to `1` for all local pipelines.
- `bytes_outbound`: Set to `0` for architecture-enforced local operations.
- `external_api_calls`: Set to `0`.

Users can inspect this audit trail in real time via the **Privacy Dashboard** or export the log as JSON via `GET /api/system/privacy`.

---

## 4. Input Validation & Defensive Security

- **Path Traversal Protection:** Filenames are sanitized via `backend/storage/file_store.py::sanitize_filename` to strip path delimiters (`../`, `..\`). Target file paths are validated to ensure they remain inside `backend/data/uploads`.
- **Extension Validation:** Only `.pdf`, `.docx`, `.txt`, `.md`, `.png`, `.jpg`, `.jpeg`, `.webp` extensions are allowed. Unrecognized binary formats are rejected.
- **Hardened CORS:** Endpoint origins are restricted in `backend/api/main.py` strictly to local dev hosts (`http://localhost:5173`, `http://127.0.0.1:5173`, etc.).

---

## 5. Offline Verification Procedure

1. Sever network connectivity (toggle Airplane Mode or disconnect Wi-Fi).
2. Open SnapAssist in your browser (`http://localhost:5173`).
3. Import a document or image and run grounded Q&A or semantic search.
4. Verify that all features operate with zero network connection.
