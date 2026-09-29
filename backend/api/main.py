import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.storage.database import init_db, record_audit
from backend.api.routes_documents import router as documents_router
from backend.api.routes_chat import router as chat_router
from backend.api.routes_search import router as search_router
from backend.api.routes_summarize import router as summarize_router
from backend.api.routes_image import router as image_router
from backend.api.routes_system import router as system_router

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    record_audit("system_boot", target="localhost", details="SnapAssist local workspace backend initialized.")
    yield

app = FastAPI(
    title="SnapAssist API",
    description="Private On-Device AI Workspace API for Qualcomm Snapdragon PCs",
    version="1.0.0",
    lifespan=lifespan
)

# Explicit CORS configuration restricting origins to local frontend ports
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# Mount API routers
app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(search_router)
app.include_router(summarize_router)
app.include_router(image_router)
app.include_router(system_router)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "SnapAssist — Private On-Device AI Workspace",
        "version": "1.0.0",
        "privacy": "100% On-Device",
        "cloud_connections": 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.main:app", host="127.0.0.1", port=8000, reload=True)
