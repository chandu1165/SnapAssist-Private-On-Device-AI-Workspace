# SnapAssist Architecture Specification

> **Qualcomm Snapdragon® AI Lab Build & Present Challenge 2026**  
> *"Your files. Your AI. Your device."*

## 1. System Architecture Overview

SnapAssist is architected as a local-first workspace for **Snapdragon-powered HP Windows PCs**. All document processing, vector search, image OCR, and contextual synthesis operate strictly on `localhost`.

```mermaid
flowchart TD
    User([User Interaction])
    UI[SnapAssist UI\nReact + TypeScript + Vite + Tailwind]
    
    subgraph Local Client & Backend Boundary
        API[FastAPI Gateway\nbackend/api/main.py]
        
        subgraph Ingestion & Preprocessing
            DocParser[DocumentParser\nPyMuPDF & python-docx]
            VisionOCR[Local Vision & OCR Engine\nOpenCV + PIL]
            Chunker[Semantic Sliding Chunker\nPage Preservation]
        end
        
        subgraph Storage & Indexing
            SQLite[(Local SQLite Database\nsnapassist.db)]
            VStore[LocalVectorStore\nDense SIMD Cosine Index]
        end
        
        subgraph RAG & Reasoning Pipeline
            RAGEngine[Grounded RAG Engine\nCitation Grounder]
        end
        
        subgraph Modular AI Provider Layer
            Manager[ProviderManager]
            QAIHub[QualcommAIHubProvider\nSnapdragon X Elite Target]
            LocalONNX[LocalONNXProvider\nQNN / DirectML / CPU]
            LocalLLM[Local Grounded Core\nZero Egress Synthesizer]
        end
        
        subgraph Hardware Runtimes
            QNN[QNN Execution Provider\nQualcomm Hexagon NPU]
            DML[DirectML Provider\nSnapdragon Adreno GPU]
            CPU[CPU Fallback\nQualcomm Oryon / Host CPU]
        end
    end
    
    User -->|Drag & Drop / Query| UI
    UI -->|Local HTTP| API
    API --> DocParser & VisionOCR
    DocParser --> Chunker
    VisionOCR --> Chunker
    Chunker --> SQLite & VStore
    API --> RAGEngine
    RAGEngine --> VStore
    RAGEngine --> Manager
    Manager --> QAIHub & LocalONNX & LocalLLM
    LocalONNX --> QNN & DML & CPU
    RAGEngine -->|Grounded Answer + Citations| UI
    UI --> User
```

---

## 2. Ingestion & Preprocessing Pipeline

1. **Document Parsing (`backend/ingestion/document_parser.py`):**
   - **PDF:** Page-by-page extraction via PyMuPDF (`pymupdf`), capturing text and page numbers.
   - **DOCX:** Paragraph and table extraction via `python-docx`.
   - **TXT / Markdown:** Plain text parsing.
   - **Images & Screenshots:** On-device visual layout classification and OCR via OpenCV contour heuristics and PIL (`backend/ai/ocr_engine.py`).
2. **Semantic Chunking (`backend/ingestion/chunker.py`):**
   - Overlapping sliding-window chunker (~300–600 characters) preserving page references.

---

## 3. Vector Storage & Search (`backend/retrieval/vector_store.py`)

- **384-Dimensional Dense Vectors:** Generated locally using positional n-gram projections or ONNX embedding graphs.
- **SIMD Cosine Dot-Product Search:** Vectorized in-memory NumPy matrix search (`np.dot(matrix, query_vec)`).

---

## 4. Modular AI Provider Abstraction (`backend/ai/`)

Inference backends extend `AIProvider`:

```python
class AIProvider(ABC):
    @abstractmethod
    def generate(self, query: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def summarize(self, text: str, summary_type: str = "comprehensive") -> Dict[str, Any]:
        pass
```

### Execution Priority & Runtime Detection
1. `QNNExecutionProvider` (Qualcomm Neural Network execution provider targeting Qualcomm Hexagon NPU on Windows 11 ARM64).
2. `DmlExecutionProvider` (DirectML GPU acceleration).
3. `CPUExecutionProvider` (Universal CPU fallback with clear status reporting).

---

## 5. Grounded RAG & Citations

- Answers are synthesized using context chunks retrieved from local vector storage.
- Every claim includes explicit source references `[Document: filename, Page: X]`.
- If evidence is insufficient, the system explicitly reports: *"I couldn't find enough information in the indexed documents."*
