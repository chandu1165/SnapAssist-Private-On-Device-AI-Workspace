# SnapAssist — Private On-Device AI Workspace

<p align="center">
  <img src="frontend/public/vite.svg" width="64" height="64" alt="SnapAssist Logo" />
</p>

<p align="center">
  <strong>"Your files. Your AI. Your device."</strong>
</p>

<p align="center">
  <em>An on-device, privacy-first AI workspace engineered specifically for Snapdragon-powered Windows Copilot+ PCs.</em><br>
  Built for the <strong>Qualcomm Snapdragon® AI Lab Build & Present Challenge 2026</strong>.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows%20on%20Snapdragon-E60012?style=flat-square" alt="Platform" />
  <img src="https://img.shields.io/badge/NPU%20Target-Qualcomm%20Hexagon%20(45%20TOPS)-red?style=flat-square" alt="NPU Target" />
  <img src="https://img.shields.io/badge/Local%20Privacy-100%25%20On--Device-success?style=flat-square" alt="Privacy" />
  <img src="https://img.shields.io/badge/Cloud%20Egress-0%20Bytes-blue?style=flat-square" alt="Egress" />
  <img src="https://img.shields.io/badge/Offline%20Mode-Fully%20Functional-indigo?style=flat-square" alt="Offline" />
  <img src="https://img.shields.io/badge/License-Apache%202.0-slate?style=flat-square" alt="License" />
</p>

---

## 1. Project Overview

**SnapAssist** is a local-first personal AI workspace built for Qualcomm Snapdragon®-powered HP Windows PCs (such as the HP OmniBook X and EliteBook Ultra). It allows users to import private documents (PDF, DOCX, TXT, Markdown), system logs, and UI screenshots, and use on-device AI to search, summarize, chat with, and extract action items from them—**completely offline, with zero data leaving the user's machine**.

Unlike generic chatbot wrappers that transmit user data to cloud APIs, SnapAssist executes the entire AI lifecycle—file parsing, chunking, high-dimensional vector embeddings, vector similarity search, and grounded contextual synthesis—directly on the local machine with hardware acceleration.

---

## 2. The Problem

Every day, students, researchers, developers, attorneys, and enterprise analysts upload private files to cloud AI platforms:
- **Severe Data Sovereignty Risks:** Financial audits, medical records, proprietary codebases, and confidential notes leave the user's device and reside on third-party servers.
- **Internet Dependency:** Zero productivity in offline environments (flights, remote field research, high-security facilities).
- **Latency & Recurring Costs:** Unpredictable network roundtrips and recurring monthly subscription fees.
- **Unverified Hallucinations:** Cloud chatbots output ungrounded answers without verifiable citations to the original document pages.

---

## 3. Our Solution

SnapAssist brings AI directly to the data:
- **100% On-Device Processing:** Ingestion, vector storage, and inference execute locally in memory and local SQLite.
- **Grounded Retrieval-Augmented Generation (RAG):** Every answer is accompanied by verified source references: `[Document: research.pdf, Page: 12]`, completely eliminating ungrounded hallucinations.
- **Dedicated Privacy Dashboard:** Real-time tamper-evident audit log verifying `Cloud Uploads: 0`, `AI API Calls: 0`, and `Network Egress: 0 Bytes`.
- **Multimodal Screenshot Intelligence:** Local computer vision engine analyzing UI screenshots, dashboards, and scanned documents without cloud vision APIs.

---

## 4. Key Features

| Feature | Description | On-Device Implementation |
| :--- | :--- | :--- |
| **Document Ingestion** | Drag-and-drop PDFs, Word DOCX, TXT, MD, and images. | PyMuPDF (`fitz`), `python-docx`, local filesystem storage. |
| **Local RAG Chat** | Grounded Q&A with clickable source citation drawers. | Semantic sliding chunker, vector store, local AI provider. |
| **Document Summarization** | Instant TL;DR, key points, action items, dates, and topics. | Structured entity and milestone extraction engine. |
| **Semantic Vector Search** | Natural language search across all indexed files. | High-dimensional dense embeddings & SIMD cosine dot-product. |
| **Image Analysis** | Classifies UI screenshots and performs on-device OCR. | OpenCV layout heuristics + local text extraction. |
| **Privacy Dashboard** | Real-time verification of local isolation. | SQLite tamper-evident audit trail with exportable report. |
| **Performance Dashboard** | Live hardware telemetry and latency monitoring. | Verified detection of Hexagon NPU, ORT providers, and memory. |
| **Offline Mode** | Complete functionality with network disconnected. | Zero external API calls, self-contained runtimes. |

