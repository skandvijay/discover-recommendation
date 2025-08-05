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
        Calculate document recommendations based on TF-IDF similarity with user queries.
        """
        try:
            # Prepare query text
            query_texts = [query.query_text for query in user_queries]
            query_combined = " ".join(query_texts)
            
            # Prepare document texts
            doc_texts = [f"{doc.title} {doc.content}" for doc in documents]
            
            # Combine all texts for TF-IDF fitting
            all_texts = [query_combined] + doc_texts
            
            # Calculate TF-IDF vectors
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Query vector is the first row
            query_vector = tfidf_matrix[0:1]
            
            # Document vectors are the rest
            doc_vectors = tfidf_matrix[1:]
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_vector, doc_vectors)[0]
            
            # Create recommendations with scores
            recommendations = []
            for i, (doc, similarity_score) in enumerate(zip(documents, similarities)):
                if similarity_score > 0.1:  # Filter out very low similarities
                    explanation = self._generate_explanation(
                        similarity_score, 
                        user_queries[-3:],  # Use last 3 queries for explanation
                        doc
                    )
                    
                    recommendations.append({
                        "id": doc.id,
                        "title": doc.title,
                        "content": doc.content[:300] + "..." if len(doc.content) > 300 else doc.content,
                        "source": doc.source,
                        "confidence": doc.confidence,
                        "relevance_score": float(similarity_score),
                        "explanation": explanation,
                        "created_at": doc.created_at.isoformat()
                    })
            
            # Sort by relevance score and return top N
            recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error calculating similarity recommendations: {str(e)}")
            return []
    
    def _generate_explanation(
        self, 
        similarity_score: float, 
        recent_queries: List[Query], 
        document: Document
    ) -> str:
        """
        Generate a human-readable explanation for why this document was recommended.
        """
        query_topics = []
        for query in recent_queries:
            # Extract key terms (simple approach - could be enhanced)
            words = query.query_text.lower().split()
            key_words = [w for w in words if len(w) > 4][:2]
            query_topics.extend(key_words)
        
        if similarity_score > 0.7:
            return f"Highly relevant to your recent queries about {', '.join(query_topics[:3])}."
        elif similarity_score > 0.4:
            return f"Related to your interests in {', '.join(query_topics[:2])}."
        elif similarity_score > 0.2:
            return f"May be useful based on your query patterns."
        else:
            return "Potentially relevant to your research area."
    
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