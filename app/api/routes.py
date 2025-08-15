from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import time
import zipfile
import io
from pathlib import Path
from loguru import logger
import os

from app.models.document import (
    QueryRequest, QueryResponse, DashboardData, UploadResponse,
    StructuredComparison, DocumentAnalysis
)
from app.services.document_processor import DocumentProcessor
from app.services.query_service import QueryService
from app.services.ai_analyzer import AIAnalyzer
from app.services.file_storage import FileStorage
from app.core.config import ALLOWED_FILE_TYPES, MAX_FILE_SIZE, MAX_DOCUMENT_SIZE

router = APIRouter()

document_processor = DocumentProcessor()
query_service = QueryService()
ai_analyzer = AIAnalyzer()
file_storage = FileStorage()

@router.post("/upload", response_model=UploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    start_time = time.time()
    uploaded_files = []
    failed_files = []
    
    try:
        logger.info(f"Processing {len(files)} uploaded files")
        
        for file in files:
            try:
                if not any(file.filename.lower().endswith(ext) for ext in ALLOWED_FILE_TYPES):
                    failed_files.append(f"{file.filename} (unsupported file type)")
                    continue
                
                if file.size > MAX_FILE_SIZE:
                    failed_files.append(f"{file.filename} (file too large)")
                    continue
                
                file_content = await file.read()
                
                document = document_processor.process_document(file.filename, file_content)
                
                enhanced_document = await ai_analyzer.enhance_document(document)
                
                file_storage.store_document(enhanced_document)
                query_service.add_documents([enhanced_document])
                
                uploaded_files.append(file.filename)
                logger.info(f"Successfully processed: {file.filename}")
                
            except Exception as e:
                logger.error(f"Failed to process {file.filename}: {str(e)}")
                failed_files.append(f"{file.filename} (processing error)")
        
        processing_time = time.time() - start_time
        
        response = UploadResponse(
            message=f"Upload completed. {len(uploaded_files)} files processed successfully.",
            uploaded_files=uploaded_files,
            failed_files=failed_files,
            total_processed=len(uploaded_files),
            processing_time=processing_time
        )
        
        logger.info(f"Upload completed in {processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/upload-folder")
async def upload_folder(zip_file: UploadFile = File(...)):
    start_time = time.time()
    uploaded_files = []
    failed_files = []
    
    try:
        if not zip_file.filename.lower().endswith('.zip'):
            raise HTTPException(status_code=400, detail="Please upload a ZIP file containing documents")
        
        zip_content = await zip_file.read()
        
        with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_ref:
            file_list = zip_ref.namelist()
            
            supported_files = [
                f for f in file_list 
                if any(f.lower().endswith(ext) for ext in ALLOWED_FILE_TYPES)
                and not f.endswith('/')
            ]
            
            logger.info(f"Found {len(supported_files)} supported files in ZIP")
            
            for filename in supported_files:
                try:
                    file_content = zip_ref.read(filename)
                    
                    document = document_processor.process_document(filename, file_content)
                    
                    enhanced_document = await ai_analyzer.enhance_document(document)
                    
                    file_storage.store_document(enhanced_document)
                    query_service.add_documents([enhanced_document])
                    
                    uploaded_files.append(filename)
                    logger.info(f"Successfully processed: {filename}")
                    
                except Exception as e:
                    logger.error(f"Failed to process {filename}: {str(e)}")
                    failed_files.append(f"{filename} (processing error)")
        
        processing_time = time.time() - start_time
        
        response = UploadResponse(
            message=f"Folder upload completed. {len(uploaded_files)} files processed successfully.",
            uploaded_files=uploaded_files,
            failed_files=failed_files,
            total_processed=len(uploaded_files),
            processing_time=processing_time
        )
        
        logger.info(f"Folder upload completed in {processing_time:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Folder upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Folder upload failed: {str(e)}")

@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    try:
        logger.info(f"Processing query: {request.question}")
        
        if not file_storage.get_all_documents():
            return QueryResponse(
                question=request.question,
                results=[],
                total_results=0,
                structured_comparisons=[],
                document_analysis=None
            )
        
        response = await query_service.query_documents_enhanced(request, file_storage.get_all_documents())
        
        return response
        
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.post("/analyze-documents")
async def analyze_documents():
    try:
        if not file_storage.get_all_documents():
            raise HTTPException(status_code=404, detail="No documents to analyze")
        
        analysis = await ai_analyzer.analyze_document_collection(file_storage.get_all_documents())
        
        return analysis
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data():
    try:
        logger.info("Generating enhanced dashboard data")
        
        if not file_storage.get_all_documents():
            return DashboardData(
                agreement_types={},
                jurisdictions={},
                industries={},
                geographies={},
                total_documents=0,
                total_value=None,
                date_range={"start": "", "end": ""},
                recent_uploads=[],
                trends_over_time={},
                risk_analysis={},
                compliance_metrics={}
            )
        
        dashboard_data = await ai_analyzer.generate_dashboard_insights(file_storage.get_all_documents())
        
        logger.info(f"Enhanced dashboard data generated for {len(file_storage.get_all_documents())} documents")
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}")

@router.post("/ai/summary")
async def generate_ai_summary(data: dict):
    try:
        logger.info(f"AI Summary request received with data: {data}")
        
        summary = ai_analyzer.generate_ai_summary(data)
        logger.info(f"AI Summary generated: {summary}")
        
        return {"summary": summary}
    except Exception as e:
        logger.error(f"AI Summary error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to generate AI summary: {str(e)}")

@router.get("/documents")
async def list_documents():
    try:
        documents = []
        for doc in file_storage.get_all_documents():
            documents.append({
                "id": doc.id,
                "filename": doc.metadata.filename,
                "file_size": doc.metadata.file_size,
                "file_type": doc.metadata.file_type,
                "upload_date": doc.metadata.upload_date.isoformat() if doc.metadata.upload_date else None,
                "agreement_type": doc.metadata.agreement_type.value if doc.metadata.agreement_type else None,
                "jurisdiction": doc.metadata.jurisdiction.value if doc.metadata.jurisdiction else None,
                "industry": doc.metadata.industry.value if doc.metadata.industry else None,
                "geography": doc.metadata.geography.value if doc.metadata.geography else None,
                "processing_status": doc.processing_status,
                "confidence_score": getattr(doc, 'confidence_score', None),
                "ai_insights": getattr(doc, 'ai_insights', {})
            })
        
        return {"documents": documents, "total": len(documents)}
        
    except Exception as e:
        logger.error(f"List documents error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@router.get("/documents/{document_id}/analysis")
async def get_document_analysis(document_id: str):
    try:
        document = None
        for doc in file_storage.get_all_documents():
            if doc.id == document_id:
                document = doc
                break
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        analysis = await ai_analyzer.analyze_single_document(document)
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze document: {str(e)}")

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    try:
        success = file_storage.delete_document(document_id)
        
        if success:
            query_service.remove_document(document_id)
            logger.info(f"Document {document_id} deleted successfully")
            return {"message": "Document deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete document error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete document: {str(e)}")

@router.post("/documents/{document_id}/regenerate-ai")
async def regenerate_document_ai(document_id: str):
    try:
        document = file_storage.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        enhanced_document = await ai_analyzer.enhance_document(document)
        
        file_storage.store_document(enhanced_document)
        query_service.add_documents([enhanced_document])
        
        logger.info(f"Fresh AI insights generated for document {document_id}")
        return {"message": f"Fresh AI insights generated for document {document_id}"}
        
    except Exception as e:
        logger.error(f"Error regenerating AI insights for document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to regenerate AI insights: {str(e)}")
