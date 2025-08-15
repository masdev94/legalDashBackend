from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid
from app.api.routes import router as api_router
from app.api.auth_routes import router as auth_router
from app.api.export_routes import router as export_router
from app.services.document_processor import DocumentProcessor
from app.services.file_storage import FileStorage
from app.services.ai_analyzer import AIAnalyzer
from app.services.query_service import QueryService
from app.models.document import Document, DocumentMetadata
from app.core.config import API_TITLE, API_VERSION, DEBUG, HOST, PORT, ALLOWED_ORIGINS
from app.core.logging import setup_logging
from loguru import logger

setup_logging()

app = FastAPI(
    title=API_TITLE,
    description="AI-powered legal document analysis and querying platform",
    version=API_VERSION,
    debug=DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(export_router, prefix="/api")

document_processor = DocumentProcessor()
file_storage = FileStorage()
ai_analyzer = AIAnalyzer()
query_service = QueryService()

@app.get("/")
async def root():
    return {"message": "Legal AI Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": ai_analyzer.get_current_timestamp().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info" if not DEBUG else "debug"
    )

