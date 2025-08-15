import csv
import io
from typing import List, Dict, Any
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from loguru import logger

class ExportService:
    def __init__(self):
        pass
    
    def export_dashboard_to_csv(self, dashboard_data: Dict[str, Any]) -> str:
        try:
            output = io.StringIO()
            output.write('\ufeff')  # BOM for Excel compatibility
            writer = csv.writer(output)
            
            # Header
            writer.writerow(["Legal Dashboard Report"])
            writer.writerow([f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
            writer.writerow([])
            
            # Document Summary
            writer.writerow(["Document Summary"])
            writer.writerow(["Total Documents", dashboard_data.get("total_documents", 0)])
            writer.writerow([])
            
            # Agreement Types
            if "agreement_types" in dashboard_data and dashboard_data["agreement_types"]:
                writer.writerow(["Agreement Types"])
                writer.writerow(["Type", "Count"])
                for agreement_type, count in dashboard_data["agreement_types"].items():
                    writer.writerow([agreement_type, count])
                writer.writerow([])
            
            # Jurisdictions
            if "jurisdictions" in dashboard_data and dashboard_data["jurisdictions"]:
                writer.writerow(["Jurisdictions"])
                writer.writerow(["Jurisdiction", "Count"])
                for jurisdiction, count in dashboard_data["jurisdictions"].items():
                    writer.writerow([jurisdiction, count])
                writer.writerow([])
            
            # Industries
            if "industries" in dashboard_data and dashboard_data["industries"]:
                writer.writerow(["Industries"])
                writer.writerow(["Industry", "Count"])
                for industry, count in dashboard_data["industries"].items():
                    writer.writerow([industry, count])
                writer.writerow([])
            
            # Risk Analysis
            if "risk_analysis" in dashboard_data and dashboard_data["risk_analysis"]:
                risk_dist = dashboard_data["risk_analysis"].get("distribution", {})
                if risk_dist:
                    writer.writerow(["Risk Analysis"])
                    writer.writerow(["Risk Level", "Count"])
                    for risk_level, count in risk_dist.items():
                        writer.writerow([risk_level.title(), count])
                    writer.writerow([])
            
            # Document Health
            if "document_health" in dashboard_data and dashboard_data["document_health"]:
                health = dashboard_data["document_health"]
                writer.writerow(["Document Health"])
                writer.writerow(["Metric", "Value"])
                writer.writerow(["Average Confidence", f"{health.get('average_confidence', 0):.2f}"])
                writer.writerow(["Processing Success Rate", f"{health.get('processing_success_rate', 0):.1f}%"])
                writer.writerow(["Metadata Completeness", f"{health.get('metadata_completeness', 0):.1f}%"])
                writer.writerow([])
            
            # Recent Uploads
            if "recent_uploads" in dashboard_data and dashboard_data["recent_uploads"]:
                writer.writerow(["Recent Uploads"])
                writer.writerow(["Filename", "Type", "Jurisdiction", "Industry", "Upload Date"])
                for doc in dashboard_data["recent_uploads"][:10]:
                    upload_date = doc.get("upload_date", "")
                    if upload_date:
                        try:
                            date_obj = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                            formatted_date = date_obj.strftime('%Y-%m-%d')
                        except:
                            formatted_date = upload_date
                    else:
                        formatted_date = "Unknown"
                    
                    writer.writerow([
                        doc.get("filename", ""),
                        doc.get("agreement_type", ""),
                        doc.get("jurisdiction", ""),
                        doc.get("industry", ""),
                        formatted_date
                    ])
            
            csv_content = output.getvalue()
            output.close()
            return csv_content
            
        except Exception as e:
            logger.error(f"Error exporting dashboard to CSV: {str(e)}")
            return ""
    
    def export_dashboard_to_pdf(self, dashboard_data: Dict[str, Any]) -> bytes:
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1
            )
            story.append(Paragraph("Legal Dashboard Report", title_style))
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
            story.append(Spacer(1, 20))
            
            # Document Summary
            story.append(Paragraph("Document Summary", styles['Heading2']))
            summary_data = [["Metric", "Value"]]
            summary_data.append(["Total Documents", str(dashboard_data.get("total_documents", 0))])
            
            if "total_value" in dashboard_data and dashboard_data["total_value"]:
                summary_data.append(["Total Value", f"${dashboard_data['total_value']:,.2f}"])
            
            summary_table = Table(summary_data, colWidths=[2*inch, 1*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Agreement Types
            if "agreement_types" in dashboard_data and dashboard_data["agreement_types"]:
                story.append(Paragraph("Agreement Types", styles['Heading2']))
                agreement_data = [["Type", "Count"]]
                for agreement_type, count in dashboard_data["agreement_types"].items():
                    agreement_data.append([agreement_type, str(count)])
                
                agreement_table = Table(agreement_data, colWidths=[3*inch, 1*inch])
                agreement_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(agreement_table)
                story.append(Spacer(1, 20))
            
            # Jurisdictions
            if "jurisdictions" in dashboard_data and dashboard_data["jurisdictions"]:
                story.append(Paragraph("Jurisdictions", styles['Heading2']))
                jurisdiction_data = [["Jurisdiction", "Count"]]
                for jurisdiction, count in dashboard_data["jurisdictions"].items():
                    jurisdiction_data.append([jurisdiction, str(count)])
                
                jurisdiction_table = Table(jurisdiction_data, colWidths=[3*inch, 1*inch])
                jurisdiction_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(jurisdiction_table)
                story.append(Spacer(1, 20))
            
            # Industries
            if "industries" in dashboard_data and dashboard_data["industries"]:
                story.append(Paragraph("Industries", styles['Heading2']))
                industry_data = [["Industry", "Count"]]
                for industry, count in dashboard_data["industries"].items():
                    industry_data.append([industry, str(count)])
                
                industry_table = Table(industry_data, colWidths=[3*inch, 1*inch])
                industry_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(industry_table)
                story.append(Spacer(1, 20))
            
            # Risk Analysis
            if "risk_analysis" in dashboard_data and dashboard_data["risk_analysis"]:
                risk_dist = dashboard_data["risk_analysis"].get("distribution", {})
                if risk_dist:
                    story.append(Paragraph("Risk Analysis", styles['Heading2']))
                    risk_data = [["Risk Level", "Count"]]
                    for risk_level, count in risk_dist.items():
                        risk_data.append([risk_level.title(), str(count)])
                    
                    risk_table = Table(risk_data, colWidths=[2*inch, 1*inch])
                    risk_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(risk_table)
                    story.append(Spacer(1, 20))
            
            # Document Health
            if "document_health" in dashboard_data and dashboard_data["document_health"]:
                health = dashboard_data["document_health"]
                story.append(Paragraph("Document Health", styles['Heading2']))
                health_data = [["Metric", "Value"]]
                health_data.append(["Average Confidence", f"{health.get('average_confidence', 0):.2f}"])
                health_data.append(["Processing Success Rate", f"{health.get('processing_success_rate', 0):.1f}%"])
                health_data.append(["Metadata Completeness", f"{health.get('metadata_completeness', 0):.1f}%"])
                
                health_table = Table(health_data, colWidths=[2*inch, 1*inch])
                health_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(health_table)
                story.append(Spacer(1, 20))
            
            # Recent Uploads
            if "recent_uploads" in dashboard_data and dashboard_data["recent_uploads"]:
                story.append(Paragraph("Recent Uploads", styles['Heading2']))
                upload_data = [["Filename", "Type", "Jurisdiction", "Upload Date"]]
                for doc in dashboard_data["recent_uploads"][:10]:
                    upload_date = doc.get("upload_date", "")
                    if upload_date:
                        try:
                            date_obj = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                            formatted_date = date_obj.strftime('%Y-%m-%d')
                        except:
                            formatted_date = upload_date
                    else:
                        formatted_date = "Unknown"
                    
                    upload_data.append([
                        doc.get("filename", "")[:30],
                        doc.get("agreement_type", ""),
                        doc.get("jurisdiction", ""),
                        formatted_date
                    ])
                
                upload_table = Table(upload_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch])
                upload_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(upload_table)
            
            doc.build(story)
            pdf_content = buffer.getvalue()
            buffer.close()
            return pdf_content
            
        except Exception as e:
            logger.error(f"Error exporting dashboard to PDF: {str(e)}")
            return b""
    
    def export_query_results_to_csv(self, query_response: Dict[str, Any]) -> str:
        try:
            output = io.StringIO()
            writer = csv.writer(output)
            
            writer.writerow(["Query Results Report"])
            writer.writerow([f"Query: {query_response.get('question', '')}"])
            writer.writerow([f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
            writer.writerow([f"Total Results: {query_response.get('total_results', 0)}"])
            writer.writerow([])
            
            if query_response.get("results"):
                writer.writerow([
                    "Filename", "Type", "Jurisdiction", "Industry", "Geography",
                    "Risk Level", "Compliance Status", "Confidence", "Upload Date"
                ])
                
                for result in query_response["results"]:
                    ai_insights = result.get("ai_insights", {})
                    writer.writerow([
                        result.get("filename", ""),
                        result.get("agreement_type", ""),
                        result.get("jurisdiction", ""),
                        result.get("industry", ""),
                        result.get("geography", ""),
                        ai_insights.get("risk_level", ""),
                        ai_insights.get("compliance_status", ""),
                        f"{ai_insights.get('confidence_score', 0):.2f}",
                        result.get("upload_date", "")
                    ])
            
            csv_content = output.getvalue()
            output.close()
            return csv_content
            
        except Exception as e:
            logger.error(f"Error exporting query results to CSV: {str(e)}")
            return ""

    def export_documents_to_csv(self, documents: List[Any]) -> str:
        try:
            output = io.StringIO()
            writer = csv.writer(output)
            
            writer.writerow(["Legal Documents Report"])
            writer.writerow([f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
            writer.writerow([f"Total Documents: {len(documents)}"])
            writer.writerow([])
            
            writer.writerow([
                "Filename", "Type", "Jurisdiction", "Industry", "Geography",
                "File Size", "Upload Date", "Risk Level", "Compliance Status", "Confidence"
            ])
            
            for doc in documents:
                ai_insights = getattr(doc, 'ai_insights', {})
                writer.writerow([
                    getattr(doc.metadata, 'filename', ''),
                    getattr(doc.metadata, 'agreement_type', ''),
                    getattr(doc.metadata, 'jurisdiction', ''),
                    getattr(doc.metadata, 'industry', ''),
                    getattr(doc.metadata, 'geography', ''),
                    getattr(doc.metadata, 'file_size', ''),
                    getattr(doc.metadata, 'upload_date', ''),
                    getattr(ai_insights, 'risk_assessment', ''),
                    getattr(ai_insights, 'compliance_status', ''),
                    getattr(ai_insights, 'confidence_score', '')
                ])
            
            csv_content = output.getvalue()
            output.close()
            return csv_content
            
        except Exception as e:
            logger.error(f"Error exporting documents to CSV: {str(e)}")
            return ""