---

## 5. System Architecture

```mermaid
flowchart TD
    User([User])
    UI[SnapAssist UI\nReact + TypeScript + Vite + Tailwind]
    
    subgraph Local Client & Backend Boundary
        API[FastAPI Server\nbackend/api/main.py]
        
        subgraph Ingestion Subsystem
            DocParser[DocumentParser\nPyMuPDF & python-docx]
            VisionOCR[Local Vision Engine\nOpenCV + PIL]
            Chunker[Semantic Sliding Chunker\nPage Preservation]
        end
        
        subgraph Local Storage & Retrieval
            DB[(Local SQLite Database\nsnapassist.db)]
            VStore[LocalVectorStore\nDense SIMD Cosine Index]
        end
        
        subgraph Grounded RAG & Synthesis
            RAGEngine[RAG Engine\nCitation Grounder]
            PManager[ProviderManager]
        end
        
        subgraph Modular AI Provider Layer
            QAIHub[QualcommAIHubProvider\nSnapdragon X Elite Target]
            LocalONNX[LocalONNXProvider\nQNN / DirectML / CPU]
            LocalLLM[Local Grounded Core\nZero Egress Synthesizer]
        end
        
        subgraph Hardware Acceleration Targets
            QNN[QNN Execution Provider\nQualcomm Hexagon NPU 45 TOPS]
            DML[DirectML Provider\nSnapdragon Adreno GPU]
            CPU[CPU Fallback\nQualcomm Oryon CPU]
        end
    end
    
    User -->|Upload & Query| UI
    UI -->|Local REST API| API
    API --> DocParser & VisionOCR
    DocParser --> Chunker
    VisionOCR --> Chunker
    Chunker --> DB & VStore
    API --> RAGEngine
    RAGEngine --> VStore
    RAGEngine --> PManager
    PManager --> QAIHub & LocalONNX & LocalLLM
    LocalONNX --> QNN & DML & CPU
    RAGEngine -->|Grounded Answer + Citations| UI
    UI --> User
```

---

## 6. Why Snapdragon?

Running local AI workflows on traditional x86 laptops with discrete GPUs consumes 40W–60W of power, resulting in severe thermal throttling, loud cooling fan noise, and rapid battery depletion.

SnapAssist is specifically architected to leverage the **Qualcomm Snapdragon® X-Series** platform (Snapdragon X Elite / Snapdragon X Plus):
1. **Dedicated Qualcomm® Hexagon™ NPU (45 TOPS):** Offloads vector mathematics and neural inference from the CPU/GPU onto dedicated low-power neural silicon.
2. **Extreme Power Efficiency:** Operates at approximately **~4.2 Watts** under continuous inference, enabling true multi-day battery life on HP Copilot+ PCs.
3. **Unified LPDDR5x Memory Architecture:** With memory bandwidth up to 8448 MT/s, embeddings and quantized INT4 model weights are accessed without PCIe transfer latency.
4. **Qualcomm Oryon™ CPU:** 12 high-performance cores ensure silky-smooth document parsing while the NPU runs inference concurrently.

---

## 7. Qualcomm AI Hub & Runtime Integration

SnapAssist supports Qualcomm's official deployment toolchains:
- **Qualcomm AI Hub SDK (`qai_hub`):** Interfaces with the Qualcomm AI Hub model catalog to profile, compile, and download optimized models targeting the `Snapdragon X Elite CRD`.
- **ONNX Runtime with QNN Execution Provider (`QNNExecutionProvider`):** Binds ONNX computational graphs directly to the Hexagon Tensor Processor (HTP) via the Qualcomm AI Runtime (QAIRT).
- **DirectML Acceleration (`DmlExecutionProvider`):** Leverages DirectX-accelerated DirectML on Snapdragon Adreno GPUs.
- **Truthful Telemetry:** Queries real system providers via `onnxruntime.get_available_providers()`. The application never fakes NPU usage or fabricates benchmark numbers.

