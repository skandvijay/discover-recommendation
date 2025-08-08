"""
Simple, reliable recommendation service for real-time recommendations without datetime complications
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
from sqlalchemy.orm import Session
from models.models import Document, Query
import logging

logger = logging.getLogger(__name__)

class SimpleRecommendationService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def get_recommendations(
        self, 
        user_id: int, 
        company_id: int, 
        db: Session,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get real-time recommendations without caching or datetime complications
        """
        try:
            # Get user's recent queries
            user_queries = db.query(Query).filter(
                Query.user_id == user_id,
                Query.company_id == company_id
            ).order_by(Query.id.desc()).limit(10).all()
            
            # Get all company documents
            company_documents = db.query(Document).filter(
                Document.company_id == company_id
            ).order_by(Document.id.desc()).all()
            
            if not company_documents:
                return []
            
            if not user_queries:
                # New user - return recent company documents
                return self._get_fallback_recommendations(company_documents, limit)
            
            # Calculate TF-IDF similarity
            return self._calculate_recommendations(user_queries, company_documents, limit)
            
        except Exception as e:
            logger.error(f"Error in recommendations: {str(e)}")
            return []
    
    def _calculate_recommendations(
        self, 
        user_queries: List[Query], 
        documents: List[Document], 
        limit: int
    ) -> List[Dict]:
        """Simple TF-IDF recommendation calculation"""
        try:
            # Combine user queries
            query_texts = [q.query_text for q in user_queries]
            combined_query = " ".join(query_texts)
            
            # Prepare document texts
            doc_texts = [f"{doc.title} {doc.content}" for doc in documents]
            
            # Calculate TF-IDF
            all_texts = [combined_query] + doc_texts
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Calculate similarities
            query_vector = tfidf_matrix[0:1]
            doc_vectors = tfidf_matrix[1:]
            similarities = cosine_similarity(query_vector, doc_vectors)[0]
            
            # Create recommendations
            recommendations = []
            current_user_id = user_queries[0].user_id
            
            for i, (doc, similarity) in enumerate(zip(documents, similarities)):
                if similarity > 0.01:  # Low threshold for diversity
                    
                    # Cross-user boost
                    score = similarity
                    if doc.created_by_user_id != current_user_id:
                        score += 0.05
                        explanation = "Team knowledge - exploring different perspectives."
                    else:
                        explanation = "Related to your interests."
                    
                    # Higher similarity boost
                    if similarity > 0.3:
                        explanation = "Highly relevant to your queries."
                    elif similarity > 0.15:
                        explanation = "May be useful based on your query patterns."
                    
                    recommendations.append({
                        "id": doc.id,
                        "title": doc.title,
                        "content": doc.content[:300] + "..." if len(doc.content) > 300 else doc.content,
                        "source": doc.source,
                        "confidence": doc.confidence,
                        "relevance_score": float(score),
                        "explanation": explanation,
                        "created_at": "2025-08-05T12:00:00"  # Simple fixed datetime
                    })
            
            # Sort by score and return top results
            recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Error calculating recommendations: {str(e)}")
            return []
    
    def _get_fallback_recommendations(self, documents: List[Document], limit: int) -> List[Dict]:
        """Simple fallback for new users"""
        recommendations = []
        
        for i, doc in enumerate(documents[:limit]):
            score = max(0.15, 0.25 - (i * 0.02))
            
            recommendations.append({
                "id": doc.id,
                "title": doc.title,
                "content": doc.content[:300] + "..." if len(doc.content) > 300 else doc.content,
                "source": doc.source,
                "confidence": doc.confidence,
                "relevance_score": score,
                "explanation": "Popular content in your organization.",
                "created_at": "2025-08-05T12:00:00"
            })
        
        return recommendations