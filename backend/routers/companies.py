from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models import get_db, Company
from schemas import CompanyCreate, CompanyResponse

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company: CompanyCreate,
    db: Session = Depends(get_db)
):
    """Create a new company"""
    # Check if company name already exists
    existing_company = db.query(Company).filter(Company.name == company.name).first()
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this name already exists"
        )
    
    db_company = Company(name=company.name)
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    
    return db_company


@router.get("/", response_model=List[CompanyResponse])
async def get_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all companies"""
    companies = db.query(Company).offset(skip).limit(limit).all()
    return companies


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific company by ID"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_update: CompanyCreate,
    db: Session = Depends(get_db)
):
    """Update a company"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Check if new name conflicts with existing company
    if company.name != company_update.name:
        existing_company = db.query(Company).filter(Company.name == company_update.name).first()
        if existing_company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company with this name already exists"
            )
    
    company.name = company_update.name
    db.commit()
    db.refresh(company)
    
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    db: Session = Depends(get_db)
):
    """Delete a company"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    db.delete(company)
    db.commit()
    
    return None