"""
Excel Integration Router for Activity Report Processing
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Dict, Any
import tempfile
import os

from models import get_db
from services.excel_integration_service import ExcelIntegrationService

router = APIRouter(prefix="/excel", tags=["excel-integration"])

# Initialize service
excel_service = ExcelIntegrationService()


@router.post("/upload-activity-report")
async def upload_activity_report(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Upload and process an Excel activity report.
    
    Expected Excel format:
    - Companies sheet: name, industry (optional)
    - Users sheet: name, email, company_name  
    - Queries sheet: user_email, company_name, query_text, timestamp
    - Documents sheet: title, content, user_email, company_name, confidence (optional)
    """
    
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file (.xlsx or .xls)"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Validate Excel format first
        validation = excel_service.validate_excel_format(temp_file_path)
        if not validation["valid"]:
            os.unlink(temp_file_path)  # Clean up temp file
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid Excel format: {validation.get('error', validation.get('errors', []))}"
            )
        
        # Process the Excel file
        results = await excel_service.process_activity_report(temp_file_path, db)
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        if "error" in results:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=results["error"]
            )
        
        return {
            "message": "Activity report processed successfully",
            "filename": file.filename,
            "validation": validation,
            "processing_results": results,
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing Excel file: {str(e)}"
        )


@router.post("/validate-format")
async def validate_excel_format(
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    """
    Validate Excel file format without processing the data.
    """
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an Excel file (.xlsx or .xls)"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Validate format
        validation = excel_service.validate_excel_format(temp_file_path)
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        return {
            "filename": file.filename,
            "validation": validation
        }
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating Excel file: {str(e)}"
        )


@router.get("/insights")
async def get_real_time_insights(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get real-time insights about the current data state.
    """
    try:
        insights = await excel_service.get_real_time_insights(db)
        return insights
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting insights: {str(e)}"
        )


@router.get("/format-template")
async def get_format_template() -> Dict[str, Any]:
    """
    Get the expected Excel format template for activity reports.
    """
    return {
        "excel_format": {
            "sheets": {
                "Companies": {
                    "required_columns": ["name"],
                    "optional_columns": ["industry"],
                    "description": "List of companies in the organization"
                },
                "Users": {
                    "required_columns": ["name", "email", "company_name"],
                    "optional_columns": [],
                    "description": "List of users with their company association"
                },
                "Queries": {
                    "required_columns": ["user_email", "company_name", "query_text"],
                    "optional_columns": ["timestamp"],
                    "description": "User queries for intent analysis and recommendations"
                },
                "Documents": {
                    "required_columns": ["title", "content", "user_email", "company_name"],
                    "optional_columns": ["confidence"],
                    "description": "Documents created by users for recommendation engine"
                }
            },
            "example_data": {
                "Companies": [
                    {"name": "TechCorp", "industry": "Technology"}
                ],
                "Users": [
                    {"name": "Alice Johnson", "email": "alice@techcorp.com", "company_name": "TechCorp"}
                ],
                "Queries": [
                    {
                        "user_email": "alice@techcorp.com", 
                        "company_name": "TechCorp",
                        "query_text": "How to implement microservices?",
                        "timestamp": "2025-08-08 10:30:00"
                    }
                ],
                "Documents": [
                    {
                        "title": "Microservices Guide",
                        "content": "A comprehensive guide to microservices architecture...",
                        "user_email": "alice@techcorp.com",
                        "company_name": "TechCorp",
                        "confidence": 0.9
                    }
                ]
            }
        },
        "notes": [
            "All sheets are optional, but at least Companies and Users are recommended",
            "Timestamps can be in various formats (Excel will auto-detect)",
            "Company names must match exactly between sheets",
            "User emails must match exactly between sheets",
            "Confidence values should be between 0.0 and 1.0"
        ]
    }