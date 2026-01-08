"""
SFIA Integration Quality Test Script
Tests the quality of keyword extraction and SFIA skill mapping

Usage:
    cd backend
    source venv/bin/activate
    python test_sfia_quality.py
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.sfia_km_service import SFIAKnowledgeService
from services.enhance_jd_service import get_enhancer, reset_enhancer


# Sample JDs for testing different domains
SAMPLE_JDS = {
    "software_engineer": """
    Senior Software Engineer
    
    We are looking for an experienced Software Engineer to join our team.
    
    Responsibilities:
    - Design and develop high-quality software solutions
    - Write clean, maintainable code in Python and JavaScript
    - Participate in code reviews and mentor junior developers
    - Collaborate with product managers on requirements
    - Implement CI/CD pipelines and automated testing
    - Debug and resolve complex technical issues
    
    Requirements:
    - 5+ years of software development experience
    - Strong knowledge of Python, JavaScript, and React
    - Experience with cloud platforms (AWS/Azure)
    - Understanding of agile methodologies
    - Excellent problem-solving skills
    """,
    
    "data_engineer": """
    Data Engineer
    
    Join our data team to build scalable data pipelines.
    
    Responsibilities:
    - Design and build data pipelines and ETL processes
    - Work with big data technologies (Spark, Hadoop)
    - Manage data warehouses and data lakes
    - Ensure data quality and governance
    - Optimize query performance
    - Collaborate with data scientists and analysts
    
    Requirements:
    - 3+ years experience in data engineering
    - Proficiency in SQL and Python
    - Experience with Apache Spark and Kafka
    - Knowledge of data modeling
    - Understanding of data security practices
    """,
    
    "cybersecurity_analyst": """
    Cybersecurity Analyst
    
    Protect our organization from cyber threats.
    
    Responsibilities:
    - Monitor security systems and respond to incidents
    - Conduct vulnerability assessments and penetration testing
    - Implement security controls and policies
    - Investigate security breaches
    - Provide security awareness training
    - Maintain compliance with security standards
    
    Requirements:
    - 3+ years in information security
    - Knowledge of SIEM tools and threat detection
    - Experience with network security and firewalls
    - Familiarity with security frameworks (ISO 27001, NIST)
    - Security certifications preferred (CISSP, CEH)
    """,
    
    "project_manager": """
    IT Project Manager
    
    Lead technology projects from inception to delivery.
    
    Responsibilities:
    - Plan and manage IT project portfolios
    - Coordinate with stakeholders and technical teams
    - Manage project budgets and timelines
    - Identify and mitigate project risks
    - Report project status to senior management
    - Ensure quality delivery of projects
    
    Requirements:
    - 5+ years of IT project management
    - PMP or PRINCE2 certification preferred
    - Experience with Agile and Waterfall methodologies
    - Strong leadership and communication skills
    - Budget management experience
    """,
    
    "devops_engineer": """
    DevOps Engineer
    
    Build and maintain our cloud infrastructure.
    
    Responsibilities:
    - Manage Kubernetes clusters and container orchestration
    - Implement infrastructure as code using Terraform
    - Set up and maintain CI/CD pipelines
    - Monitor system performance and reliability
    - Automate deployment processes
    - Ensure high availability of services
    
    Requirements:
    - 4+ years in DevOps or SRE roles
    - Strong experience with Docker and Kubernetes
    - Proficiency in cloud platforms (AWS, GCP)
    - Experience with monitoring tools (Prometheus, Grafana)
    - Scripting skills (Bash, Python)
    """
}


def test_knowledge_graph_connection():
    """Test if Knowledge Graph is accessible"""
    print("\n" + "="*60)
    print("TEST 1: Knowledge Graph Connection")
    print("="*60)
    
    try:
        service = SFIAKnowledgeService()
        connected = service.is_connected()
        
        if connected:
            print("✅ Knowledge Graph is connected")
            stats = service.get_knowledge_graph_stats()
            print(f"   Skills in KG: {stats.get('skills_count', 'N/A')}")
            print(f"   Categories: {stats.get('categories_count', 'N/A')}")
            return True
        else:
            print("❌ Knowledge Graph is NOT connected")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Knowledge Graph: {e}")
        return False


def test_skill_search(service, test_keywords):
    """Test skill search for given keywords"""
    print("\n" + "="*60)
    print("TEST 2: SFIA Skill Search Quality")
    print("="*60)
    
    results = {}
    for keyword in test_keywords:
        skills = service.search_skills(keyword, limit=5)
        results[keyword] = skills
        
        print(f"\n🔍 Keyword: '{keyword}'")
        if skills:
            for skill in skills:
                print(f"   → {skill.get('code', 'N/A')}: {skill.get('name', 'N/A')}")
                if skill.get('category'):
                    print(f"      Category: {skill.get('category')}")
        else:
            print("   → No matches found")
    
    return results


def test_full_enhancement(jd_name, jd_text, org_context=None):
    """Test full enhancement workflow"""
    print("\n" + "="*60)
    print(f"TEST 3: Full Enhancement - {jd_name}")
    print("="*60)
    
    try:
        reset_enhancer()
        enhancer = get_enhancer()
        
        if not enhancer:
            print("❌ Failed to create enhancer")
            return None
        
        print(f"\nProcessing JD: {jd_name}")
        print("-" * 40)
        
        result = enhancer.enhance(jd_text, org_context or {})
        
        print("\n📋 RESULTS:")
        print(f"\n   Extracted Keywords ({len(result.get('extracted_keywords', []))}):")
        for kw in result.get('extracted_keywords', [])[:15]:
            print(f"      • {kw}")
        
        print(f"\n   Matched SFIA Skills ({len(result.get('skills', []))}):")
        for skill in result.get('skills', []):
            print(f"      • {skill.get('code')}: {skill.get('name')} (Level {skill.get('level')})")
            if skill.get('keyword_matched'):
                print(f"        ↳ Matched from: '{skill.get('keyword_matched')}'")
        
        print(f"\n   Knowledge Graph Connected: {result.get('knowledge_graph_connected', False)}")
        
        # Quality metrics
        keywords_count = len(result.get('extracted_keywords', []))
        skills_count = len(result.get('skills', []))
        match_rate = (skills_count / keywords_count * 100) if keywords_count > 0 else 0
        
        print(f"\n   📊 Quality Metrics:")
        print(f"      Keywords extracted: {keywords_count}")
        print(f"      SFIA skills matched: {skills_count}")
        print(f"      Match rate: {match_rate:.1f}%")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during enhancement: {e}")
        import traceback
        traceback.print_exc()
        return None


def run_all_tests():
    """Run all quality tests"""
    print("\n" + "#"*60)
    print("# SFIA INTEGRATION QUALITY TEST")
    print("#"*60)
    
    # Test 1: KG Connection
    kg_connected = test_knowledge_graph_connection()
    
    if not kg_connected:
        print("\n⚠️  Cannot proceed without Knowledge Graph connection")
        print("   Make sure Apache Jena Fuseki is running on localhost:3030")
        return
    
    # Test 2: Skill Search
    service = SFIAKnowledgeService()
    test_keywords = [
        "programming",
        "software development",
        "data analysis",
        "cybersecurity",
        "project management",
        "cloud computing",
        "DevOps",
        "machine learning",
        "agile",
        "leadership"
    ]
    test_skill_search(service, test_keywords)
    
    # Test 3: Full Enhancement
    print("\n" + "#"*60)
    print("# FULL ENHANCEMENT TESTS")
    print("#"*60)
    
    # Test with sample org context
    sample_org_context = {
        "company_name": "TechCorp Inc",
        "org_industry": "Technology",
        "company_culture": "Innovation-focused, collaborative",
        "role_type": "Permanent",
        "work_environment": "Hybrid"
    }
    
    results = {}
    for jd_name, jd_text in list(SAMPLE_JDS.items())[:2]:  # Test first 2 for speed
        result = test_full_enhancement(jd_name, jd_text, sample_org_context)
        if result:
            results[jd_name] = result
    
    # Summary
    print("\n" + "#"*60)
    print("# SUMMARY")
    print("#"*60)
    
    print("\n📊 Overall Results:")
    for jd_name, result in results.items():
        keywords = len(result.get('extracted_keywords', []))
        skills = len(result.get('skills', []))
        rate = (skills / keywords * 100) if keywords > 0 else 0
        print(f"   {jd_name}: {skills}/{keywords} skills matched ({rate:.1f}%)")
    
    print("\n✅ Quality test completed!")


if __name__ == "__main__":
    run_all_tests()
