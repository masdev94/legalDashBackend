import re
from typing import List, Dict, Any, Optional
from loguru import logger
from app.models.document import Document, QueryRequest, QueryResponse, StructuredComparison
from datetime import datetime

class QueryService:
    
    def __init__(self):
        self.documents_storage = []
        
        # Enhanced query patterns for intent recognition
        self.query_patterns = {
            'agreement_type': [
                r'\b(?:which|what|show|find|list)\s+(?:agreements?|contracts?|documents?)\s+(?:are|is)\s+(?:of\s+)?type\s+(\w+)',
                r'\b(?:agreements?|contracts?)\s+(?:of\s+)?type\s+(\w+)',
                r'\b(?:show|find|list)\s+(\w+)\s+(?:agreements?|contracts?)',
                r'\b(?:all|every|any)\s+(\w+)\s+(?:agreements?|contracts?)',
                r'\b(?:(\w+)\s+(?:agreements?|contracts?))',
            ],
            'jurisdiction': [
                r'\b(?:which|what|show|find|list)\s+(?:agreements?|contracts?|documents?)\s+(?:are|is)\s+(?:governed\s+by|subject\s+to)\s+(\w+)',
                r'\b(?:agreements?|contracts?)\s+(?:governed\s+by|subject\s+to)\s+(\w+)',
                r'\b(?:show|find|list)\s+(?:documents?)\s+(?:in|from)\s+(\w+)',
                r'\b(?:(\w+)\s+(?:law|jurisdiction|governing))',
                r'\b(?:documents?\s+(?:in|from)\s+(\w+))',
            ],
            'industry': [
                r'\b(?:which|what|show|find|list)\s+(?:agreements?|contracts?|documents?)\s+(?:are|is)\s+(?:in|related\s+to)\s+(?:the\s+)?(\w+)',
                r'\b(?:agreements?|contracts?)\s+(?:in|related\s+to)\s+(?:the\s+)?(\w+)',
                r'\b(?:(\w+)\s+(?:industry|sector|business))',
                r'\b(?:documents?\s+(?:in|related\s+to)\s+(\w+))',
            ],
            'value_range': [
                r'\b(?:which|what|show|find|list)\s+(?:agreements?|contracts?|documents?)\s+(?:are|is)\s+(?:worth|valued\s+at)\s+(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(\w+)',
                r'\b(?:agreements?|contracts?)\s+(?:worth|valued\s+at)\s+(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(\w+)',
                r'\b(?:documents?\s+(?:worth|valued\s+at)\s+(\d+(?:,\d{3})*(?:\.\d{2})?))',
            ],
            'date_range': [
                r'\b(?:which|what|show|find|list)\s+(?:agreements?|contracts?|documents?)\s+(?:are|is)\s+(?:signed|effective|expired)\s+(?:in|during|between)\s+(\w+)',
                r'\b(?:agreements?|contracts?)\s+(?:signed|effective|expired)\s+(?:in|during|between)\s+(\w+)',
                r'\b(?:documents?\s+(?:signed|effective|expired)\s+(?:in|during|between)\s+(\w+))',
            ],
            'comparison': [
                r'\b(?:compare|comparison|difference|similarity|versus|vs)\s+(?:between|among|across)\s+([^.]*?)\b',
                r'\b(?:how\s+do|what\s+are\s+the\s+differences|similarities)\s+(?:between|among|across)\s+([^.]*?)\b',
                r'\b(?:compare|comparison|difference|similarity)\s+(\w+)',
            ],
            'risk_analysis': [
                r'\b(?:risk|risky|high\s+risk|low\s+risk)\s+(?:agreements?|contracts?|documents?)\b',
                r'\b(?:which|what)\s+(?:agreements?|contracts?)\s+(?:have|contain)\s+(?:high|low)\s+risk\b',
                r'\b(?:analyze|analysis)\s+(?:risk|risks)\b',
                r'\b(?:risk\s+assessment|risk\s+analysis)\b',
            ],
            'compliance_check': [
                r'\b(?:compliance|compliant|non\s*compliant)\s+(?:agreements?|contracts?|documents?)\b',
                r'\b(?:which|what)\s+(?:agreements?|contracts?)\s+(?:are|is)\s+(?:compliant|non\s*compliant)\b',
                r'\b(?:compliance\s+check|compliance\s+status)\b',
                r'\b(?:analyze|analysis)\s+(?:compliance)\b',
            ],
            'trend_analysis': [
                r'\b(?:trend|trends|pattern|patterns)\s+(?:in|of|across)\s+(\w+)',
                r'\b(?:analyze|analysis)\s+(?:trends?|patterns?)\b',
                r'\b(?:what\s+are\s+the\s+trends?|patterns?)\b',
                r'\b(?:trend\s+analysis|pattern\s+analysis)\b',
            ],
            'summary_request': [
                r'\b(?:summarize|summary|overview|summary\s+of)\s+(\w+)',
                r'\b(?:give\s+me\s+a\s+summary|overview)\b',
                r'\b(?:what\s+is\s+the\s+summary|overview)\b',
            ],
        }

    def add_documents(self, documents: List[Document]) -> None:
        self.documents_storage.extend(documents)
        logger.info(f"Added {len(documents)} documents to query service")

    def remove_document(self, document_id: str) -> bool:
        """Remove a document from the query service storage"""
        try:
            for i, doc in enumerate(self.documents_storage):
                if doc.id == document_id:
                    removed_doc = self.documents_storage.pop(i)
                    logger.info(f"Removed document {document_id} from query service")
                    return True
            
            logger.warning(f"Document {document_id} not found in query service")
            return False
            
        except Exception as e:
            logger.error(f"Error removing document {document_id} from query service: {str(e)}")
            return False

    def query_documents(self, question: str, documents: List[Document] = None) -> Dict[str, Any]:
        try:
            logger.info(f"Processing legacy query: {question}")
            
            # Use provided documents or fall back to storage
            target_documents = documents if documents is not None else self.documents_storage
            
            if not target_documents:
                return {
                    "question": question,
                    "results": [],
                    "total_results": 0,
                    "query_analysis": {"intent": "unknown", "entities": []}
                }
            
            # Analyze query intent
            query_analysis = self._analyze_query(question)
            
            # Filter documents based on query
            filtered_documents = self._filter_documents(question, target_documents, query_analysis)
            
            # Format results
            results = []
            for doc in filtered_documents:
                results.append({
                    "id": doc.id,
                    "filename": doc.metadata.filename,
                    "agreement_type": doc.metadata.agreement_type.value if doc.metadata.agreement_type else "Unknown",
                    "jurisdiction": doc.metadata.jurisdiction.value if doc.metadata.jurisdiction else "Unknown",
                    "industry": doc.metadata.industry.value if doc.metadata.industry else "Unknown",
                    "geography": doc.metadata.geography.value if doc.metadata.geography else "Unknown",
                    "governing_law": doc.metadata.governing_law,
                    "parties": doc.metadata.parties,
                    "effective_date": doc.metadata.effective_date.isoformat() if doc.metadata.effective_date else None,
                    "expiration_date": doc.metadata.expiration_date.isoformat() if doc.metadata.expiration_date else None,
                    "value": doc.metadata.value,
                    "currency": doc.metadata.currency,
                    "upload_date": doc.metadata.upload_date.isoformat(),
                })
            
            return {
                "question": question,
                "results": results,
                "total_results": len(results),
                "query_analysis": query_analysis
            }
            
        except Exception as e:
            logger.error(f"Query processing error: {str(e)}")
            return {
                "question": question,
                "results": [],
                "total_results": 0,
                "query_analysis": {"intent": "error", "entities": [], "error": str(e)}
            }

    async def query_documents_enhanced(self, request: QueryRequest, documents: List[Document] = None) -> QueryResponse:
        try:
            logger.info(f"Processing enhanced query: {request.question}")
            if request.filters:
                logger.info(f"Filters applied: {request.filters}")
            
            # Use provided documents or fall back to storage
            target_documents = documents if documents is not None else self.documents_storage
            
            if not target_documents:
                return QueryResponse(
                    question=request.question,
                    results=[],
                    total_results=0,
                    structured_comparisons=[],
                    document_analysis=None,
                    query_analysis={"intent": "no_documents", "entities": [], "confidence": 0.0}
                )
            
            # Analyze query intent
            query_analysis = self._analyze_enhanced_query(request.question)
            
            # Filter documents based on query
            filtered_documents = self._filter_documents_enhanced(request.question, target_documents, query_analysis, request.filters)
            
            logger.info(f"Documents after filtering: {len(filtered_documents)} out of {len(target_documents)}")
            
            # Generate structured comparisons if requested
            structured_comparisons = []
            if request.comparison_type or 'comparison' in query_analysis.get('intent', ''):
                structured_comparisons = self._generate_structured_comparisons(filtered_documents, request.question)
            
            # Format results with enhanced metadata
            results = []
            for doc in filtered_documents:
                result = {
                    "id": doc.id,
                    "filename": doc.metadata.filename,
                    "agreement_type": doc.metadata.agreement_type.value if doc.metadata.agreement_type else "Unknown",
                    "jurisdiction": doc.metadata.jurisdiction.value if doc.metadata.jurisdiction else "Unknown",
                    "industry": doc.metadata.industry.value if doc.metadata.industry else "Unknown",
                    "geography": doc.metadata.geography.value if doc.metadata.geography else "Unknown",
                    "governing_law": doc.metadata.governing_law,
                    "parties": doc.metadata.parties,
                    "effective_date": doc.metadata.effective_date.isoformat() if doc.metadata.effective_date else None,
                    "expiration_date": doc.metadata.expiration_date.isoformat() if doc.metadata.expiration_date else None,
                    "value": doc.metadata.value,
                    "currency": doc.metadata.currency,
                    "upload_date": doc.metadata.upload_date.isoformat(),
                }
                
                # Add AI insights if available
                if hasattr(doc, 'ai_insights') and doc.ai_insights:
                    result["ai_insights"] = {
                        "risk_level": doc.ai_insights.risk_assessment.value.upper() if doc.ai_insights.risk_assessment else "Unknown",
                        "compliance_status": doc.ai_insights.compliance_status.value if doc.ai_insights.compliance_status else "Unknown",
                        "confidence_score": doc.ai_insights.confidence_score,
                        "summary": doc.ai_insights.summary
                    }
                
                results.append(result)
            
            # Generate document analysis if requested or if analysis keywords detected
            document_analysis = None
            if (request.include_analysis or 
                query_analysis.get('analysis_requested') or 
                any(word in request.question.lower() for word in ['analyze', 'analysis', 'insight', 'trend', 'pattern'])):
                document_analysis = self._generate_document_analysis(filtered_documents, request.question)
            
            return QueryResponse(
                question=request.question,
                results=results,
                total_results=len(results),
                structured_comparisons=structured_comparisons,
                document_analysis=document_analysis,
                query_analysis=query_analysis
            )
            
        except Exception as e:
            logger.error(f"Enhanced query processing error: {str(e)}")
            return QueryResponse(
                question=request.question,
                results=[],
                total_results=0,
                structured_comparisons=[],
                document_analysis=None,
                query_analysis={"intent": "error", "entities": [], "confidence": 0.0, "error": str(e)}
            )

    def _analyze_query(self, question: str) -> Dict[str, Any]:
        question_lower = question.lower()
        
        intent = "general_search"
        entities = []
        
        # Check for specific query patterns
        for intent_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, question_lower, re.IGNORECASE)
                if matches:
                    intent = intent_type
                    entities.extend(matches)
                    break
        
        return {
            "intent": intent,
            "entities": entities,
            "confidence": 0.8 if entities else 0.3
        }

    def _analyze_enhanced_query(self, question: str) -> Dict[str, Any]:
        question_lower = question.lower()
        
        intent = "general_search"
        entities = []
        comparison_requested = False
        analysis_requested = False
        summary_requested = False
        
        # Check for specific query patterns
        for intent_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, question_lower, re.IGNORECASE)
                if matches:
                    intent = intent_type
                    entities.extend(matches)
                    
                    # Check for comparison intent
                    if intent_type == 'comparison':
                        comparison_requested = True
                    
                    # Check for analysis intent
                    if intent_type in ['risk_analysis', 'compliance_check', 'trend_analysis']:
                        analysis_requested = True
                    
                    # Check for summary intent
                    if intent_type == 'summary_request':
                        summary_requested = True
                    
                    break
        
        # Check for comparison keywords
        comparison_keywords = ['compare', 'comparison', 'difference', 'similarity', 'versus', 'vs', 'between', 'among']
        if any(keyword in question_lower for keyword in comparison_keywords):
            comparison_requested = True
        
        # Check for analysis keywords
        analysis_keywords = ['analyze', 'analysis', 'insight', 'trend', 'pattern', 'risk', 'compliance', 'assess', 'evaluate']
        if any(keyword in question_lower for keyword in analysis_keywords):
            analysis_requested = True
        
        # Check for summary keywords
        summary_keywords = ['summarize', 'summary', 'overview', 'brief', 'gist']
        if any(keyword in question_lower for keyword in summary_keywords):
            summary_requested = True
        
        # Determine complexity based on multiple factors
        complexity = "low"
        if comparison_requested or analysis_requested or summary_requested:
            complexity = "high"
        elif len(question.split()) > 8 or len(entities) > 2:
            complexity = "medium"
        
        # Calculate confidence based on pattern matches and entities
        confidence = 0.3  # Base confidence
        if entities:
            confidence += 0.3
        if intent != "general_search":
            confidence += 0.2
        if comparison_requested or analysis_requested:
            confidence += 0.2
        
        return {
            "intent": intent,
            "entities": entities,
            "confidence": min(confidence, 1.0),
            "comparison_requested": comparison_requested,
            "analysis_requested": analysis_requested,
            "summary_requested": summary_requested,
            "complexity": complexity
        }

    def _filter_documents_enhanced(self, question: str, documents: List[Document], query_analysis: Dict[str, Any], filters: Dict[str, Any] = None) -> List[Document]:
        if not query_analysis.get("entities") and query_analysis.get("intent") == "general_search":
            # Apply filters even for general search
            if filters and any(filters.values()):
                documents = self._apply_filters(documents, filters)
            return documents[:20]  # Return first 20 if no specific entities
        
        # Apply filters first
        if filters and any(filters.values()):
            documents = self._apply_filters(documents, filters)
        
        filtered = []
        question_lower = question.lower()
        question_words = set(word.lower() for word in question.split() if len(word) > 2)
        
        for doc in documents:
            score = 0
            
            # Enhanced metadata scoring
            if doc.metadata.agreement_type:
                agreement_type_lower = doc.metadata.agreement_type.value.lower()
                if agreement_type_lower in question_lower:
                    score += 8  # Exact match
                elif any(word in agreement_type_lower for word in question_words):
                    score += 5  # Partial match
                elif any(word in agreement_type_lower for word in ['contract', 'agreement', 'nda', 'msa']):
                    score += 2  # Generic legal terms
            
            if doc.metadata.jurisdiction:
                jurisdiction_lower = doc.metadata.jurisdiction.value.lower()
                if jurisdiction_lower in question_lower:
                    score += 8  # Exact match
                elif any(word in jurisdiction_lower for word in question_words):
                    score += 5  # Partial match
                elif any(word in jurisdiction_lower for word in ['uk', 'usa', 'uae', 'singapore']):
                    score += 2  # Common jurisdictions
            
            if doc.metadata.industry:
                industry_lower = doc.metadata.industry.value.lower()
                if industry_lower in question_lower:
                    score += 6  # Exact match
                elif any(word in industry_lower for word in question_words):
                    score += 4  # Partial match
            
            if doc.metadata.geography:
                geography_lower = doc.metadata.geography.value.lower()
                if geography_lower in question_lower:
                    score += 6  # Exact match
                elif any(word in geography_lower for word in question_words):
                    score += 4  # Partial match
            
            # Enhanced content scoring
            if doc.metadata.governing_law and doc.metadata.governing_law.lower() in question_lower:
                score += 4
            
            # Party matching
            for party in doc.metadata.parties:
                if party.lower() in question_lower:
                    score += 3
            
            # AI insights scoring
            if hasattr(doc, 'ai_insights') and doc.ai_insights:
                if query_analysis.get("analysis_requested"):
                    score += 3  # Boost documents with AI insights for analysis queries
                
                # Risk-based scoring
                if 'risk' in question_lower and doc.ai_insights.risk_assessment:
                    if 'high' in question_lower and doc.ai_insights.risk_assessment.value == 'HIGH':
                        score += 4
                    elif 'low' in question_lower and doc.ai_insights.risk_assessment.value == 'LOW':
                        score += 4
                    elif 'medium' in question_lower and doc.ai_insights.risk_assessment.value == 'MEDIUM':
                        score += 4
                
                # Compliance-based scoring
                if 'compliance' in question_lower and doc.ai_insights.compliance_status:
                    if 'compliant' in question_lower and doc.ai_insights.compliance_status.value == 'COMPLIANT':
                        score += 4
                    elif 'non' in question_lower and 'compliant' in question_lower and doc.ai_insights.compliance_status.value == 'NON_COMPLIANT':
                        score += 4
                    elif 'pending' in question_lower and doc.ai_insights.compliance_status.value == 'PENDING_REVIEW':
                        score += 4
            
            # Text content relevance
            if doc.extracted_text:
                text_lower = doc.extracted_text.lower()
                
                # Check for entity matches in text
                for entity in query_analysis.get("entities", []):
                    if entity.lower() in text_lower:
                        score += 2
                
                # Semantic matching for longer queries
                if len(question_words) > 3:
                    text_words = set(text_lower.split())
                    common_words = question_words & text_words
                    score += len(common_words) * 0.5
                
                # Boost for documents with substantial content
                if len(text_lower) > 1000:
                    score += 1
                elif len(text_lower) > 500:
                    score += 0.5
            
            # Intent-specific scoring
            if query_analysis.get("intent") == "summary_request":
                if hasattr(doc, 'ai_insights') and doc.ai_insights and doc.ai_insights.summary:
                    score += 2  # Boost documents with AI summaries
            
            if query_analysis.get("intent") == "trend_analysis":
                if doc.metadata.upload_date:
                    score += 1  # Boost documents with dates for trend analysis
            
            if score > 0:
                filtered.append((doc, score))
        
        # Sort by relevance score
        filtered.sort(key=lambda x: x[1], reverse=True)
        
        # Return top documents, but ensure we have at least some results
        max_results = min(30, len(filtered))
        return [doc for doc, score in filtered[:max_results]]

    def _generate_structured_comparisons(self, documents: List[Document], question: str) -> List[StructuredComparison]:
        comparisons = []
        
        try:
            if len(documents) < 2:
                return comparisons
            
            # Group documents by key attributes for comparison
            comparison_groups = self._group_documents_for_comparison(documents)
            
            for group_type, group_docs in comparison_groups.items():
                if len(group_docs) >= 2:
                    comparison = self._create_comparison(group_type, group_docs, question)
                    if comparison:
                        comparisons.append(comparison)
            
            return comparisons
            
        except Exception as e:
            logger.error(f"Error generating structured comparisons: {str(e)}")
            return []

    def _group_documents_for_comparison(self, documents: List[Document]) -> Dict[str, List[Document]]:
        groups = {}
        
        # Group by agreement type
        agreement_groups = {}
        for doc in documents:
            if doc.metadata.agreement_type:
                agreement_type = doc.metadata.agreement_type.value
                if agreement_type not in agreement_groups:
                    agreement_groups[agreement_type] = []
                agreement_groups[agreement_type].append(doc)
        
        for agreement_type, docs in agreement_groups.items():
            if len(docs) >= 2:
                groups[f"agreement_type_{agreement_type}"] = docs
        
        # Group by jurisdiction
        jurisdiction_groups = {}
        for doc in documents:
            if doc.metadata.jurisdiction:
                jurisdiction = doc.metadata.jurisdiction.value
                if jurisdiction not in jurisdiction_groups:
                    jurisdiction_groups[jurisdiction] = []
                jurisdiction_groups[jurisdiction].append(doc)
        
        for jurisdiction, docs in jurisdiction_groups.items():
            if len(docs) >= 2:
                groups[f"jurisdiction_{jurisdiction}"] = docs
        
        # Group by industry
        industry_groups = {}
        for doc in documents:
            if doc.metadata.industry:
                industry = doc.metadata.industry.value
                if industry not in industry_groups:
                    industry_groups[industry] = []
                industry_groups[industry].append(doc)
        
        for industry, docs in industry_groups.items():
            if len(docs) >= 2:
                groups[f"industry_{industry}"] = docs
        
        return groups

    def _create_comparison(self, group_type: str, documents: List[Document], question: str) -> Optional[StructuredComparison]:
        try:
            if len(documents) < 2:
                return None
            
            # Extract key differences and similarities
            similarities = self._find_similarities(documents)
            differences = self._find_differences(documents)
            
            # Generate insights
            insights = self._generate_comparison_insights(documents, similarities, differences)
            
            # Calculate confidence
            confidence = self._calculate_comparison_confidence(documents, similarities, differences)
            
            # Create metadata comparison
            metadata_comparison = self._create_metadata_comparison(documents)
            
            comparison = StructuredComparison(
                comparison_type=group_type,
                documents_involved=[doc.metadata.filename for doc in documents],
                similarities=similarities,
                differences=differences,
                insights=insights,
                confidence_score=confidence,
                metadata_comparison=metadata_comparison
            )
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error creating comparison: {str(e)}")
            return None

    def _find_similarities(self, documents: List[Document]) -> List[str]:
        similarities = []
        
        try:
            # Check for common agreement types
            agreement_types = [doc.metadata.agreement_type.value for doc in documents if doc.metadata.agreement_type]
            if len(set(agreement_types)) == 1:
                similarities.append(f"All documents are {agreement_types[0]} agreements")
            
            # Check for common jurisdictions
            jurisdictions = [doc.metadata.jurisdiction.value for doc in documents if doc.metadata.jurisdiction]
            if len(set(jurisdictions)) == 1:
                similarities.append(f"All documents are governed by {jurisdictions[0]} law")
            
            # Check for common industries
            industries = [doc.metadata.industry.value for doc in documents if doc.metadata.industry]
            if len(set(industries)) == 1:
                similarities.append(f"All documents are in the {industries[0]} industry")
            
            # Check for common risk levels
            risk_levels = [doc.ai_insights.risk_assessment.value for doc in documents if doc.ai_insights and doc.ai_insights.risk_assessment]
            if len(set(risk_levels)) == 1:
                similarities.append(f"All documents have {risk_levels[0]} risk level")
            
            return similarities
            
        except Exception as e:
            logger.error(f"Error finding similarities: {str(e)}")
            return []

    def _find_differences(self, documents: List[Document]) -> List[str]:
        differences = []
        
        try:
            # Check for different values
            values = [doc.metadata.value for doc in documents if doc.metadata.value]
            if len(set(values)) > 1:
                min_value = min(values)
                max_value = max(values)
                differences.append(f"Contract values range from {min_value} to {max_value}")
            
            # Check for different parties
            all_parties = []
            for doc in documents:
                all_parties.extend(doc.metadata.parties)
            unique_parties = list(set(all_parties))
            if len(unique_parties) > len(documents):
                differences.append(f"Documents involve {len(unique_parties)} different parties")
            
            # Check for different risk levels
            risk_levels = [doc.ai_insights.risk_assessment.value for doc in documents if doc.ai_insights and doc.ai_insights.risk_assessment]
            if len(set(risk_levels)) > 1:
                differences.append(f"Documents have varying risk levels: {', '.join(set(risk_levels))}")
            
            return differences
            
        except Exception as e:
            logger.error(f"Error finding differences: {str(e)}")
            return []

    def _generate_comparison_insights(self, documents: List[Document], similarities: List[str], differences: List[str]) -> str:
        try:
            insights = []
            
            if similarities:
                insights.append(f"Key similarities: {'; '.join(similarities)}")
            
            if differences:
                insights.append(f"Key differences: {'; '.join(differences)}")
            
            # Add business insights
            total_value = sum(doc.metadata.value for doc in documents if doc.metadata.value)
            if total_value > 0:
                insights.append(f"Combined contract value: {total_value}")
            
            # Add risk insights
            high_risk_count = sum(1 for doc in documents if doc.ai_insights and doc.ai_insights.risk_assessment and doc.ai_insights.risk_assessment.value == 'High')
            if high_risk_count > 0:
                insights.append(f"{high_risk_count} high-risk documents identified")
            
            return ' '.join(insights) if insights else "Standard comparison analysis"
            
        except Exception as e:
            logger.error(f"Error generating comparison insights: {str(e)}")
            return "Comparison insights unavailable"

    def _calculate_comparison_confidence(self, documents: List[Document], similarities: List[str], differences: List[str]) -> float:
        try:
            confidence_factors = 0
            total_factors = 0
            
            # Document quality factor
            for doc in documents:
                if doc.ai_insights and doc.ai_insights.confidence_score:
                    confidence_factors += doc.ai_insights.confidence_score
                    total_factors += 1
            
            # Metadata completeness factor
            metadata_complete = 0
            for doc in documents:
                if doc.metadata.agreement_type and doc.metadata.jurisdiction and doc.metadata.industry:
                    metadata_complete += 1
            total_factors += 1
            if metadata_complete > 0:
                confidence_factors += (metadata_complete / len(documents))
            
            # Comparison quality factor
            total_factors += 1
            if similarities or differences:
                confidence_factors += 1
            
            if total_factors > 0:
                confidence = confidence_factors / total_factors
                return round(confidence, 2)
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"Error calculating comparison confidence: {str(e)}")
            return 0.5

    def _create_metadata_comparison(self, documents: List[Document]) -> Dict[str, Any]:
        try:
            comparison = {
                "agreement_types": {},
                "jurisdictions": {},
                "industries": {},
                "total_documents": len(documents),
                "value_range": {},
                "risk_distribution": {},
                "compliance_distribution": {}
            }
            
            # Count agreement types
            for doc in documents:
                if doc.metadata.agreement_type:
                    agreement_type = doc.metadata.agreement_type.value
                    comparison["agreement_types"][agreement_type] = comparison["agreement_types"].get(agreement_type, 0) + 1
            
            # Count jurisdictions
            for doc in documents:
                if doc.metadata.jurisdiction:
                    jurisdiction = doc.metadata.jurisdiction.value
                    comparison["jurisdictions"][jurisdiction] = comparison["jurisdictions"].get(jurisdiction, 0) + 1
            
            # Count industries
            for doc in documents:
                if doc.metadata.industry:
                    industry = doc.metadata.industry.value
                    comparison["industries"][industry] = comparison["industries"].get(industry, 0) + 1
            
            # Value range
            values = [doc.metadata.value for doc in documents if doc.metadata.value]
            if values:
                comparison["value_range"] = {
                    "min": min(values),
                    "max": max(values),
                    "average": sum(values) / len(values)
                }
            
            # Risk distribution
            risk_counts = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
            for doc in documents:
                if doc.ai_insights and doc.ai_insights.risk_assessment:
                    risk_counts[doc.ai_insights.risk_assessment.value] += 1
            comparison["risk_distribution"] = risk_counts
            
            # Compliance distribution
            compliance_counts = {'Compliant': 0, 'Non-Compliant': 0, 'Pending Review': 0, 'Requires Action': 0}
            for doc in documents:
                if doc.ai_insights and doc.ai_insights.compliance_status:
                    compliance_counts[doc.ai_insights.compliance_status.value] += 1
            comparison["compliance_distribution"] = compliance_counts
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error creating metadata comparison: {str(e)}")
            return {}

    def _generate_document_analysis(self, documents: List[Document], question: str) -> Dict[str, Any]:
        try:
            if not documents:
                return None
            
            # Analyze the collection
            total_docs = len(documents)
            
            # Risk distribution
            risk_distribution = {}
            risk_scores = []
            for doc in documents:
                if hasattr(doc, 'ai_insights') and doc.ai_insights and doc.ai_insights.risk_assessment:
                    risk_level = doc.ai_insights.risk_assessment.value
                    risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
                    if hasattr(doc.ai_insights, 'confidence_score') and doc.ai_insights.confidence_score:
                        risk_scores.append(doc.ai_insights.confidence_score)
            
            # Compliance distribution
            compliance_distribution = {}
            compliance_scores = []
            for doc in documents:
                if hasattr(doc, 'ai_insights') and doc.ai_insights and doc.ai_insights.compliance_status:
                    compliance_status = doc.ai_insights.compliance_status.value
                    compliance_distribution[compliance_status] = compliance_distribution.get(compliance_status, 0) + 1
                    if hasattr(doc.ai_insights, 'confidence_score') and doc.ai_insights.confidence_score:
                        compliance_scores.append(doc.ai_insights.confidence_score)
            
            # Generate insights based on question
            question_lower = question.lower()
            key_findings = []
            
            if 'risk' in question_lower:
                if risk_distribution:
                    high_risk = risk_distribution.get('HIGH', 0)
                    if high_risk > 0:
                        key_findings.append(f"{high_risk} documents identified as high risk")
                    key_findings.append(f"Risk distribution: {risk_distribution}")
            
            if 'compliance' in question_lower:
                if compliance_distribution:
                    non_compliant = compliance_distribution.get('NON_COMPLIANT', 0) + compliance_distribution.get('REQUIRES_ACTION', 0)
                    if non_compliant > 0:
                        key_findings.append(f"{non_compliant} documents require compliance attention")
                    key_findings.append(f"Compliance distribution: {compliance_distribution}")
            
            if 'trend' in question_lower or 'pattern' in question_lower:
                # Analyze patterns across documents
                agreement_types = {}
                jurisdictions = {}
                for doc in documents:
                    if doc.metadata.agreement_type:
                        agreement_types[doc.metadata.agreement_type.value] = agreement_types.get(doc.metadata.agreement_type.value, 0) + 1
                    if doc.metadata.jurisdiction:
                        jurisdictions[doc.metadata.jurisdiction.value] = jurisdictions.get(doc.metadata.jurisdiction.value, 0) + 1
                
                if agreement_types:
                    most_common_type = max(agreement_types.items(), key=lambda x: x[1])
                    key_findings.append(f"Most common agreement type: {most_common_type[0]} ({most_common_type[1]} documents)")
                
                if jurisdictions:
                    most_common_jurisdiction = max(jurisdictions.items(), key=lambda x: x[1])
                    key_findings.append(f"Most common jurisdiction: {most_common_jurisdiction[0]} ({most_common_jurisdiction[1]} documents)")
            
            # Generate recommendations
            recommendations = []
            if risk_distribution.get('HIGH', 0) > 0:
                recommendations.append("Review high-risk documents immediately")
                recommendations.append("Consider risk mitigation strategies")
            
            if compliance_distribution.get('NON_COMPLIANT', 0) > 0 or compliance_distribution.get('REQUIRES_ACTION', 0) > 0:
                recommendations.append("Address compliance issues promptly")
                recommendations.append("Implement compliance monitoring")
            
            if len(documents) > 10:
                recommendations.append("Consider document categorization and tagging")
                recommendations.append("Implement regular review cycles")
            
            # Calculate average confidence
            all_scores = []
            for doc in documents:
                if hasattr(doc, 'ai_insights') and doc.ai_insights and hasattr(doc.ai_insights, 'confidence_score'):
                    if doc.ai_insights.confidence_score:
                        all_scores.append(doc.ai_insights.confidence_score)
            
            avg_confidence = sum(all_scores) / len(all_scores) if all_scores else 0.0
            
            return {
                "analysis_summary": f"Analysis of {total_docs} documents completed successfully",
                "key_findings": key_findings if key_findings else ["Standard document analysis completed"],
                "risk_assessment": {
                    "level": "HIGH" if risk_distribution.get('HIGH', 0) > 0 else "MEDIUM" if risk_distribution.get('MEDIUM', 0) > 0 else "LOW",
                    "factors": list(risk_distribution.keys()) if risk_distribution else [],
                    "score": avg_confidence
                },
                "compliance_check": {
                    "status": "REQUIRES_ACTION" if compliance_distribution.get('NON_COMPLIANT', 0) > 0 else "PENDING_REVIEW" if compliance_distribution.get('PENDING_REVIEW', 0) > 0 else "COMPLIANT",
                    "requirements": list(compliance_distribution.keys()) if compliance_distribution else [],
                    "score": avg_confidence
                },
                "business_implications": [
                    f"Total documents analyzed: {total_docs}",
                    f"Risk assessment completed: {len(risk_distribution)} risk levels identified",
                    f"Compliance status assessed: {len(compliance_distribution)} compliance levels identified"
                ],
                "recommendations": recommendations if recommendations else ["Continue monitoring document collection"],
                "confidence_score": avg_confidence,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating document analysis: {str(e)}")
            return {
                "analysis_summary": "Analysis failed - using fallback data",
                "key_findings": ["Analysis could not be completed"],
                "risk_assessment": {"level": "UNKNOWN", "factors": [], "score": 0.0},
                "compliance_check": {"status": "UNKNOWN", "requirements": [], "score": 0.0},
                "business_implications": ["Analysis failed"],
                "recommendations": ["Review documents manually"],
                "confidence_score": 0.0,
                "analysis_timestamp": datetime.now().isoformat()
            }

    def _filter_documents(self, question: str, documents: List[Document], query_analysis: Dict[str, Any]) -> List[Document]:
        if not query_analysis.get("entities"):
            return documents[:10]  # Return first 10 if no specific entities
        
        filtered = []
        question_lower = question.lower()
        
        for doc in documents:
            score = 0
            
            # Check agreement type
            if doc.metadata.agreement_type:
                if doc.metadata.agreement_type.value.lower() in question_lower:
                    score += 3
            
            # Check jurisdiction
            if doc.metadata.jurisdiction:
                if doc.metadata.jurisdiction.value.lower() in question_lower:
                    score += 3
            
            # Check industry
            if doc.metadata.industry:
                if doc.metadata.industry.value.lower() in question_lower:
                    score += 2
            
            # Check geography
            if doc.metadata.geography:
                if doc.metadata.geography.value.lower() in question_lower:
                    score += 2
            
            # Check governing law
            if doc.metadata.governing_law and doc.metadata.governing_law.lower() in question_lower:
                score += 2
            
            # Check parties
            for party in doc.metadata.parties:
                if party.lower() in question_lower:
                    score += 1
            
            # Check extracted text content
            if any(entity.lower() in doc.extracted_text.lower() for entity in query_analysis["entities"]):
                score += 1
            
            if score > 0:
                filtered.append(doc)
        
        # Sort by relevance score
        filtered.sort(key=lambda x: self._calculate_relevance_score(x, question_lower), reverse=True)
        
        return filtered[:20]  # Limit to top 20 results

    def _calculate_relevance_score(self, doc: Document, question: str) -> int:
        score = 0
        
        # Text content relevance
        if any(word in doc.extracted_text.lower() for word in question.split() if len(word) > 3):
            score += 1
        
        # Metadata relevance
        if doc.metadata.agreement_type and doc.metadata.agreement_type.value.lower() in question:
            score += 2
        
        if doc.metadata.jurisdiction and doc.metadata.jurisdiction.value.lower() in question:
            score += 2
        
        return score

    def _apply_filters(self, documents: List[Document], filters: Dict[str, Any]) -> List[Document]:
        """Apply filters to documents based on metadata"""
        if not filters or not any(filters.values()):
            return documents
        
        logger.info(f"Applying filters: {filters}")
        logger.info(f"Documents before filtering: {len(documents)}")
        
        filtered_docs = []
        
        for doc in documents:
            include_doc = True
            
            # Agreement Type filter
            if filters.get('agreement_type') and doc.metadata.agreement_type:
                if doc.metadata.agreement_type.value != filters['agreement_type']:
                    include_doc = False
                    logger.debug(f"Document {doc.metadata.filename} excluded by agreement_type filter: {doc.metadata.agreement_type.value} != {filters['agreement_type']}")
            
            # Jurisdiction filter
            if filters.get('jurisdiction') and doc.metadata.jurisdiction:
                if doc.metadata.jurisdiction.value != filters['jurisdiction']:
                    include_doc = False
                    logger.debug(f"Document {doc.metadata.filename} excluded by jurisdiction filter: {doc.metadata.jurisdiction.value} != {filters['jurisdiction']}")
            
            # Industry filter
            if filters.get('industry') and doc.metadata.industry:
                if doc.metadata.industry.value != filters['industry']:
                    include_doc = False
                    logger.debug(f"Document {doc.metadata.filename} excluded by industry filter: {doc.metadata.industry.value} != {filters['industry']}")
            
            # Geography filter
            if filters.get('geography') and doc.metadata.geography:
                if doc.metadata.geography.value != filters['geography']:
                    include_doc = False
                    logger.debug(f"Document {doc.metadata.filename} excluded by geography filter: {doc.metadata.geography.value} != {filters['geography']}")
            
            # File Type filter
            if filters.get('file_type') and doc.metadata.file_type:
                if doc.metadata.file_type.lower() != filters['file_type'].lower():
                    include_doc = False
                    logger.debug(f"Document {doc.metadata.filename} excluded by file_type filter: {doc.metadata.file_type} != {filters['file_type']}")
            
            # Date range filter (if implemented)
            if filters.get('date_from') and doc.metadata.upload_date:
                try:
                    from_date = datetime.fromisoformat(filters['date_from'])
                    if doc.metadata.upload_date < from_date:
                        include_doc = False
                        logger.debug(f"Document {doc.metadata.filename} excluded by date_from filter: {doc.metadata.upload_date} < {from_date}")
                except:
                    pass
            
            if filters.get('date_to') and doc.metadata.upload_date:
                try:
                    to_date = datetime.fromisoformat(filters['date_to'])
                    if doc.metadata.upload_date > to_date:
                        include_doc = False
                        logger.debug(f"Document {doc.metadata.filename} excluded by date_to filter: {doc.metadata.upload_date} > {to_date}")
                except:
                    pass
            
            if include_doc:
                filtered_docs.append(doc)
        
        logger.info(f"Documents after filtering: {len(filtered_docs)}")
        return filtered_docs

    def get_documents_summary(self) -> Dict[str, Any]:
        if not self.documents_storage:
            return {
                "total_documents": 0,
                "agreement_types": {},
                "jurisdictions": {},
                "industries": {},
                "geographies": {}
            }
        
        summary = {
            "total_documents": len(self.documents_storage),
            "agreement_types": {},
            "jurisdictions": {},
            "industries": {},
            "geographies": {}
        }
        
        for doc in self.documents_storage:
            # Count agreement types
            if doc.metadata.agreement_type:
                agreement_type = doc.metadata.agreement_type.value
                summary["agreement_types"][agreement_type] = summary["agreement_types"].get(agreement_type, 0) + 1
            
            # Count jurisdictions
            if doc.metadata.jurisdiction:
                jurisdiction = doc.metadata.jurisdiction.value
                summary["jurisdictions"][jurisdiction] = summary["jurisdictions"].get(jurisdiction, 0) + 1
            
            # Count industries
            if doc.metadata.industry:
                industry = doc.metadata.industry.value
                summary["industries"][industry] = summary["industries"].get(industry, 0) + 1
            
            # Count geographies
            if doc.metadata.geography:
                geography = doc.metadata.geography.value
                summary["geographies"][geography] = summary["geographies"].get(geography, 0) + 1
        
        return summary