#!/usr/bin/env python3
"""
Add more sample documents for comprehensive recommendation testing
"""
import sqlite3
import random
from datetime import datetime, timedelta

# Sample documents with diverse topics for TechCorp
techcorp_docs = [
    {
        "title": "Introduction to Cloud Computing: AWS vs Azure vs GCP",
        "content": "Cloud computing has revolutionized how businesses deploy and manage their IT infrastructure. Amazon Web Services (AWS) leads the market with comprehensive services including EC2, S3, and Lambda. Microsoft Azure provides strong enterprise integration with Office 365 and Active Directory. Google Cloud Platform (GCP) excels in machine learning and data analytics with BigQuery and TensorFlow integration. Each platform offers unique advantages: AWS for market maturity, Azure for Microsoft ecosystem integration, and GCP for AI/ML capabilities.",
        "source": "Cloud Architecture Guide",
        "confidence": 0.88,
        "created_by_user_id": 1  # Alice
    },
    {
        "title": "DevOps Best Practices: CI/CD Pipeline Implementation",
        "content": "Continuous Integration and Continuous Deployment (CI/CD) pipelines are essential for modern software development. Key practices include automated testing, code quality gates, infrastructure as code, and deployment automation. Popular tools include Jenkins, GitLab CI, GitHub Actions, and Azure DevOps. Implementing proper branching strategies, automated rollbacks, and monitoring ensures reliable deployments. Security scanning and compliance checks should be integrated into every pipeline stage.",
        "source": "DevOps Handbook",
        "confidence": 0.91,
        "created_by_user_id": 2  # Bob
    },
    {
        "title": "Python for Data Science: NumPy, Pandas, and Scikit-learn",
        "content": "Python has become the de facto language for data science due to its rich ecosystem of libraries. NumPy provides fundamental array operations and mathematical functions. Pandas offers powerful data manipulation and analysis tools with DataFrames. Scikit-learn delivers comprehensive machine learning algorithms for classification, regression, and clustering. Jupyter notebooks provide an interactive environment for data exploration and visualization.",
        "source": "Data Science Guide",
        "confidence": 0.89,
        "created_by_user_id": 1  # Alice
    },
    {
        "title": "Kubernetes Container Orchestration: Deployment and Scaling",
        "content": "Kubernetes has become the standard for container orchestration, enabling automated deployment, scaling, and management of containerized applications. Key concepts include pods, services, deployments, and ingress controllers. Kubernetes provides self-healing capabilities, horizontal scaling, and service discovery. Best practices include using namespaces for isolation, implementing resource limits, and following security guidelines with RBAC.",
        "source": "Container Platform Guide",
        "confidence": 0.87,
        "created_by_user_id": 2  # Bob
    },
    {
        "title": "Database Design Patterns: SQL vs NoSQL Decision Framework",
        "content": "Choosing between SQL and NoSQL databases depends on specific use case requirements. SQL databases excel in ACID compliance, complex queries, and structured data. Popular options include PostgreSQL, MySQL, and SQL Server. NoSQL databases offer horizontal scaling and flexible schemas, with MongoDB for documents, Redis for caching, and Cassandra for distributed systems. Consider data consistency requirements, scalability needs, and query complexity when making decisions.",
        "source": "Database Architecture",
        "confidence": 0.85,
        "created_by_user_id": 1  # Alice
    },
    {
        "title": "API Design Principles: RESTful Services and GraphQL",
        "content": "Well-designed APIs are crucial for modern applications. RESTful APIs follow standard HTTP methods (GET, POST, PUT, DELETE) and status codes. Best practices include consistent naming conventions, proper versioning, and comprehensive documentation. GraphQL offers an alternative approach with strongly typed schemas and efficient data fetching. Consider API security with OAuth 2.0, rate limiting, and input validation.",
        "source": "API Design Guide",
        "confidence": 0.90,
        "created_by_user_id": 2  # Bob
    },
    {
        "title": "Frontend Frameworks Comparison: React vs Vue vs Angular",
        "content": "Modern frontend frameworks have transformed web development. React offers component-based architecture with a large ecosystem and strong community support. Vue.js provides gentle learning curve with excellent documentation and performance. Angular delivers a full-featured framework with TypeScript integration and comprehensive tooling. Consider project requirements, team expertise, and long-term maintenance when choosing frameworks.",
        "source": "Frontend Development",
        "confidence": 0.86,
        "created_by_user_id": 1  # Alice
    },
    {
        "title": "Cybersecurity Fundamentals: Threat Detection and Response",
        "content": "Cybersecurity threats continue to evolve, requiring comprehensive defense strategies. Key components include network security, endpoint protection, identity management, and incident response. Implement defense in depth with firewalls, intrusion detection systems, and security monitoring. Regular security assessments, employee training, and patch management are essential. Consider zero-trust architecture and multi-factor authentication for enhanced security.",
        "source": "Security Framework",
        "confidence": 0.93,
        "created_by_user_id": 2  # Bob
    },
    {
        "title": "Agile Project Management: Scrum and Kanban Methodologies",
        "content": "Agile methodologies have revolutionized project management in software development. Scrum provides structured sprints with defined roles (Product Owner, Scrum Master, Development Team) and ceremonies (Sprint Planning, Daily Standups, Retrospectives). Kanban focuses on visual workflow management and continuous delivery. Both emphasize collaboration, adaptability, and customer feedback for successful project outcomes.",
        "source": "Agile Practices",
        "confidence": 0.84,
        "created_by_user_id": 1  # Alice
    },
    {
        "title": "Microservices Architecture: Design Patterns and Best Practices",
        "content": "Microservices architecture breaks monolithic applications into smaller, independent services. Benefits include scalability, technology diversity, and fault isolation. Key patterns include API Gateway, Circuit Breaker, and Event Sourcing. Challenges include distributed system complexity, data consistency, and network communication. Consider service boundaries, data ownership, and monitoring strategies for successful implementation.",
        "source": "Architecture Patterns",
        "confidence": 0.88,
        "created_by_user_id": 2  # Bob
    }
]

