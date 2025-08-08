import redis
import json
import os
from typing import List, Dict, Optional
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class CacheService:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # Cache TTL settings
        self.QUERY_HISTORY_TTL = timedelta(hours=24)
        self.RECOMMENDATIONS_TTL = timedelta(minutes=5)  # Reduced for testing 
        self.INTENT_TTL = timedelta(hours=6)
    
    def _get_user_key(self, user_id: int, key_type: str) -> str:
        """Generate Redis key for user-specific data"""
        return f"user:{user_id}:{key_type}"
    
    def _get_company_key(self, company_id: int, key_type: str) -> str:
        """Generate Redis key for company-specific data"""
        return f"company:{company_id}:{key_type}"
    
    async def cache_query_history(self, user_id: int, queries: List[Dict]) -> bool:
        """Cache the last 5 queries for a user"""
        try:
            key = self._get_user_key(user_id, "query_history")
            # Keep only last 5 queries
            queries_data = queries[-5:] if len(queries) > 5 else queries
            
            self.redis_client.setex(
                key,
                self.QUERY_HISTORY_TTL,
                json.dumps(queries_data)
            )
            return True
        except Exception as e:
            print(f"Error caching query history: {str(e)}")
            return False
    
    async def get_query_history(self, user_id: int) -> List[Dict]:
        """Retrieve cached query history for a user"""
        try:
            key = self._get_user_key(user_id, "query_history")
            cached_data = self.redis_client.get(key)
            
            if cached_data:
                return json.loads(cached_data)
            return []
        except Exception as e:
            print(f"Error retrieving query history: {str(e)}")
            return []
    
    async def cache_recommendations(self, user_id: int, recommendations: List[Dict]) -> bool:
        """Cache recommendations for a user"""
        try:
            key = self._get_user_key(user_id, "recommendations")
            
            self.redis_client.setex(
                key,
                self.RECOMMENDATIONS_TTL,
                json.dumps(recommendations)
            )
            return True
        except Exception as e:
            print(f"Error caching recommendations: {str(e)}")
            return False
    
    async def get_recommendations(self, user_id: int) -> Optional[List[Dict]]:
        """Retrieve cached recommendations for a user"""
        try:
            key = self._get_user_key(user_id, "recommendations")
            cached_data = self.redis_client.get(key)
            
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            print(f"Error retrieving recommendations: {str(e)}")
            return None
    
    async def cache_intent(self, query: str, intent_data: Dict) -> bool:
        """Cache intent detection results"""
        try:
            # Use query hash as key to avoid key length issues
            import hashlib
            query_hash = hashlib.md5(query.encode()).hexdigest()
            key = f"intent:{query_hash}"
            
            self.redis_client.setex(
                key,
                self.INTENT_TTL,
                json.dumps(intent_data)
            )
            return True
        except Exception as e:
            print(f"Error caching intent: {str(e)}")
            return False
    
    async def get_intent(self, query: str) -> Optional[Dict]:
        """Retrieve cached intent for a query"""
        try:
            import hashlib
            query_hash = hashlib.md5(query.encode()).hexdigest()
            key = f"intent:{query_hash}"
            
            cached_data = self.redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            print(f"Error retrieving intent: {str(e)}")
            return None
    
    async def invalidate_user_cache(self, user_id: int) -> bool:
        """Invalidate all cached data for a user"""
        try:
            pattern = self._get_user_key(user_id, "*")
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"Error invalidating user cache: {str(e)}")
            return False
    
    async def health_check(self) -> bool:
        """Check if Redis is available"""
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False