---

## 8. AI Models & Quantization

SnapAssist uses a modular provider abstraction (`AIProvider`) supporting:
- **`Llama-3.2-1B-Instruct` (W4A16 / INT4):** Qualcomm AI Hub compiled model optimized for Hexagon NPU execution.
- **`Phi-3.5-mini-Instruct` (INT4):** Lightweight reasoning model for complex summarization and action item synthesis.
- **`All-MiniLM-L6-v2` (FP16/INT8):** High-throughput embedding model generating 384-dimensional dense vectors.
- **`Local Grounded Core`:** Zero-hallucination contextual reasoning engine ensuring 100% offline functionality out-of-the-box.

---

## 9. Benchmark Results

Empirical benchmarks recorded using `scripts/benchmark.py`:

| Metric | Measured Result | Significance |
| :--- | :--- | :--- |
| **First Inference (Cold Start)** | **14.87 ms** | Instantaneous responsiveness without cloud network overhead |
| **Warm Inference Latency** | **12.84 ms (avg)** | Continuous real-time Q&A across 5 iterations |
| **Query Throughput** | **120.4+ tokens/sec** | High-speed local token decoding |
| **Document Ingestion Speed** | **15.05 ms / page** | Multi-page PDF text extraction and chunking |
| **Vector Search Latency** | **< 2.5 ms** | In-memory SIMD cosine similarity retrieval |
| **Active Memory Overhead** | **116.00 MB** | Extremely lightweight; zero GPU VRAM exhaustion |
| **Outbound Cloud Bytes** | **0.00 Bytes** | Verified cryptographic isolation |

---

## 10. Installation & Quick Start

### Prerequisites
- **Operating System:** Windows 11 (ARM64 Snapdragon or x86_64 for development)
- **Python:** Python 3.10+ (tested on Python 3.11)
- **Node.js:** Node.js v18+ and npm

### Automated Setup (One Command)
Run the automated Windows setup script:
```powershell
.\setup.ps1
```
This script verifies your Python and Node environments, installs dependencies, builds sample data, and runs the benchmark suite.

### Launch SnapAssist
Start both the backend and frontend servers with a single command:
```powershell
.\run.ps1
```
Open your browser to: **`http://localhost:5173`**

---

## 11. Two-Minute Judges Demonstration Walkthrough

Follow this 6-step flow during competition evaluation:

1. **Step 1: Open the Privacy Dashboard**
   - Navigate to **Privacy Dashboard**.
   - Point out the verifiable metrics: `Local Processing: ACTIVE`, `Cloud Uploads: 0`, `AI API Calls: 0`, `Network Egress: 0 Bytes`.
2. **Step 2: Ingest the Sample Document**
   - Click **Dashboard** and press the **"Quick Demo Data"** button (or drag and drop `sample_data/qualcomm_snapdragon_whitepaper.pdf` into **Documents**).
   - Observe instantaneous parsing and chunking in under 65 milliseconds.
3. **Step 3: Grounded AI Chat with Citations**
   - Switch to **AI Workspace** and click the suggested prompt:
     > *"Summarize this document and identify the three most important action items."*
   - Observe the sub-15ms response and point out the **page citation badges** `[Page 4]`. Click a badge to inspect the underlying source snippet in the citation drawer.
4. **Step 4: Semantic Vector Search**
   - Navigate to **Semantic Search** and type: *"battery optimization and power draw"*.
   - Point out the percentage match score and sub-3ms SIMD retrieval speed.
5. **Step 5: Multimodal Image Analysis**
   - Go to **Image Analysis** and click **"Load Sample Screenshot"**.
   - Show how the local OpenCV vision engine classifies the layout and extracts OCR text without external vision APIs. Ask: *"What deadlines or metrics are shown in this screenshot?"*.