def add_sample_documents():
    """Add comprehensive sample documents to the database"""
    
    # Connect to database
    conn = sqlite3.connect('backend/discover.db')
    cursor = conn.cursor()
    
    print("📝 Adding sample documents for comprehensive recommendations...")
    
    # Add documents for TechCorp (company_id = 1)
    company_id = 1
    base_date = datetime.now() - timedelta(days=30)
    
    for i, doc in enumerate(techcorp_docs):
        # Spread documents across time for realistic timestamps
        created_at = base_date + timedelta(days=i*2, hours=random.randint(1, 23))
        
        cursor.execute("""
            INSERT INTO documents (title, content, source, confidence, created_by_user_id, company_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            doc["title"],
            doc["content"],
            doc["source"],
            doc["confidence"],
            doc["created_by_user_id"],
            company_id,
            created_at.isoformat()
        ))
    
    # Add some documents for other companies too (P&G, etc.)
    pg_docs = [
        {
            "title": "Consumer Behavior Analysis: Understanding Market Trends",
            "content": "Consumer behavior analysis is crucial for successful product marketing. Key factors include demographic trends, purchasing patterns, and brand loyalty. Market research techniques include surveys, focus groups, and behavioral analytics. Understanding customer journey touchpoints enables targeted marketing strategies. Digital transformation has shifted consumer expectations toward personalized experiences.",
            "source": "Marketing Research",
            "confidence": 0.87,
            "created_by_user_id": 7  # Skand Vijay from P&G
        },
        {
            "title": "Supply Chain Optimization: Global Logistics Management",
            "content": "Effective supply chain management ensures product availability while minimizing costs. Key components include demand forecasting, inventory optimization, and supplier relationship management. Technology solutions like ERP systems and IoT sensors provide real-time visibility. Sustainability considerations include carbon footprint reduction and ethical sourcing practices.",
            "source": "Supply Chain Guide",
            "confidence": 0.89,
            "created_by_user_id": 7
        }
    ]
    
    # Add P&G documents (company_id = 4)
    for doc in pg_docs:
        created_at = datetime.now() - timedelta(days=random.randint(1, 20))
        cursor.execute("""
            INSERT INTO documents (title, content, source, confidence, created_by_user_id, company_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            doc["title"],
            doc["content"],
            doc["source"],
            doc["confidence"],
            doc["created_by_user_id"],
            4,  # P&G company_id
            created_at.isoformat()
        ))
    
    # Commit changes
    conn.commit()
    
    # Get final counts
    cursor.execute("SELECT COUNT(*) FROM documents WHERE company_id = 1")
    techcorp_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM documents WHERE company_id = 4") 
    pg_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"✅ Added sample documents:")
    print(f"   📊 TechCorp: {techcorp_count} total documents")
    print(f"   📊 P&G: {pg_count} total documents")
    print(f"   🎯 Ready for 20+ recommendations per user!")
    
if __name__ == "__main__":
    add_sample_documents()