from .companies import router as companies_router
from .users import router as users_router
from .search import router as search_router
from .recommendations import router as recommendations_router
from .documents import router as documents_router

__all__ = [
    "companies_router",
    "users_router", 
    "search_router",
    "recommendations_router",
    "documents_router"
]