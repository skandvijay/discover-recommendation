from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# Company Schemas
class CompanyBase(BaseModel):
    name: str


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    company_id: int


class UserResponse(UserBase):
    id: int
    company_id: int
    created_at: datetime
    company: CompanyResponse
    
    class Config:
        from_attributes = True


# Document Schemas
class DocumentBase(BaseModel):
    title: str
    content: str
    source: Optional[str] = "LLM Generated"
    confidence: Optional[float] = 0.8


class DocumentCreate(DocumentBase):
    created_by_user_id: int
    company_id: int


class DocumentResponse(DocumentBase):
    id: int
    created_by_user_id: int
    company_id: int
    created_at: datetime
    created_by_user: UserResponse
    
    class Config:
        from_attributes = True


# Query Schemas
class QueryBase(BaseModel):
    query_text: str


class QueryCreate(QueryBase):
    user_id: int
    company_id: int


class QueryResponse(QueryBase):
    id: int
    user_id: int
    company_id: int
    created_at: datetime
    user: UserResponse
    
    class Config:
        from_attributes = True


# Search Schemas
class SearchRequest(BaseModel):
    query: str
    user_id: int
    company_id: int
    save_as_document: Optional[bool] = True


class SearchResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]
    confidence: float
    document_id: Optional[int] = None


# Recommendation Schemas
class RecommendationResponse(BaseModel):
    id: int
    title: str
    content: str
    source: str
    confidence: float
    relevance_score: float
    explanation: str
    created_at: datetime
    
    class Config:
        from_attributes = True