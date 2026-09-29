import time
import os
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel

from backend.storage.file_store import save_uploaded_file, delete_stored_file
from backend.ai.ocr_engine import get_ocr_engine
from backend.ai.provider_manager import get_provider_manager
from backend.storage.database import record_audit, record_performance

router = APIRouter(prefix="/api/image", tags=["image"])

class ImageQARequest(BaseModel):
    query: str
    ocr_text: str
    visual_type: Optional[str] = "image"

@router.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    start_time = time.time()
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty image file.")

        doc_id, filename, file_path, file_size = save_uploaded_file(file.filename, content)
        ext = os.path.splitext(filename)[1].lower()
        if ext not in [".png", ".jpg", ".jpeg", ".webp"]:
            delete_stored_file(file_path)
            raise HTTPException(status_code=400, detail="Uploaded file is not a supported image format.")

        ocr = get_ocr_engine()
        result = ocr.analyze_image(file_path)

        elapsed_ms = (time.time() - start_time) * 1000
        record_audit("image_analysis", target=filename, details=f"Type: {result.get('visual_type')}, Chars: {len(result.get('text', ''))}")
        record_performance("image_analysis", "Local-Vision-OCR-Engine", "Local CV2/PIL", "CPU/NPU Vision", elapsed_ms)

        return {
            "image_id": doc_id,
            "filename": filename,
            "file_size": file_size,
            "visual_type": result.get("visual_type"),
            "dimensions": result.get("dimensions"),
            "text_regions_count": result.get("text_regions_count"),
            "mean_brightness": result.get("mean_brightness"),
            "ocr_text": result.get("text"),
            "insights": result.get("insights", []),
            "latency_ms": round(elapsed_ms, 2)
        }
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

@router.post("/qa")
def image_qa(request: ImageQARequest):
    if not request.query:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    start_time = time.time()
    provider = get_provider_manager().get_active_provider()
    
    context_chunks = [{
        "chunk_id": "img_chunk_1",
        "doc_id": "image",
        "document_name": f"Visual Artifact ({request.visual_type})",
        "page_number": 1,
        "content": request.ocr_text,
        "score": 1.0
    }]
    
    result = provider.generate(request.query, context_chunks)
    elapsed_ms = (time.time() - start_time) * 1000
    record_audit("image_qa", details=f"Question: {request.query[:50]}")

    return {
        "query": request.query,
        "answer": result.get("answer"),
        "citations": result.get("citations"),
        "latency_ms": round(elapsed_ms, 2),
        "execution_provider": result.get("execution_provider")
    }
