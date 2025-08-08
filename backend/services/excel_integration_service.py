"""
Excel Integration Service for Real-Time Activity Report Processing
Handles Excel files with company, user, and query data for real-time recommendations.
"""
import pandas as pd
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
from models.models import Company, User, Query, Document
from models.database import get_db

logger = logging.getLogger(__name__)

class ExcelIntegrationService:
    """
    Service for processing Excel activity reports and integrating them into the recommendation system.
    
    Expected Excel format:
    - Companies sheet: name, industry (optional)
    - Users sheet: name, email, company_name
    - Queries sheet: user_email, company_name, query_text, timestamp
    - Documents sheet: title, content, user_email, company_name, confidence (optional)
    """
    
    def __init__(self):
        self.logger = logger
    
    async def process_activity_report(
        self, 
        excel_file_path: str, 
        db: Session
    ) -> Dict[str, Any]:
        """
        Process an Excel activity report and update the database with new data.
        
        Args:
            excel_file_path: Path to the Excel file
            db: Database session
            
        Returns:
            Dict with processing results and statistics
        """
        try:
            # Load Excel file
            excel_data = pd.read_excel(excel_file_path, sheet_name=None)
            
            results = {
                "companies_processed": 0,
                "users_processed": 0,
                "queries_processed": 0,
                "documents_processed": 0,
                "errors": []
            }
            
            # Process companies first
            if "Companies" in excel_data:
                results["companies_processed"] = await self._process_companies(
                    excel_data["Companies"], db
                )
            
            # Process users
            if "Users" in excel_data:
                results["users_processed"] = await self._process_users(
                    excel_data["Users"], db
                )
            
            # Process queries 
            if "Queries" in excel_data:
                results["queries_processed"] = await self._process_queries(
                    excel_data["Queries"], db
                )
            
            # Process documents
            if "Documents" in excel_data:
                results["documents_processed"] = await self._process_documents(
                    excel_data["Documents"], db
                )
                
            db.commit()
            
            self.logger.info(f"Excel processing complete: {results}")
            return results
            
        except Exception as e:
            db.rollback()
            error_msg = f"Error processing Excel file: {str(e)}"
            self.logger.error(error_msg)
            return {"error": error_msg, "success": False}
    
    async def _process_companies(self, companies_df: pd.DataFrame, db: Session) -> int:
        """Process companies from Excel data"""
        processed = 0
        
        for _, row in companies_df.iterrows():
            try:
                company_name = row.get('name', '').strip()
                if not company_name:
                    continue
                
                # Check if company already exists
                existing = db.query(Company).filter(Company.name == company_name).first()
                if existing:
                    continue
                
                # Create new company
                company = Company(
                    name=company_name,
                    # Add other fields if available in Excel
                )
                db.add(company)
                processed += 1
                
            except Exception as e:
                self.logger.error(f"Error processing company {row}: {e}")
                continue
        
        return processed
    
    async def _process_users(self, users_df: pd.DataFrame, db: Session) -> int:
        """Process users from Excel data"""
        processed = 0
        
        for _, row in users_df.iterrows():
            try:
                user_name = row.get('name', '').strip()
                user_email = row.get('email', '').strip()
                company_name = row.get('company_name', '').strip()
                
                if not all([user_name, user_email, company_name]):
                    continue
                
                # Find company
                company = db.query(Company).filter(Company.name == company_name).first()
                if not company:
                    self.logger.warning(f"Company '{company_name}' not found for user {user_email}")
                    continue
                
                # Check if user already exists
                existing = db.query(User).filter(User.email == user_email).first()
                if existing:
                    continue
                
                # Create new user
                user = User(
                    name=user_name,
                    email=user_email,
                    company_id=company.id
                )
                db.add(user)
                processed += 1
                
            except Exception as e:
                self.logger.error(f"Error processing user {row}: {e}")
                continue
        
        return processed
    
    async def _process_queries(self, queries_df: pd.DataFrame, db: Session) -> int:
        """Process queries from Excel data"""
        processed = 0
        
        for _, row in queries_df.iterrows():
            try:
                user_email = row.get('user_email', '').strip()
                company_name = row.get('company_name', '').strip()
                query_text = row.get('query_text', '').strip()
                timestamp_str = row.get('timestamp', '')
                
                if not all([user_email, company_name, query_text]):
                    continue
                
                # Find user and company
                user = db.query(User).filter(User.email == user_email).first()
                company = db.query(Company).filter(Company.name == company_name).first()
                
                if not user or not company:
                    self.logger.warning(f"User '{user_email}' or company '{company_name}' not found")
                    continue
                
                # Parse timestamp
                query_time = None
                if timestamp_str:
                    try:
                        if isinstance(timestamp_str, str):
                            query_time = pd.to_datetime(timestamp_str)
                        else:
                            query_time = timestamp_str
                    except:
                        query_time = datetime.utcnow()
                else:
                    query_time = datetime.utcnow()
                
                # Create query
                query = Query(
                    query_text=query_text,
                    user_id=user.id,
                    company_id=company.id,
                    created_at=query_time
                )
                db.add(query)
                processed += 1
                
            except Exception as e:
                self.logger.error(f"Error processing query {row}: {e}")
                continue
        
        return processed
    
    async def _process_documents(self, documents_df: pd.DataFrame, db: Session) -> int:
        """Process documents from Excel data"""
        processed = 0
        
        for _, row in documents_df.iterrows():
            try:
                title = row.get('title', '').strip()
                content = row.get('content', '').strip()
                user_email = row.get('user_email', '').strip()
                company_name = row.get('company_name', '').strip()
                confidence = row.get('confidence', 0.8)
                
                if not all([title, content, user_email, company_name]):
                    continue
                
                # Find user and company
                user = db.query(User).filter(User.email == user_email).first()
                company = db.query(Company).filter(Company.name == company_name).first()
                
                if not user or not company:
                    continue
                
                # Create document
                document = Document(
                    title=title,
                    content=content,
                    source="Excel Import",
                    confidence=float(confidence),
                    created_by_user_id=user.id,
                    company_id=company.id
                )
                db.add(document)
                processed += 1
                
            except Exception as e:
                self.logger.error(f"Error processing document {row}: {e}")
                continue
        
        return processed
    
    def validate_excel_format(self, excel_file_path: str) -> Dict[str, Any]:
        """
        Validate Excel file format and return structure information.
        
        Returns:
            Dict with validation results and sheet information
        """
        try:
            excel_data = pd.read_excel(excel_file_path, sheet_name=None)
            
            validation = {
                "valid": True,
                "sheets": list(excel_data.keys()),
                "row_counts": {},
                "missing_sheets": [],
                "errors": []
            }
            
            # Check for expected sheets
            expected_sheets = ["Companies", "Users", "Queries"]
            for sheet in expected_sheets:
                if sheet in excel_data:
                    validation["row_counts"][sheet] = len(excel_data[sheet])
                else:
                    validation["missing_sheets"].append(sheet)
            
            # Validate required columns
            if "Companies" in excel_data:
                companies_df = excel_data["Companies"]
                if "name" not in companies_df.columns:
                    validation["errors"].append("Companies sheet missing 'name' column")
            
            if "Users" in excel_data:
                users_df = excel_data["Users"]
                required_cols = ["name", "email", "company_name"]
                missing_cols = [col for col in required_cols if col not in users_df.columns]
                if missing_cols:
                    validation["errors"].append(f"Users sheet missing columns: {missing_cols}")
            
            if "Queries" in excel_data:
                queries_df = excel_data["Queries"]
                required_cols = ["user_email", "company_name", "query_text"]
                missing_cols = [col for col in required_cols if col not in queries_df.columns]
                if missing_cols:
                    validation["errors"].append(f"Queries sheet missing columns: {missing_cols}")
            
            if validation["errors"] or validation["missing_sheets"]:
                validation["valid"] = False
            
            return validation
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Error reading Excel file: {str(e)}"
            }
    
    async def get_real_time_insights(self, db: Session) -> Dict[str, Any]:
        """
        Get real-time insights about the current data state.
        
        Returns:
            Dict with current system statistics and insights
        """
        try:
            companies = db.query(Company).count()
            users = db.query(User).count()
            queries = db.query(Query).count()
            documents = db.query(Document).count()
            
            # Get recent activity (last 24 hours)
            from datetime import datetime, timedelta
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            recent_queries = db.query(Query).filter(
                Query.created_at >= yesterday
            ).count()
            
            # Get top active companies by query count
            from sqlalchemy import func
            top_companies = db.query(
                Company.name,
                func.count(Query.id).label('query_count')
            ).join(Query).group_by(Company.id).order_by(
                func.count(Query.id).desc()
            ).limit(5).all()
            
            return {
                "total_companies": companies,
                "total_users": users,
                "total_queries": queries,
                "total_documents": documents,
                "recent_queries_24h": recent_queries,
                "top_active_companies": [
                    {"name": name, "query_count": count} 
                    for name, count in top_companies
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting insights: {e}")
            return {"error": str(e)}