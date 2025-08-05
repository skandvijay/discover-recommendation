from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from models import get_db, Document, User
from schemas import DocumentCreate, DocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    company_id: int,
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get documents for a company, optionally filtered by user
    """
    query = db.query(Document).filter(Document.company_id == company_id)
    
    if user_id:
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
        
        query = query.filter(Document.created_by_user_id == user_id)
    
    documents = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    company_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific document by ID (with company validation)
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.company_id == company_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new document
    """
    # Validate user belongs to company
    user = db.query(User).filter(
        User.id == document.created_by_user_id,
        User.company_id == document.company_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user or company"
        )
    
    db_document = Document(
        title=document.title,
        content=document.content,
        source=document.source,
        confidence=document.confidence,
        created_by_user_id=document.created_by_user_id,
        company_id=document.company_id
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_update: DocumentCreate,
    db: Session = Depends(get_db)
):
    """
    Update a document
    """
    # Get document with company validation
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.company_id == document_update.company_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Validate user belongs to company
    user = db.query(User).filter(
        User.id == document_update.created_by_user_id,
        User.company_id == document_update.company_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user or company"
        )
    
    # Update document
    document.title = document_update.title
    document.content = document_update.content
    document.source = document_update.source
    document.confidence = document_update.confidence
    document.created_by_user_id = document_update.created_by_user_id
    
    db.commit()
    db.refresh(document)
    
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    company_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a document (with security checks)
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.company_id == company_id,
        Document.created_by_user_id == user_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied"
        )
    
    db.delete(document)
    db.commit()
    
    return None


@router.get("/user/{user_id}", response_model=List[DocumentResponse])
async def get_user_documents(
    user_id: int,
    company_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get all documents created by a specific user
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
    
    documents = db.query(Document).filter(
        Document.created_by_user_id == user_id,
        Document.company_id == company_id
    ).order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    
    return documents