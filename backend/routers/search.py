from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models import get_db, User, Company, Document, Query
from schemas import SearchRequest, SearchResponse, QueryResponse
from services import LLMService, CacheService, RecommendationService

router = APIRouter(prefix="/search", tags=["search"])

# Initialize services lazily to avoid import-time errors
cache_service = CacheService()
recommendation_service = RecommendationService(cache_service)


@router.post("/", response_model=SearchResponse)
async def search_and_generate(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Process user query, generate LLM response, and optionally save as document
    """
    # Validate user and company
    user = db.query(User).filter(
        User.id == request.user_id,
        User.company_id == request.company_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user or company"
        )
    
    try:
        # Get recent context from user's queries
        recent_queries = db.query(Query).filter(
            Query.user_id == request.user_id,
            Query.company_id == request.company_id
        ).order_by(Query.created_at.desc()).limit(3).all()
        
        context = [q.query_text for q in recent_queries] if recent_queries else []
        
        # Generate answer using LLM (lazy initialization)
        llm_service = LLMService()
        
        try:
            llm_response = await llm_service.generate_answer(request.query, context)
        except Exception as llm_error:
            # Save query even if LLM fails, but don't save error documents
            db_query = Query(
                query_text=request.query,
                user_id=request.user_id,
                company_id=request.company_id
            )
            db.add(db_query)
            db.commit()
            
            # Return error response without saving document
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Unable to generate answer: {str(llm_error)}"
            )
        
        # Save query to database
        db_query = Query(
            query_text=request.query,
            user_id=request.user_id,
            company_id=request.company_id
        )
        db.add(db_query)
        db.commit()
        
        document_id = None
        
        # Save as document if requested (only save successful responses)
        if request.save_as_document and llm_response.get("success", False):
            db_document = Document(
                title=llm_response["title"],
                content=llm_response["answer"],
                source=llm_response["sources"][0] if llm_response["sources"] else "LLM Generated",
                confidence=llm_response["confidence"],
                created_by_user_id=request.user_id,
                company_id=request.company_id
            )
            db.add(db_document)
            db.commit()
            db.refresh(db_document)
            document_id = db_document.id
        
        # Update user profile for recommendations (invalidate cache)
        await recommendation_service.update_user_profile(request.user_id, request.query)
        
        # Update cached query history
        all_queries = db.query(Query).filter(
            Query.user_id == request.user_id,
            Query.company_id == request.company_id
        ).order_by(Query.created_at.desc()).limit(5).all()
        
        query_cache_data = [
            {
                "id": q.id,
                "query_text": q.query_text,
                "created_at": q.created_at.isoformat()
            }
            for q in all_queries
        ]
        await cache_service.cache_query_history(request.user_id, query_cache_data)
        
        return SearchResponse(
            query=request.query,
            answer=llm_response["answer"],
            sources=llm_response["sources"],
            confidence=llm_response["confidence"],
            document_id=document_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing search request: {str(e)}"
        )


@router.get("/queries/{user_id}", response_model=List[QueryResponse])
async def get_user_queries(
    user_id: int,
    company_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get user's query history (scoped to company for security)
    """
    # Validate user belongs to company
    user = db.query(User).filter(
        User.id == user_id,
        User.company_id == company_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user or company"
        )
    
    # Get queries with proper scoping
    queries = db.query(Query).filter(
        Query.user_id == user_id,
        Query.company_id == company_id
    ).order_by(Query.created_at.desc()).offset(skip).limit(limit).all()
    
    return queries


@router.delete("/queries/{query_id}")
async def delete_query(
    query_id: int,
    user_id: int,
    company_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a specific query (with security checks)
    """
    query = db.query(Query).filter(
        Query.id == query_id,
        Query.user_id == user_id,
        Query.company_id == company_id
    ).first()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found or access denied"
        )
    
    db.delete(query)
    db.commit()
    
    # Invalidate cache after deletion
    await cache_service.invalidate_user_cache(user_id)
    
    return {"message": "Query deleted successfully"}