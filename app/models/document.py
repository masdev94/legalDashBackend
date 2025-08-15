from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class AgreementType(str, Enum):
    NDA = "NDA"
    MSA = "MSA"
    FRANCHISE = "Franchise Agreement"
    EMPLOYMENT = "Employment Contract"
    LEASE = "Lease Agreement"
    PARTNERSHIP = "Partnership Agreement"
    SUPPLY = "Supply Agreement"
    SERVICE = "Service Agreement"
    LICENSING = "Licensing Agreement"
    MERGER = "Merger Agreement"
    ACQUISITION = "Acquisition Agreement"
    JOINT_VENTURE = "Joint Venture Agreement"
    DISTRIBUTION = "Distribution Agreement"
    CONFIDENTIALITY = "Confidentiality Agreement"
    NON_COMPETE = "Non-Compete Agreement"
    INTELLECTUAL_PROPERTY = "IP Agreement"
    OTHER = "Other"

class Jurisdiction(str, Enum):
    UAE = "UAE"
    UK = "UK"
    USA = "USA"
    DELAWARE = "Delaware"
    SINGAPORE = "Singapore"
    HONG_KONG = "Hong Kong"
    GERMANY = "Germany"
    FRANCE = "France"
    CANADA = "Canada"
    AUSTRALIA = "Australia"
    JAPAN = "Japan"
    SOUTH_KOREA = "South Korea"
    INDIA = "India"
    BRAZIL = "Brazil"
    MEXICO = "Mexico"
    OTHER = "Other"

class Industry(str, Enum):
    TECHNOLOGY = "Technology"
    HEALTHCARE = "Healthcare"
    FINANCE = "Finance"
    OIL_GAS = "Oil & Gas"
    REAL_ESTATE = "Real Estate"
    MANUFACTURING = "Manufacturing"
    RETAIL = "Retail"
    CONSULTING = "Consulting"
    TELECOMMUNICATIONS = "Telecommunications"
    AUTOMOTIVE = "Automotive"
    AEROSPACE = "Aerospace"
    ENERGY = "Energy"
    TRANSPORTATION = "Transportation"
    EDUCATION = "Education"
    MEDIA = "Media & Entertainment"
    OTHER = "Other"

class Geography(str, Enum):
    MIDDLE_EAST = "Middle East"
    EUROPE = "Europe"
    NORTH_AMERICA = "North America"
    ASIA_PACIFIC = "Asia Pacific"
    AFRICA = "Africa"
    SOUTH_AMERICA = "South America"
    CENTRAL_AMERICA = "Central America"
    CARIBBEAN = "Caribbean"
    OCEANIA = "Oceania"
    OTHER = "Other"

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class ComplianceStatus(str, Enum):
    COMPLIANT = "Compliant"
    NON_COMPLIANT = "Non-Compliant"
    PENDING_REVIEW = "Pending Review"
    REQUIRES_ACTION = "Requires Action"

class DocumentMetadata(BaseModel):
    filename: str
    file_size: int
    file_type: str
    upload_date: datetime
    agreement_type: Optional[AgreementType] = None
    jurisdiction: Optional[Jurisdiction] = None
    industry: Optional[Industry] = None
    geography: Optional[Geography] = None
    governing_law: Optional[str] = None
    parties: List[str] = Field(default_factory=list)
    effective_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    value: Optional[float] = None
    currency: Optional[str] = None
    
    # Enhanced metadata fields
    contract_duration: Optional[str] = None
    termination_clauses: Optional[List[str]] = Field(default_factory=list)
    key_obligations: Optional[List[str]] = Field(default_factory=list)
    risk_factors: Optional[List[str]] = Field(default_factory=list)
    compliance_requirements: Optional[List[str]] = Field(default_factory=list)
    renewal_terms: Optional[str] = None
    penalty_clauses: Optional[List[str]] = Field(default_factory=list)

class AIInsights(BaseModel):
    summary: Optional[str] = None
    key_terms: List[str] = Field(default_factory=list)
    risk_assessment: Optional[RiskLevel] = None
    compliance_status: Optional[ComplianceStatus] = None
    business_impact: Optional[str] = None
    recommendations: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.0)
    extracted_entities: Dict[str, List[str]] = Field(default_factory=dict)
    sentiment_analysis: Optional[str] = None
    complexity_score: Optional[float] = None

class Document(BaseModel):
    id: str
    metadata: DocumentMetadata
    content: Union[str, bytes]
    extracted_text: str
    processing_status: str = "completed"
    created_at: datetime
    updated_at: datetime
    
    raw_bytes: Optional[bytes] = None
    
    ai_insights: Optional[AIInsights] = None
    confidence_score: Optional[float] = None
    processing_errors: List[str] = Field(default_factory=list)

class QueryRequest(BaseModel):
    question: str = Field(..., description="Natural language question about the documents")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional filters")
    comparison_type: Optional[str] = Field(default=None, description="Type of comparison requested")
    include_analysis: bool = Field(default=True, description="Include AI analysis in response")

class StructuredComparison(BaseModel):
    comparison_type: str
    documents_involved: List[str]
    similarities: List[str]
    differences: List[str]
    insights: str
    confidence_score: float
    metadata_comparison: Dict[str, Any]

class QueryResponse(BaseModel):
    question: str
    results: List[Dict[str, Any]]
    total_results: int
    structured_comparisons: List[StructuredComparison] = Field(default_factory=list)
    document_analysis: Optional[Dict[str, Any]] = None
    query_analysis: Optional[Dict[str, Any]] = None

class DashboardData(BaseModel):
    agreement_types: Dict[str, int]
    jurisdictions: Dict[str, int]
    industries: Dict[str, int]
    geographies: Dict[str, int]
    total_documents: int
    total_value: Optional[float] = None
    date_range: Dict[str, str]
    recent_uploads: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Enhanced analytics
    trends_over_time: Dict[str, Any] = Field(default_factory=dict)
    risk_analysis: Dict[str, Any] = Field(default_factory=dict)
    compliance_metrics: Dict[str, Any] = Field(default_factory=dict)
    document_health: Dict[str, Any] = Field(default_factory=dict)
    ai_insights_summary: Optional[str] = None

class UploadResponse(BaseModel):
    message: str
    uploaded_files: List[str]
    failed_files: List[str]
    total_processed: int
    processing_time: float
    processing_summary: Optional[Dict[str, Any]] = None

class DocumentsListResponse(BaseModel):
    documents: List[Dict[str, Any]]
    total: int
    page: int
    size: int

class DocumentAnalysis(BaseModel):
    document_id: str
    filename: str
    analysis_summary: str
    key_findings: List[str]
    risk_assessment: Dict[str, Any]
    compliance_check: Dict[str, Any]
    business_implications: List[str]
    recommendations: List[str]
    confidence_score: float
    analysis_timestamp: datetime

class CrossDocumentAnalysis(BaseModel):
    analysis_type: str
    documents_analyzed: int
    key_insights: List[str]
    patterns_found: List[str]
    anomalies_detected: List[str]
    recommendations: List[str]
    risk_aggregation: Dict[str, Any]
    compliance_overview: Dict[str, Any]
    analysis_timestamp: datetime