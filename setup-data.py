#!/usr/bin/env python3
"""
Setup script to populate the database with sample data for testing
"""

import requests
import json
import sys
import time

# Configuration
API_BASE_URL = "http://localhost:8000/api"
SAMPLE_COMPANIES = [
    {"name": "TechCorp Solutions"},
    {"name": "InnovateAI Labs"},
    {"name": "DataFlow Systems"}
]

SAMPLE_USERS = [
    {"name": "Alice Johnson", "email": "alice@techcorp.com"},
    {"name": "Bob Smith", "email": "bob@techcorp.com"},
    {"name": "Carol Davis", "email": "carol@innovateai.com"},
    {"name": "David Wilson", "email": "david@innovateai.com"},
    {"name": "Eve Brown", "email": "eve@dataflow.com"},
    {"name": "Frank Miller", "email": "frank@dataflow.com"}
]

SAMPLE_QUERIES = [
    "What are the best practices for API design?",
    "How do we implement machine learning models in production?",
    "What is the difference between SQL and NoSQL databases?",
    "How do we set up continuous integration and deployment?",
    "What are the latest trends in cloud computing?",
    "How do we ensure data security in web applications?",
    "What is the role of microservices in modern architecture?",
    "How do we optimize database performance?",
    "What are the benefits of containerization with Docker?",
    "How do we implement real-time data processing?"
]

def wait_for_api():
    """Wait for API to be available"""
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{API_BASE_URL[:-4]}/health")
            if response.status_code == 200:
                print("✅ API is ready!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        
        print(f"⏳ Waiting for API... ({i+1}/{max_retries})")
        time.sleep(2)
    
    print("❌ API is not responding. Please check if the backend is running.")
    return False

def create_companies():
    """Create sample companies"""
    print("📊 Creating sample companies...")
    companies = []
    
    for company_data in SAMPLE_COMPANIES:
        try:
            response = requests.post(f"{API_BASE_URL}/companies", json=company_data)
            if response.status_code == 201:
                company = response.json()
                companies.append(company)
                print(f"   ✅ Created company: {company['name']}")
            else:
                print(f"   ❌ Failed to create company {company_data['name']}: {response.text}")
        except Exception as e:
            print(f"   ❌ Error creating company {company_data['name']}: {str(e)}")
    
    return companies

def create_users(companies):
    """Create sample users for each company"""
    print("👥 Creating sample users...")
    users = []
    
    # Distribute users across companies
    users_per_company = len(SAMPLE_USERS) // len(companies)
    
    for i, company in enumerate(companies):
        start_idx = i * users_per_company
        end_idx = start_idx + users_per_company
        if i == len(companies) - 1:  # Last company gets remaining users
            end_idx = len(SAMPLE_USERS)
        
        company_users = SAMPLE_USERS[start_idx:end_idx]
        
        for user_data in company_users:
            user_data_with_company = {
                **user_data,
                "company_id": company["id"]
            }
            
            try:
                response = requests.post(f"{API_BASE_URL}/users", json=user_data_with_company)
                if response.status_code == 201:
                    user = response.json()
                    users.append(user)
                    print(f"   ✅ Created user: {user['name']} at {company['name']}")
                else:
                    print(f"   ❌ Failed to create user {user_data['name']}: {response.text}")
            except Exception as e:
                print(f"   ❌ Error creating user {user_data['name']}: {str(e)}")
    
    return users

def create_sample_queries(users):
    """Create sample queries and documents for users"""
    print("🔍 Creating sample queries and documents...")
    
    import random
    
    for user in users:
        # Create 2-4 queries per user
        num_queries = random.randint(2, 4)
        user_queries = random.sample(SAMPLE_QUERIES, num_queries)
        
        for query in user_queries:
            search_data = {
                "query": query,
                "user_id": user["id"],
                "company_id": user["company_id"],
                "save_as_document": True
            }
            
            try:
                response = requests.post(f"{API_BASE_URL}/search", json=search_data)
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Created query for {user['name']}: {query[:50]}...")
                else:
                    print(f"   ❌ Failed to create query: {response.text}")
                    
                # Add small delay to avoid overwhelming the LLM API
                time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ Error creating query: {str(e)}")

def main():
    """Main setup function"""
    print("🚀 Setting up Discover vNext with sample data...")
    print("=" * 60)
    
    # Wait for API
    if not wait_for_api():
        sys.exit(1)
    
    try:
        # Create companies
        companies = create_companies()
        if not companies:
            print("❌ No companies created. Exiting.")
            sys.exit(1)
        
        # Create users
        users = create_users(companies)
        if not users:
            print("❌ No users created. Exiting.")
            sys.exit(1)
        
        # Create sample queries (optional - requires OpenAI API key)
        create_queries = input("\n🤖 Do you want to create sample queries using OpenAI? (y/n): ").lower().strip()
        if create_queries == 'y':
            print("⚠️  This will use your OpenAI API credits. Make sure your API key is configured.")
            confirm = input("Continue? (y/n): ").lower().strip()
            if confirm == 'y':
                create_sample_queries(users)
        
        print("\n" + "=" * 60)
        print("🎉 Setup completed successfully!")
        print(f"📊 Created {len(companies)} companies")
        print(f"👥 Created {len(users)} users")
        print("\n💡 You can now:")
        print("   1. Open http://localhost:3000 to access the frontend")
        print("   2. Select a company and user from the header")
        print("   3. Try searching or exploring recommendations")
        print("   4. Access API docs at http://localhost:8000/docs")
        
    except KeyboardInterrupt:
        print("\n⏹️  Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()