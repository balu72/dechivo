"""
Flask API Routes for Knowledge Graph Integration

Add these routes to your Flask backend (app.py or a new blueprint)
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
import sys
import os

# Add knowledge-graph scripts to path
kg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'knowledge-graph', 'scripts')
sys.path.insert(0, kg_path)

from kg_service import KnowledgeGraphService

# Create blueprint
kg_bp = Blueprint('knowledge_graph', __name__, url_prefix='/api/kg')

# Initialize service
kg_service = KnowledgeGraphService(
    endpoint_url=os.getenv('FUSEKI_ENDPOINT', 'http://localhost:3030/unified/query'),
    username=os.getenv('FUSEKI_USERNAME', 'admin'),
    password=os.getenv('FUSEKI_PASSWORD', 'admin123')
)


@kg_bp.route('/occupations/search', methods=['GET'])
def search_occupations():
    """
    Search for occupations by keyword
    
    Query params:
        q: Search query
        
    Example: GET /api/kg/occupations/search?q=software
    """
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({
            'error': 'Query parameter "q" is required'
        }), 400
    
    try:
        results = kg_service.search_occupations(query)
        return jsonify({
            'success': True,
            'query': query,
            'count': len(results),
            'results': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kg_bp.route('/occupations/<path:occupation_label>/profile', methods=['GET'])
def get_occupation_profile(occupation_label: str):
    """
    Get complete profile for an occupation
    
    Example: GET /api/kg/occupations/Software Developer/profile
    """
    try:
        profile = kg_service.get_occupation_complete_profile(occupation_label)
        
        if not profile.get('found'):
            return jsonify(profile), 404
        
        return jsonify(profile)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kg_bp.route('/occupations/<path:occupation_label>/skills', methods=['GET'])
def get_occupation_skills(occupation_label: str):
    """
    Get skills for an occupation
    
    Example: GET /api/kg/occupations/Software Developer/skills
    """
    try:
        # First find the occupation
        occupations = kg_service.search_occupations(occupation_label)
        
        if not occupations:
            return jsonify({
                'success': False,
                'message': f"No occupation found matching '{occupation_label}'"
            }), 404
        
        occupation_uri = occupations[0].get('occupation', '')
        skills = kg_service.get_occupation_skills(occupation_uri)
        
        return jsonify({
            'success': True,
            'occupation': occupations[0],
            'skills': skills
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kg_bp.route('/occupations/<path:occupation_label>/similar', methods=['GET'])
def find_similar_occupations(occupation_label: str):
    """
    Find occupations similar to the given one
    
    Query params:
        min_skills: Minimum common skills (default: 5)
        
    Example: GET /api/kg/occupations/Software Developer/similar?min_skills=3
    """
    try:
        min_skills = int(request.args.get('min_skills', 5))
        similar = kg_service.find_similar_occupations(occupation_label, min_skills)
        
        return jsonify({
            'success': True,
            'occupation': occupation_label,
            'min_common_skills': min_skills,
            'count': len(similar),
            'similar_occupations': similar
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kg_bp.route('/skills/search', methods=['GET'])
def search_skills():
    """
    Search for skills by keyword
    
    Query params:
        q: Search query
        
    Example: GET /api/kg/skills/search?q=python
    """
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({
            'error': 'Query parameter "q" is required'
        }), 400
    
    try:
        results = kg_service.find_skills_by_keyword(query)
        return jsonify({
            'success': True,
            'query': query,
            'count': len(results),
            'results': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kg_bp.route('/skills/<path:skill_name>/occupations', methods=['GET'])
def get_skill_occupations(skill_name: str):
    """
    Find occupations that require a specific skill
    
    Example: GET /api/kg/skills/Python Programming/occupations
    """
    try:
        occupations = kg_service.get_occupations_requiring_skill(skill_name)
        
        return jsonify({
            'success': True,
            'skill': skill_name,
            'count': len(occupations),
            'occupations': occupations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kg_bp.route('/jd/enrich', methods=['POST'])
def enrich_jd():
    """
    Enrich a job description with skills from the knowledge graph
    
    Request body:
        {
            "job_title": "Software Developer",
            "existing_skills": ["Python", "SQL"]
        }
        
    Example: POST /api/kg/jd/enrich
    """
    try:
        data = request.get_json()
        
        if not data or 'job_title' not in data:
            return jsonify({
                'error': 'job_title is required in request body'
            }), 400
        
        job_title = data['job_title']
        existing_skills = data.get('existing_skills', [])
        
        enrichment = kg_service.enrich_jd_with_skills(job_title, existing_skills)
        
        if not enrichment.get('success'):
            return jsonify(enrichment), 404
        
        return jsonify(enrichment)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kg_bp.route('/career/skill-gap', methods=['POST'])
def calculate_skill_gap():
    """
    Calculate skill gap between current and target occupation
    
    Request body:
        {
            "current_occupation": "Junior Developer",
            "target_occupation": "Senior Developer"
        }
        
    Example: POST /api/kg/career/skill-gap
    """
    try:
        data = request.get_json()
        
        if not data or 'current_occupation' not in data or 'target_occupation' not in data:
            return jsonify({
                'error': 'current_occupation and target_occupation are required'
            }), 400
        
        current = data['current_occupation']
        target = data['target_occupation']
        
        gap_analysis = kg_service.calculate_skill_gap(current, target)
        
        if not gap_analysis.get('success'):
            return jsonify(gap_analysis), 404
        
        return jsonify(gap_analysis)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@kg_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify KG connectivity
    
    Example: GET /api/kg/health
    """
    try:
        # Try a simple query
        results = kg_service._execute_query(
            "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o } LIMIT 1"
        )
        
        return jsonify({
            'status': 'healthy',
            'endpoint': kg_service.endpoint_url,
            'connected': len(results) > 0
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'endpoint': kg_service.endpoint_url,
            'error': str(e)
        }), 503


# Error handlers
@kg_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404


@kg_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# Example: How to register this blueprint in app.py
"""
from backend.kg_routes import kg_bp

app.register_blueprint(kg_bp)
"""
