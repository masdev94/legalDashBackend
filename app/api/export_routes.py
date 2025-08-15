from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.export_service import ExportService
from app.services.auth_service import AuthService
from app.services.ai_analyzer import AIAnalyzer
from app.services.file_storage import FileStorage
from typing import Dict, Any
from loguru import logger

router = APIRouter(prefix="/export", tags=["export"])
security = HTTPBearer()
export_service = ExportService()
auth_service = AuthService()
ai_analyzer = AIAnalyzer()
file_storage = FileStorage()

@router.get("/health")
async def export_health():
    return {"status": "healthy", "service": "export", "message": "Export routes are working"}

@router.get("/{format}")
async def export_dashboard(
    format: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        logger.info(f"Export dashboard request received for format: {format}")
        
        current_user = auth_service.get_current_user(credentials.credentials)
        if not current_user:
            logger.error("Export failed: Invalid token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        logger.info(f"Export authenticated for user: {current_user['email']}")
        
        if format not in ['csv', 'pdf']:
            logger.error(f"Export failed: Invalid format: {format}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid format. Use 'csv' or 'pdf'"
            )
        
        documents = file_storage.get_all_documents()
        logger.info(f"Found {len(documents)} documents for export")
        
        if not documents:
            logger.warning("Export failed: No documents found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No documents found for export"
            )
        
        logger.info("Generating dashboard insights...")
        dashboard_data = await ai_analyzer.generate_dashboard_insights(documents)
        logger.info(f"Dashboard insights generated with {len(dashboard_data)} keys")
        
        if format == 'csv':
            logger.info("Generating CSV export...")
            content = export_service.export_dashboard_to_csv(dashboard_data)
            if not content:
                logger.error("CSV generation failed: No content returned")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate CSV"
                )
            media_type = "text/csv"
            file_extension = "csv"
            logger.info(f"CSV generated successfully, length: {len(content)}")
        else:  # pdf
            logger.info("Generating PDF export...")
            content = export_service.export_dashboard_to_pdf(dashboard_data)
            if not content:
                logger.error("PDF generation failed: No content returned")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate PDF"
                )
            media_type = "application/pdf"
            file_extension = "pdf"
            logger.info(f"PDF generated successfully, length: {len(content)}")
        
        timestamp = ai_analyzer.get_current_timestamp().strftime('%Y%m%d_%H%M%S')
        filename = f"legal_dashboard_{timestamp}.{file_extension}"
        
        logger.info(f"Export successful: {filename}")
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export dashboard {format} error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export dashboard as {format.upper()}: {str(e)}"
        )