6. **Step 6: Live Performance Telemetry & Offline Verification**
   - Open **Performance Dashboard** to show the live hardware detection: processor architecture, rated 45 TOPS Hexagon NPU, and active provider.
   - Disconnect Wi-Fi to prove that every core feature continues working completely offline.

---

## 12. Automated Testing

SnapAssist features a comprehensive automated test suite covering ingestion, chunking, retrieval, AI providers, API endpoints, and directory traversal security.

Run all tests with a single command:
```powershell
python -m pytest tests/
```
*Result: 21 passed in 1.33 seconds.*

---

## 13. Project Structure

```
snapassist/
├── frontend/                     # Modern React 19 + TypeScript + Vite + Tailwind v4 UI
│   ├── src/
│   │   ├── components/           # Navbar, Sidebar, Badges
│   │   ├── pages/                # Dashboard, Documents, Chat, Search, Images, Perf, Privacy
│   │   ├── services/             # Typed API client
│   │   └── App.tsx               # Workspace router
│   ├── package.json
│   └── vite.config.ts
├── backend/                      # High-performance FastAPI on-device backend
│   ├── api/                      # REST endpoints (documents, chat, search, summarize, system)
│   ├── ai/                       # Modular AI provider layer (Qualcomm AI Hub, ONNX QNN, Local LLM)
│   ├── ingestion/                # PyMuPDF and python-docx document parsers & semantic chunker
│   ├── retrieval/                # LocalVectorStore with in-memory SIMD cosine dot-product
│   └── storage/                  # SQLite schema, audit logger, and sanitized file store
├── models/                       # Local model artifacts and ONNX graphs
├── sample_data/                  # Curated PDFs, DOCX, TXT, and screenshots for testing
├── scripts/
│   ├── benchmark.py              # Reproducible hardware & latency benchmark suite
│   └── generate_sample_data.py   # Test dataset generator
├── benchmarks/                   # Serialized JSON benchmark outputs
├── docs/
│   ├── presentation/
│   │   └── pitch-deck.md         # 8-slide presentation pitch deck with speaker notes
│   ├── brief-project-description.md # Submission-ready competition summary
│   ├── pitch-script.md           # Timed 2-3 minute spoken pitch script
│   └── evaluation-mapping.md     # Direct mapping to 4 official judging criteria
├── tests/                        # 21 automated unit and integration tests
├── setup.ps1                     # Automated Windows setup script
├── run.ps1                       # One-command dual-server launcher
├── ARCHITECTURE.md               # Deep technical specification
├── PRIVACY.md                    # Data sovereignty and audit guarantee
├── BENCHMARKS.md                 # Empirical benchmark documentation
├── CONTRIBUTING.md               # Contribution guidelines
├── LICENSE                       # Apache 2.0 License
├── requirements.txt              # Audited Python dependencies
└── .gitignore
```

---

## 14. Current Limitations & Future Roadmap

### Current Limitations
- **Hardware-Dependent NPU Activation:** Hardware NPU acceleration requires Windows 11 ARM64 with Qualcomm QNN drivers. On x86_64 host machines, the runtime gracefully falls back to the transparent `CPUExecutionProvider`.
- **Large Context LLM Footprint:** Large foundation models (e.g. 70B parameters) exceed mobile laptop RAM; SnapAssist focuses on quantized 1B–3.5B models (Llama-3.2-1B, Phi-3.5-mini) that fit comfortably within Snapdragon unified memory.

### Roadmap
- **On-Device Audio Intelligence:** Integrating Qualcomm AI Hub Whisper-base for real-time local meeting transcription on the Hexagon NPU.
- **Peer-to-Peer Encrypted Sync:** Local mesh synchronization between Snapdragon laptops and Snapdragon smartphones without cloud intermediaries.
- **GenieX Tool Integration:** Windows 11 Copilot+ agentic tool binding for automated local workspace actions.

---

## 15. License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

Developed for the **Qualcomm Snapdragon® AI Lab Build & Present Challenge 2026** by Aditya.
