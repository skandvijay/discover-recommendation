from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from models import get_db, User, Company
from schemas import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user and assign to company"""
    # Check if company exists
    company = db.query(Company).filter(Company.id == user.company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company not found"
        )
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    db_user = User(
        name=user.name,
        email=user.email,
        company_id=user.company_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.get("/", response_model=List[UserResponse])
async def get_users(
    company_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get users, optionally filtered by company"""
    query = db.query(User)
    
    if company_id:
        query = query.filter(User.company_id == company_id)
    
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserCreate,
    db: Session = Depends(get_db)
):
    """Update a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if company exists
    company = db.query(Company).filter(Company.id == user_update.company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company not found"
        )
    
    # Check if new email conflicts with existing user
    if user.email != user_update.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
    
    user.name = user_update.name
    user.email = user_update.email
    user.company_id = user_update.company_id
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Delete a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    
    return None


@router.get("/company/{company_id}", response_model=List[UserResponse])
async def get_users_by_company(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all users for a specific company"""
    # Verify company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    users = db.query(User).filter(
        User.company_id == company_id
    ).offset(skip).limit(limit).all()
    
    return users