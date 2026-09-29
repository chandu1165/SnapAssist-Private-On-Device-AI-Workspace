# SnapAssist — Brief Project Description

**Competition Submission:** Qualcomm Snapdragon® AI Lab Build & Present Challenge 2026  
**Project Name:** SnapAssist — Private On-Device AI Workspace  
**Tagline:** *"Your files. Your AI. Your device."*  
**Developer:** Aditya (Lead Engineer & Product Designer)  

---

### 1. Problem
Knowledge workers, researchers, developers, and students frequently upload confidential documents, financial reports, medical records, and proprietary source code to cloud AI services. This introduces data privacy risks, internet dependency, recurring per-token API costs, and network latency.

### 2. Proposed Solution
SnapAssist is a local-first desktop workspace engineered for Snapdragon-powered Windows Copilot+ PCs (such as the HP OmniBook X and EliteBook Ultra). It enables users to import PDFs, Word documents, text files, and screenshot images, and use on-device AI to search, summarize, chat with, and extract action items from their personal files—completely offline with zero data egress.

### 3. Key Innovation & Grounded RAG
- **Local Parsing & Chunking:** PyMuPDF extracts text and page numbers on-device in sub-10ms per page.
- **Dense Vector Search:** Fast 384-dimensional dense semantic vector search via in-memory NumPy SIMD matrix dot-product.
- **Grounded Citations:** Answers are anchored to specific document passages and page numbers `[Page X]`, enabling instant verification. If evidence is insufficient, the system reports: *"I couldn't find enough information in the indexed documents."*
- **Multimodal Screenshot Intelligence:** Local computer vision engine running OpenCV and OCR classifies UI layouts and answers questions about screenshots without cloud vision APIs.

### 4. Snapdragon & Qualcomm AI Architecture
- **Hexagon™ NPU (45 TOPS Design Target):** Configured for ONNX Runtime with Qualcomm Neural Network (`QNNExecutionProvider`) and DirectML, offloading neural processing from the Qualcomm Oryon™ CPU.
- **Truthful Hardware Telemetry:** Automatically queries system execution providers (`QNNExecutionProvider`, `DmlExecutionProvider`, `CPUExecutionProvider`) and displays status (`ACTIVE`, `FALLBACK`, `UNAVAILABLE`) with human-readable explanations.

### 5. Verifiable Privacy & Security
- **Local Audit Log:** Displays a local tamper-evident audit log verifying `Cloud Uploads: 0` and `AI API Calls: 0`.
- **Hardened Security:** Restricted CORS middleware, path traversal sanitization, and strict upload validation.

### 6. Deployment & Accessibility
- **Windows First-Class:** Includes one-command automated installation (`setup.ps1`) and startup (`run.ps1`).
- **Complete Test Coverage:** 21 automated unit and integration tests passing cleanly.
- **Runtime Offline Resilience:** 100% functional at runtime with network interfaces severed.
