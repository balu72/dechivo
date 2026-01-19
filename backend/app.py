from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
import os
import logging
import secrets
from datetime import datetime, timedelta, timezone

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from models import db, User
from auth import token_required, get_current_user
from services.sfia_km_service import get_sfia_service
from services.jd_services import get_enhancer, reset_enhancer, create_jd as create_jd_service, enhance_jd as enhance_jd_service
from services.email_service import send_verification_email
import time
from analytics import (
    track_enhancement_request,
    track_enhancement_success,
    track_enhancement_failure,
    track_api_error
)

# Import Knowledge Graph blueprint
from kg_routes import kg_bp

app = Flask(__name__)
CORS(app, 
     resources={r"/api/*": {"origins": "*"}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DEBUG'] = True

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Database Configuration
database_url = os.environ.get('DATABASE_URL', 'sqlite:///dechivo.db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(kg_bp)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dechivo_backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create tables
with app.app_context():
    db.create_all()
    logger.info("Database tables created")

# ============= AUTHENTICATION ROUTES =============

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    logger.info("POST /api/auth/register - Registration request received")
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'username', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        email = data.get('email').lower().strip()
        username = data.get('username').strip()
        password = data.get('password')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already taken'}), 400
        
        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        token_expires = datetime.utcnow() + timedelta(hours=24)
        
        # Create new user (not verified yet)
        user = User(
            email=email,
            username=username,
            full_name=data.get('full_name'),
            organization=data.get('organization'),
            is_verified=False,
            verification_token=verification_token,
            verification_token_expires=token_expires
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"User registered successfully: {username}")
        
        # Send verification email
        email_sent = send_verification_email(
            email=email,
            token=verification_token,
            name=data.get('full_name') or username
        )
        
        if email_sent:
            return jsonify({
                'success': True,
                'message': 'Registration successful! Please check your email to verify your account.',
                'requires_verification': True
            }), 201
        else:
            # Email failed but user is created - log verification URL for testing
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
            verification_url = f"{frontend_url}/verify-email?token={verification_token}"
            logger.info(f"📧 Email sending failed. For testing, use this verification URL: {verification_url}")
            
            return jsonify({
                'success': True,
                'message': 'Registration successful! Please request a verification email.',
                'requires_verification': True,
                'email_sent': False
            }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user and return tokens"""
    logger.info("POST /api/auth/login - Login request received")
    try:
        data = request.get_json()
        
        email_or_username = data.get('email_or_username', '').strip()
        password = data.get('password')
        
        if not email_or_username or not password:
            return jsonify({'error': 'Email/username and password are required'}), 400
        
        # Find user by email or username
        user = User.query.filter(
            (User.email == email_or_username.lower()) | 
            (User.username == email_or_username)
        ).first()
        
        if not user or not user.check_password(password):
            logger.warning(f"Login failed for: {email_or_username}")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Check if email is verified
        if not user.is_verified:
            return jsonify({
                'error': 'Please verify your email before logging in',
                'requires_verification': True,
                'email': user.email
            }), 403
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        # Generate tokens (identity must be string)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        logger.info(f"User logged in successfully: {user.username}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 200
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    logger.info("POST /api/auth/refresh - Token refresh request")
    try:
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'success': True,
            'access_token': access_token
        }), 200
    
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Token refresh failed'}), 500

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_me():
    """Get current user profile"""
    logger.info("GET /api/auth/me - Profile request")
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, int(current_user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to get profile'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client-side token removal)"""
    logger.info("POST /api/auth/logout - Logout request")
    # In a production app, you might want to implement token blacklisting
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200


@app.route('/api/auth/verify-email', methods=['POST'])
def verify_email():
    """Verify user email with token"""
    logger.info("POST /api/auth/verify-email - Verification request")
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Verification token is required'}), 400
        
        # Find user by token
        user = User.query.filter_by(verification_token=token).first()
        
        if not user:
            return jsonify({'error': 'Invalid verification token'}), 400
        
        # Check if token expired
        if user.verification_token_expires and user.verification_token_expires < datetime.utcnow():
            return jsonify({
                'error': 'Verification token has expired. Please request a new one.',
                'expired': True
            }), 400
        
        # Verify user
        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires = None
        db.session.commit()
        
        logger.info(f"User verified successfully: {user.username}")
        
        return jsonify({
            'success': True,
            'message': 'Email verified successfully! You can now log in.'
        }), 200
    
    except Exception as e:
        logger.error(f"Verification error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Verification failed'}), 500


@app.route('/api/auth/resend-verification', methods=['POST'])
def resend_verification():
    """Resend verification email"""
    logger.info("POST /api/auth/resend-verification - Resend request")
    try:
        data = request.get_json()
        email = data.get('email', '').lower().strip()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Don't reveal if email exists
            return jsonify({
                'success': True,
                'message': 'If this email is registered, a verification link will be sent.'
            }), 200
        
        if user.is_verified:
            return jsonify({'error': 'Email is already verified'}), 400
        
        # Generate new token
        verification_token = secrets.token_urlsafe(32)
        token_expires = datetime.utcnow() + timedelta(hours=24)
        
        user.verification_token = verification_token
        user.verification_token_expires = token_expires
        db.session.commit()
        
        # Send email
        email_sent = send_verification_email(
            email=email,
            token=verification_token,
            name=user.full_name or user.username
        )
        
        if email_sent:
            return jsonify({
                'success': True,
                'message': 'Verification email sent! Please check your inbox.'
            }), 200
        else:
            return jsonify({
                'error': 'Failed to send verification email. Please try again.'
            }), 500
    
    except Exception as e:
        logger.error(f"Resend verification error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to resend verification'}), 500

# ============= PUBLIC ROUTES =============

@app.route('/')
def index():
    logger.info("Index endpoint accessed")
    return jsonify({
        'message': 'Dechivo Backend API',
        'status': 'running',
        'version': '2.0.0'
    })

@app.route('/api/health')
def health_check():
    logger.info("Health check endpoint accessed")
    return jsonify({
        'status': 'healthy',
        'service': 'dechivo-backend',
        'version': '2.1.0'
    })

@app.route('/api/health/kg', methods=['GET'])
def kg_health_check():
    """Check Knowledge Graph connectivity and status"""
    logger.info("GET /api/health/kg - Knowledge Graph health check")
    try:
        sfia_service = get_sfia_service()
        
        if sfia_service.is_connected():
            stats = sfia_service.get_knowledge_graph_stats()
            return jsonify({
                'status': 'healthy',
                'connected': True,
                'fuseki_url': sfia_service.fuseki_url,
                'dataset': sfia_service.dataset,
                'stats': stats
            }), 200
        else:
            return jsonify({
                'status': 'unavailable',
                'connected': False,
                'message': 'Knowledge Graph not connected',
                'fallback_mode': True
            }), 503
    
    except Exception as e:
        logger.error(f"KG health check error: {str(e)}")
        return jsonify({
            'status': 'error',
            'connected': False,
            'error': str(e)
        }), 500

# ============= PROTECTED ROUTES =============

@app.route('/api/create-jd', methods=['POST'])
@jwt_required()
def create_jd_endpoint():
    """
    Endpoint to create a job description from organizational context only.
    This generates a new JD without requiring an existing one.
    
    Request body:
        org_context: dict - Organizational context including:
            - company_name: Name of the company
            - company_description: Brief description of the company
            - role_title: Title of the role
            - role_type: Type of role (permanent, contract, etc.)
            - role_grade: Grade/band of the role
            - reporting_to: Reporting manager/title
            - location: Work location
            - work_environment: Work environment (remote, hybrid, onsite)
            - role_context: Key skills (optional)
            - business_context: Experience level (optional)
    """
    logger.info("POST /api/create-jd - Create JD request received")
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, int(current_user_id))
        
        data = request.get_json()
        org_context = data.get('org_context', {})
        
        logger.info(f"JD creation requested by user: {user.username}")
        logger.info(f"Org context provided: {list(org_context.keys())}")
        
        # Validate required fields
        required_fields = ['company_name', 'company_description', 'role_title', 
                          'role_type', 'role_grade', 'reporting_to', 
                          'location', 'work_environment']
        
        missing_fields = [f for f in required_fields if not org_context.get(f)]
        if missing_fields:
            logger.warning(f"Create JD failed: Missing fields: {missing_fields}")
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Track creation request
        start_time = time.time()
        track_enhancement_request(
            user_id=str(current_user_id),
            jd_length=0,
            has_org_context=True
        )
        
        # Use the create_jd API function
        result = create_jd_service(org_context)
        
        if not result.get('success') or not result.get('job_description'):
            logger.error("Create JD failed: No job description generated")
            return jsonify({
                'error': result.get('error') or 'Failed to generate job description. Please try again.'
            }), 500
        
        # Track success
        duration_ms = int((time.time() - start_time) * 1000)
        track_enhancement_success(
            user_id=str(current_user_id),
            skills_count=len(result.get('skills', [])),
            duration_ms=duration_ms,
            llm_provider='openai',
            kg_connected=True
        )
        
        logger.info(f"JD created successfully for role: {org_context.get('role_title')}")
        
        return jsonify({
            'success': True,
            'job_description': result.get('job_description'),
            'skills': result.get('skills', []),
            'extracted_keywords': result.get('extracted_keywords', [])
        }), 200
        
    except Exception as e:
        logger.error(f"Create JD error: {str(e)}", exc_info=True)
        track_enhancement_failure(
            user_id=str(current_user_id) if 'current_user_id' in locals() else 'unknown',
            error=str(e)
        )
        track_api_error(
            user_id=str(current_user_id) if 'current_user_id' in locals() else 'unknown',
            endpoint='/api/create-jd',
            error=str(e)
        )
        return jsonify({
            'error': f'Error creating job description: {str(e)}'
        }), 500

@app.route('/api/enhance-jd', methods=['POST'])
@jwt_required()
def enhance_jd_endpoint():
    """
    Endpoint to enhance job descriptions using SFIA framework (Protected)
    Uses Knowledge Graph for skill mapping when available
    
    Request body:
        job_description: str - The job description text to enhance
        org_context: dict (optional) - Organizational context including:
            - org_industry: Industry sector
            - company_name: Name of the company
            - company_description: Brief description of the company
            - company_culture: Company culture description
            - company_values: Core company values
            - business_context: Business context for the role
            - role_context: Company-specific role context
            - role_type: Type of role (permanent, contract, etc.)
            - role_grade: Grade/band of the role
            - location: Work location
            - work_environment: Work environment (remote, hybrid, onsite)
            - reporting_to: Reporting manager/title
    """
    logger.info("POST /api/enhance-jd - Enhancement request received")
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, int(current_user_id))
        
        data = request.get_json()
        job_description = data.get('job_description', '')
        org_context = data.get('org_context', {})
        
        logger.info(f"JD enhancement requested by user: {user.username}")
        logger.info(f"JD length: {len(job_description)} characters")
        if org_context:
            logger.info(f"Org context provided: {list(org_context.keys())}")
        
        # JD is optional - can generate from context alone
        if not job_description and not org_context:
            logger.warning("Enhancement failed: No job description or context provided")
            return jsonify({
                'error': 'Please provide either a job description or fill in the context fields'
            }), 400
        
        # Track enhancement request
        start_time = time.time()
        track_enhancement_request(
            user_id=str(current_user_id),
            jd_length=len(job_description),
            has_org_context=bool(org_context)
        )
        
        # Use the real enhancement service with Knowledge Graph
        enhancer = get_enhancer()
        enhancement_result = enhancer.enhance(job_description, org_context=org_context)
        
        # Get skills and regenerated JD
        skills = enhancement_result.get('skills', [])
        regenerated_jd = enhancement_result.get('regenerated_jd', '')
        
        # Use regenerated JD if available, otherwise format manually
        if regenerated_jd:
            enhanced_jd = regenerated_jd
        else:
            # Fallback: Format enhanced JD output manually
            skills_text = "\n".join([
                f"- {s.get('name', s.get('code', 'Unknown'))} ({s.get('code', 'N/A')}) - Level {s.get('level', 'N/A')} ({s.get('level_name', '')})\n  {s.get('level_description', '')}" 
                for s in skills
            ])
            
            enhanced_jd = f"""# Enhanced Job Description (SFIA-Based)

## Original Job Description:
{job_description}

---

## SFIA Skills & Competencies Identified:

{skills_text if skills_text else "No specific SFIA skills identified."}

---

**Keywords Extracted:** {', '.join(enhancement_result.get('extracted_keywords', []))}

**Knowledge Graph Status:** {'Connected ✓' if enhancement_result.get('knowledge_graph_connected') else 'Fallback Mode'}

**Enhanced by:** {user.username}
**Organization:** {user.organization or 'N/A'}
"""
        
        logger.info(f"JD enhanced successfully. Skills found: {len(skills)}")
        
        # Track successful enhancement
        duration_ms = int((time.time() - start_time) * 1000)
        track_enhancement_success(
            user_id=str(current_user_id),
            skills_count=len(skills),
            duration_ms=duration_ms,
            llm_provider=enhancer.llm_provider if hasattr(enhancer, 'llm_provider') else 'unknown',
            kg_connected=enhancement_result.get('knowledge_graph_connected', False)
        )
        
        return jsonify({
            'success': True,
            'enhanced_jd': enhanced_jd,
            'regenerated_jd': regenerated_jd,
            'skills': skills,
            'skills_count': len(skills),
            'extracted_keywords': enhancement_result.get('extracted_keywords', []),
            'knowledge_graph_connected': enhancement_result.get('knowledge_graph_connected', False),
            'workflow_messages': enhancement_result.get('workflow_messages', []),
            'message': 'Job description enhanced successfully',
            'processing_time_ms': duration_ms
        })
    
    except Exception as e:
        logger.error(f"Error enhancing JD: {str(e)}", exc_info=True)
        
        # Track failure
        duration_ms = int((time.time() - start_time) * 1000) if 'start_time' in locals() else 0
        track_enhancement_failure(
            user_id=str(current_user_id) if 'current_user_id' in locals() else 'unknown',
            error=str(e),
            duration_ms=duration_ms
        )
        
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/search-skills', methods=['GET'])
@jwt_required()
def search_skills_endpoint():
    """
    Endpoint to search skills for autocomplete (Protected)
    Searches both common skills and SFIA framework skills
    
    Query params:
        query: Search keyword (required)
        limit: Maximum number of results (optional, default 10)
    """
    logger.info("GET /api/search-skills - Skill search request received")
    try:
        current_user_id = get_jwt_identity()
        query = request.args.get('query', '').strip().lower()
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        if len(query) < 2:
            return jsonify({'skills': []}), 200
        
        logger.info(f"Searching skills with query: '{query}', limit: {limit}")
        
        all_results = []
        
        # 1. Search common skills from JSON file
        try:
            import json
            common_skills_path = os.path.join(os.path.dirname(__file__), 'data', 'common_skills.json')
            if os.path.exists(common_skills_path):
                with open(common_skills_path, 'r') as f:
                    common_skills_data = json.load(f)
                    
                for skill in common_skills_data.get('skills', []):
                    skill_name = skill['name'].lower()
                    skill_desc = skill.get('description', '').lower()
                    skill_category = skill.get('category', '').lower()
                    
                    # Check if query matches name, description, or category
                    if (query in skill_name or 
                        query in skill_desc or 
                        query in skill_category):
                        
                        # Calculate relevance score
                        score = 0
                        if skill_name.startswith(query):
                            score = 100  # Exact start match
                        elif query == skill_name:
                            score = 95  # Exact match
                        elif query in skill_name:
                            score = 80  # Partial name match
                        elif query in skill_category:
                            score = 60  # Category match
                        else:
                            score = 40  # Description match
                        
                        all_results.append({
                            'code': '',
                            'name': skill['name'],
                            'description': skill.get('description', ''),
                            'category': skill.get('category', ''),
                            'source': 'common',
                            'score': score
                        })
        except Exception as e:
            logger.warning(f"Error loading common skills: {e}")
        
        # 2. Search SFIA Knowledge Graph
        try:
            sfia_service = get_sfia_service()
            if sfia_service.is_connected():
                sfia_skills = sfia_service.search_skills(query, limit=limit)
                
                for skill in sfia_skills:
                    all_results.append({
                        'code': skill.get('code', ''),
                        'name': skill.get('name', ''),
                        'description': skill.get('description', '')[:100] + '...' if len(skill.get('description', '')) > 100 else skill.get('description', ''),
                        'category': skill.get('category', ''),
                        'source': 'sfia',
                        'score': 50  # SFIA skills get medium priority
                    })
        except Exception as e:
            logger.warning(f"Error searching SFIA: {e}")
        
        # 3. Search Unified Knowledge Graph (ESCO, O*NET, Singapore, Canada)
        try:
            import sys
            kg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'knowledge-graph', 'scripts')
            if kg_path not in sys.path:
                sys.path.insert(0, kg_path)
            
            from kg_service import kg_service
            
            # Search skills in unified KG
            kg_skills = kg_service.find_skills_by_keyword(query)
            
            for skill in kg_skills[:limit]:  # Limit KG results
                all_results.append({
                    'code': '',
                    'name': skill.get('skillLabel', skill.get('label', '')),
                    'description': skill.get('description', '')[:100] + '...' if skill.get('description', '') and len(skill.get('description', '')) > 100 else skill.get('description', ''),
                    'category': skill.get('category', ''),
                    'source': 'kg',  # Knowledge Graph (4 frameworks)
                    'score': 70  # KG skills get high priority (international standards)
                })
            
            logger.info(f"Found {len(kg_skills)} skills from unified KG")
        except Exception as e:
            logger.warning(f"Error searching unified KG: {e}")
        
        # 4. Sort by relevance score and remove duplicates
        all_results.sort(key=lambda x: x['score'], reverse=True)
        
        # Remove duplicates (prefer: common > KG > SFIA for same name)
        seen_names = set()
        unique_results = []
        for result in all_results:
            name_lower = result['name'].lower()
            if name_lower not in seen_names:
                seen_names.add(name_lower)
                unique_results.append(result)
        
        # Limit results
        final_results = unique_results[:limit]
        
        # Remove score from response
        for result in final_results:
            result.pop('score', None)
        
        logger.info(f"Found {len(final_results)} matching skills (common: {sum(1 for r in final_results if r['source'] == 'common')}, KG: {sum(1 for r in final_results if r['source'] == 'kg')}, SFIA: {sum(1 for r in final_results if r['source'] == 'sfia')})")
        
        return jsonify({
            'skills': final_results,
            'count': len(final_results),
            'sources': {
                'common': sum(1 for r in final_results if r['source'] == 'common'),
                'kg': sum(1 for r in final_results if r['source'] == 'kg'),
                'sfia': sum(1 for r in final_results if r['source'] == 'sfia')
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching skills: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload-jd', methods=['POST'])
@jwt_required()
def upload_jd():
    """
    Endpoint to upload job description file (Protected)
    """
    logger.info("POST /api/upload-jd - File upload request received")
    try:
        current_user_id = get_jwt_identity()
        user = db.session.get(User, int(current_user_id))
        
        if 'file' not in request.files:
            logger.warning("Upload failed: No file in request")
            return jsonify({
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            logger.warning("Upload failed: Empty filename")
            return jsonify({
                'error': 'No file selected'
            }), 400
        
        logger.info(f"Processing file: {file.filename} uploaded by {user.username}")
        
        # Read file content
        content = file.read().decode('utf-8')
        
        logger.info(f"File uploaded successfully: {file.filename}, size: {len(content)} characters")
        return jsonify({
            'success': True,
            'content': content,
            'filename': file.filename,
            'message': 'File uploaded successfully'
        })
    
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
