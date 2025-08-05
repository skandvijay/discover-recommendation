from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models import get_db, User
from schemas import RecommendationResponse
from services import RecommendationService, CacheService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

# Initialize services
cache_service = CacheService()
recommendation_service = RecommendationService(cache_service)


@router.get("/{user_id}", response_model=List[RecommendationResponse])
async def get_recommendations(
    user_id: int,
    company_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get personalized recommendations for a user based on their query history
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
    
    try:
        recommendations = await recommendation_service.get_recommendations(
            user_id=user_id,
            company_id=company_id,
            db=db,
            limit=limit
        )
        
        # Convert to response format
        recommendation_responses = []
        for rec in recommendations:
            recommendation_responses.append(RecommendationResponse(
                id=rec["id"],
                title=rec["title"],
                content=rec["content"],
                source=rec["source"],
                confidence=rec["confidence"],
                relevance_score=rec["relevance_score"],
                explanation=rec["explanation"],
                created_at=rec["created_at"]
            ))
        
        return recommendation_responses
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.post("/{user_id}/refresh")
async def refresh_recommendations(
    user_id: int,
    company_id: int,
    db: Session = Depends(get_db)
):
    """
    Force refresh recommendations for a user (clear cache)
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
    
    try:
        # Clear cached recommendations
        await cache_service.invalidate_user_cache(user_id)
        
        # Generate fresh recommendations
        recommendations = await recommendation_service.get_recommendations(
            user_id=user_id,
            company_id=company_id,
            db=db,
            limit=10
        )
        
        return {
            "message": "Recommendations refreshed successfully",
            "count": len(recommendations)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing recommendations: {str(e)}"
        )


@router.get("/health/cache")
async def check_cache_health():
    """
    Check if Redis cache is working properly
    """
    try:
        is_healthy = await cache_service.health_check()
        
        if is_healthy:
            return {"status": "healthy", "cache": "connected"}
        else:
            return {"status": "unhealthy", "cache": "disconnected"}
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache health check failed: {str(e)}"
        )