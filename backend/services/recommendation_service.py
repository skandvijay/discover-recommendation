import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from models.models import Document, Query, User
from services.cache_service import CacheService
import logging

logger = logging.getLogger(__name__)

class RecommendationService:
    def __init__(self, cache_service: CacheService):
        self.cache_service = cache_service
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    async def get_recommendations(
        self, 
        user_id: int, 
        company_id: int, 
        db: Session,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get personalized document recommendations for a user based on their query history.
        """
        # Check cache first
        cached_recommendations = await self.cache_service.get_recommendations(user_id)
        if cached_recommendations:
            logger.info(f"Returning cached recommendations for user {user_id}")
            return cached_recommendations
        
        # Get user's query history
        user_queries = db.query(Query).filter(
            Query.user_id == user_id,
            Query.company_id == company_id
        ).order_by(Query.created_at.desc()).limit(10).all()
        
        if not user_queries:
            # New user - return company-level popular documents with lower baseline scores
            logger.info(f"New user {user_id} - providing fallback recommendations")
            return await self._get_company_fallback_recommendations(company_id, db, limit)
        
        # Get all company documents
        company_documents = db.query(Document).filter(
            Document.company_id == company_id
        ).order_by(Document.created_at.desc()).all()
        
        if not company_documents:
            return []
        
        # Calculate recommendations using TF-IDF similarity
        recommendations = await self._calculate_similarity_recommendations(
            user_queries, company_documents, limit
        )
        
        # Cache the recommendations
        await self.cache_service.cache_recommendations(user_id, recommendations)
        
        return recommendations
    
    async def _calculate_similarity_recommendations(
        self,
        user_queries: List[Query],
        documents: List[Document],
        limit: int
    ) -> List[Dict]:
        """
        INTELLIGENT DYNAMIC RECOMMENDATION ALGORITHM
        - Semantic content analysis without hardcoded categories
        - Adaptive query understanding
        - Dynamic relevance scoring
        """
        try:
            if not user_queries:
                return []
            
            # STEP 1: DYNAMIC QUERY PROCESSING with intelligent recency weighting
            query_texts = [query.query_text for query in user_queries]
            
            # Exponential decay for query importance (most recent = highest weight)
            weighted_queries = []
            for i, query_text in enumerate(query_texts):
                # Exponential decay: weight = e^(-0.5*i)
                # Recent: 1.0, Second: 0.6, Third: 0.37, Fourth: 0.22, etc.
                import math
                weight = math.exp(-0.5 * i)
                repetitions = max(1, int(weight * 10))  # Scale to reasonable repetitions
                weighted_queries.extend([query_text] * repetitions)
            
            query_combined = " ".join(weighted_queries)
            
            # STEP 2: ADVANCED SEMANTIC PREPROCESSING
            processed_queries = self._preprocess_text_intelligently(query_combined)
            processed_docs = [self._preprocess_text_intelligently(f"{doc.title} {doc.content}") 
                            for doc in documents]
            
            # STEP 3: INTELLIGENT TF-IDF with enhanced parameters
            all_texts = [processed_queries] + processed_docs
            
            # Enhanced TF-IDF vectorizer for better semantic understanding
            tfidf_vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=10000,  # Increased for better vocabulary coverage
                ngram_range=(1, 3),  # Include trigrams for better phrase matching
                min_df=1,
                max_df=0.7,  # Lower to avoid common words
                sublinear_tf=True,  # Use log-scaled term frequencies
                use_idf=True,
                smooth_idf=True,
                norm='l2'  # L2 normalization for better cosine similarity
            )
            
            tfidf_matrix = tfidf_vectorizer.fit_transform(all_texts)
            query_vector = tfidf_matrix[0:1]
            doc_vectors = tfidf_matrix[1:]
            
            # Base cosine similarity scores
            base_similarities = cosine_similarity(query_vector, doc_vectors)[0]
            
            # STEP 4: INTELLIGENT SEMANTIC BOOSTING (No hardcoded categories!)
            enhanced_similarities = []
            most_recent_query = user_queries[0].query_text.lower()
            
            for i, (doc, base_sim) in enumerate(zip(documents, base_similarities)):
                enhanced_score = base_sim
                
                # DYNAMIC TITLE RELEVANCE BOOST
                title_relevance = self._calculate_title_relevance(most_recent_query, doc.title)
                enhanced_score += title_relevance
                
                # SEMANTIC KEYWORD DENSITY BOOST  
                keyword_density = self._calculate_semantic_keyword_density(most_recent_query, doc)
                enhanced_score += keyword_density
                
                # CONTENT FRESHNESS & CONFIDENCE BOOST
                confidence_boost = self._calculate_confidence_boost(doc)
                enhanced_score += confidence_boost
                
                # QUERY-DOCUMENT SEMANTIC ALIGNMENT
                semantic_alignment = self._calculate_semantic_alignment(user_queries, doc)
                enhanced_score += semantic_alignment
                
                enhanced_similarities.append(enhanced_score)
                
                # Debug logging for transparency
                if title_relevance > 0 or keyword_density > 0.1 or semantic_alignment > 0.1:
                    print(f"🧠 SMART BOOST: '{doc.title[:50]}...' - Title:{title_relevance:.3f}, Keywords:{keyword_density:.3f}, Alignment:{semantic_alignment:.3f}")
            
            similarities = enhanced_similarities
            
            # Create recommendations with scores
            recommendations = []
            for i, (doc, similarity_score) in enumerate(zip(documents, similarities)):
                # Lower threshold to 0.01 to allow more diverse cross-intent recommendations
                # Even documents with low similarity should be shown to promote discovery
                if similarity_score > 0.01:  
                    explanation = self._generate_explanation(
                        similarity_score, 
                        user_queries[-3:],  # Use last 3 queries for explanation
                        doc
                    )
                    
                    # Apply diversity boost for source variety and quality
                    final_score = self._apply_diversity_boost(
                        similarity_score, 
                        doc, 
                        user_queries[0].user_id if user_queries else None
                    )
                    
                    recommendations.append({
                        "id": doc.id,
                        "title": doc.title,
                        "content": doc.content[:300] + "..." if len(doc.content) > 300 else doc.content,
                        "source": doc.source,
                        "confidence": doc.confidence,
                        "relevance_score": float(final_score),
                        "explanation": explanation,
                        "created_at": doc.created_at.isoformat()
                    })
            
            # Ensure source diversity: guarantee representation from different document types
            recommendations = self._ensure_source_diversity(recommendations, documents, user_queries[0].user_id if user_queries else None)
            
            # Sort by relevance score and return top N
            recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error calculating similarity recommendations: {str(e)}")
            return []
    
    def _preprocess_text_intelligently(self, text: str) -> str:
        """
        Intelligent text preprocessing for better semantic understanding
        """
        import re
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        
        # Handle common abbreviations and expand them
        abbreviations = {
            'hr': 'human resources',
            'gl': 'general ledger', 
            'capex': 'capital expenditure',
            'q1': 'quarter one', 'q2': 'quarter two', 'q3': 'quarter three', 'q4': 'quarter four'
        }
        
        for abbr, full in abbreviations.items():
            text = re.sub(r'\b' + abbr + r'\b', full, text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def _calculate_title_relevance(self, query: str, title: str) -> float:
        """
        Dynamic title relevance calculation without hardcoded categories
        """
        query_words = set(query.lower().split())
        title_words = set(title.lower().split())
        
        # Calculate word overlap ratio
        overlap = len(query_words.intersection(title_words))
        total_query_words = len(query_words)
        
        if total_query_words == 0:
            return 0.0
        
        # Higher boost for higher overlap percentage
        overlap_ratio = overlap / total_query_words
        title_boost = overlap_ratio * 0.8  # Max 0.8 boost for perfect title match
        
        return title_boost
    
    def _calculate_semantic_keyword_density(self, query: str, document: Document) -> float:
        """
        Calculate keyword density in document content
        """
        query_words = set(query.lower().split())
        doc_content = f"{document.title} {document.content}".lower()
        doc_words = doc_content.split()
        
        if not doc_words:
            return 0.0
        
        # Count keyword occurrences in document
        keyword_count = sum(1 for word in doc_words if word in query_words)
        density = keyword_count / len(doc_words)
        
        # Scale density to reasonable boost range
        density_boost = min(0.5, density * 10)  # Max 0.5 boost
        
        return density_boost
    
    def _calculate_confidence_boost(self, document: Document) -> float:
        """
        Boost based on document confidence and quality indicators
        """
        confidence_boost = 0.0
        
        # Use document confidence if available
        if hasattr(document, 'confidence') and document.confidence:
            confidence_boost += (document.confidence - 0.5) * 0.2  # Scale confidence
        
        # Boost for longer, more detailed content
        content_length = len(document.content)
        if content_length > 200:
            length_boost = min(0.1, content_length / 2000)  # Max 0.1 boost
            confidence_boost += length_boost
        
        return max(0.0, confidence_boost)
    
    def _calculate_semantic_alignment(self, user_queries: List[Query], document: Document) -> float:
        """
        Calculate how well document aligns with user's query patterns
        """
        if not user_queries:
            return 0.0
        
        # Analyze query patterns
        all_query_text = " ".join([q.query_text.lower() for q in user_queries[:3]])  # Recent 3 queries
        doc_content = f"{document.title} {document.content}".lower()
        
        # Simple semantic alignment based on word co-occurrence
        query_words = set(all_query_text.split())
        doc_words = set(doc_content.split())
        
        # Calculate Jaccard similarity
        intersection = len(query_words.intersection(doc_words))
        union = len(query_words.union(doc_words))
        
        if union == 0:
            return 0.0
        
        jaccard_similarity = intersection / union
        alignment_boost = jaccard_similarity * 0.3  # Max 0.3 boost
        
        return alignment_boost
    
    def _generate_explanation(
        self, 
        similarity_score: float, 
        recent_queries: List[Query], 
        document: Document
    ) -> str:
        """
        Generate RAG-ready explanations based on content relevance and source type.
        """
        query_topics = []
        for query in recent_queries:
            # Extract key terms (simple approach - could be enhanced)
            words = query.query_text.lower().split()
            key_words = [w for w in words if len(w) > 4][:2]
            query_topics.extend(key_words)
        
        # Source-based explanations (RAG-ready)
        source_explanations = {
            "API": "API documentation",
            "Guide": "Step-by-step guide", 
            "Research": "Research insights",
            "Wiki": "Knowledge base content",
            "Policy": "Policy documentation"
        }
        
        source_context = source_explanations.get(document.source, "Documentation")
        
        if similarity_score > 0.4:
            if query_topics:
                topics_str = ', '.join(query_topics[:2])
                return f"{source_context}: Directly related to {topics_str}."
            else:
                return f"{source_context}: Highly relevant to your recent queries."
        elif similarity_score > 0.15:
            return f"{source_context}: May be useful based on your query patterns."
        elif similarity_score > 0.05:
            return f"{source_context}: Potentially relevant to your research area."
        else:
            return f"{source_context}: Exploring different content types for broader insights."
    
    def _apply_diversity_boost(
        self, 
        similarity_score: float, 
        document: Document, 
        current_user_id: int = None
    ) -> float:
        """
        Apply diversity boost for RAG-ready document discovery.
        Promotes source diversity and recency without relying on user authorship.
        """
        base_score = similarity_score
        
        # Source diversity boost (simulate different document sources)
        # In real RAG: GitHub vs Confluence vs Support tickets
        source_types = ["Guide", "Research", "Wiki", "API", "Policy"]
        if document.source in source_types:
            # Boost non-standard sources to encourage exploration
            if document.source not in ["Guide", "Wiki"]:  # Boost less common sources
                source_diversity_boost = 0.03
                base_score += source_diversity_boost
        
        # Boost for recent documents (recency matters in RAG)
        from datetime import datetime, timedelta
        if document.created_at and isinstance(document.created_at, datetime):
            days_old = (datetime.utcnow() - document.created_at).days
            if days_old <= 7:  # Recent documents get boost
                recency_boost = 0.02 * (7 - days_old) / 7
                base_score += recency_boost
        
        # Document quality/confidence boost (simulates RAG document quality scores)
        if hasattr(document, 'confidence') and document.confidence:
            quality_boost = (document.confidence - 0.5) * 0.05  # Boost high-confidence docs
            base_score += max(0, quality_boost)
        
        # Cap the maximum score to 1.0
        return min(base_score, 1.0)
    
    def _ensure_source_diversity(
        self, 
        recommendations: List[Dict], 
        all_documents: List[Document], 
        current_user_id: int = None
    ) -> List[Dict]:
        """
        Ensure source type diversity in recommendations for RAG integration.
        Promotes discovery across different document types (APIs, guides, policies, etc.)
        """
        # Get all unique source types in current recommendations
        rec_sources = {rec["source"] for rec in recommendations}
        
        # Get all available source types in the company
        all_sources = {doc.source for doc in all_documents}
        missing_sources = all_sources - rec_sources
        
        # Add one document from each missing source type
        for source_type in missing_sources:
            # Find the highest quality document from this source
            source_docs = [doc for doc in all_documents if doc.source == source_type]
            if source_docs:
                # Sort by confidence/quality, then by recency
                best_doc = max(source_docs, key=lambda d: (d.confidence or 0.5, d.created_at))
                
                # Add with source diversity score
                diversity_rec = {
                    "id": best_doc.id,
                    "title": best_doc.title,
                    "content": best_doc.content[:300] + "..." if len(best_doc.content) > 300 else best_doc.content,
                    "source": best_doc.source,
                    "confidence": best_doc.confidence,
                    "relevance_score": 0.06,  # Low but visible score for source diversity
                    "explanation": f"Knowledge from {source_type} - exploring different content types.",
                    "created_at": best_doc.created_at.isoformat()
                }
                
                # Only add if not already in recommendations
                if not any(rec["id"] == best_doc.id for rec in recommendations):
                    recommendations.append(diversity_rec)
        
        return recommendations
    
    async def _get_company_fallback_recommendations(
        self, 
        company_id: int, 
        db: Session, 
        limit: int
    ) -> List[Dict]:
        """
        Get fallback recommendations for new users based on company-wide popular documents.
        Uses lower baseline scores to ensure users with query history rank higher.
        """
        try:
            # Get most recent documents from the company
            company_documents = db.query(Document).filter(
                Document.company_id == company_id
            ).order_by(Document.created_at.desc()).limit(limit).all()
            
            recommendations = []
            for i, doc in enumerate(company_documents):
                # Use decreasing baseline scores for new users (0.25 -> 0.15)
                # This ensures users with real query similarity always rank higher
                baseline_score = max(0.15, 0.25 - (i * 0.02))
                
                recommendations.append({
                    "id": doc.id,
                    "title": doc.title,
                    "content": doc.content[:300] + "..." if len(doc.content) > 300 else doc.content,
                    "source": doc.source,
                    "confidence": doc.confidence,
                    "relevance_score": baseline_score,
                    "explanation": f"New user suggestion: popular content in your organization.",
                    "created_at": doc.created_at.isoformat()
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting company fallback recommendations: {str(e)}")
            return []
    
    async def update_user_profile(self, user_id: int, new_query: str) -> bool:
        """
        Update user profile after a new query (invalidate cache).
        """
        try:
            # Invalidate cached recommendations since user behavior changed
            await self.cache_service.invalidate_user_cache(user_id)
            return True
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return False