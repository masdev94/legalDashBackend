from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.export_service import ExportService
from app.services.auth_service import AuthService
from app.services.ai_analyzer import AIAnalyzer
from app.services.file_storage import FileStorage
from typing import Dict, Any
from loguru import logger
from datetime import datetime

router = APIRouter(prefix="/export", tags=["export"])
security = HTTPBearer()
export_service = ExportService()
auth_service = AuthService()
ai_analyzer = AIAnalyzer()
file_storage = FileStorage()

@router.get("/health")
async def export_health():
    return {"status": "healthy", "service": "export", "message": "Export routes are working"}

@router.get("/test/{format}")
async def test_export(
    format: str
):
    """Test endpoint for export functionality without authentication"""
    try:
        logger.info(f"Test export request received for format: {format}")
        
        if format not in ['csv', 'pdf']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid format. Use 'csv' or 'pdf'"
            )
        
        # Create sample dashboard data for testing
        sample_data = {
            "total_documents": 5,
            "agreement_types": {"Contract": 3, "Agreement": 2},
            "jurisdictions": {"US": 3, "EU": 2},
            "industries": {"Technology": 3, "Finance": 2},
            "geographies": {"North America": 3, "Europe": 2},
            "total_value": 1500000.00,
            "date_range": {"start": "2024-01-01", "end": "2024-12-31"},
            "recent_uploads": [
                {
                    "filename": "sample_contract.pdf",
                    "agreement_type": "Contract",
                    "jurisdiction": "US",
                    "industry": "Technology",
                    "upload_date": "2024-01-15T10:00:00Z"
                }
            ],
            "trends_over_time": {"monthly": {"January": 2, "February": 3}},
            "risk_analysis": {"distribution": {"Low": 3, "Medium": 2}},
            "compliance_metrics": {"overall": 85.5},
            "document_health": {
                "average_confidence": 0.87,
                "processing_success_rate": 95.0,
                "metadata_completeness": 88.0
            }
        }
        
        if format == 'csv':
            content = export_service.export_dashboard_to_csv(sample_data)
            media_type = "text/csv"
            file_extension = "csv"
        else:  # pdf
            content = export_service.export_dashboard_to_pdf(sample_data)
            media_type = "application/pdf"
            file_extension = "pdf"
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate {format.upper()}"
            )
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_dashboard_{timestamp}.{file_extension}"
        
        logger.info(f"Test export successful: {filename}")
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test export {format} error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test export as {format.upper()}: {str(e)}"
        )

@router.get("/{format}")
async def export_dashboard(
    format: str,
    # credentials: HTTPAuthorizationCredentials = Depends(security)  # Temporarily disabled for testing
):
    try:
        logger.info(f"Export dashboard request received for format: {format}")
        
        # Temporarily disable authentication for testing
        # current_user = auth_service.get_current_user(credentials.credentials)
        # if not current_user:
        #     logger.error("Export failed: Invalid token")
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Invalid token"
        #     )
        
        # logger.info(f"Export authenticated for user: {current_user['email']}")
        logger.info("Export authentication temporarily disabled for testing")
        
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
