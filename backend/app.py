from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
import os
import logging
from datetime import datetime, timedelta
from models import db, User
from auth import token_required, get_current_user

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
        
        # Create new user
        user = User(
            email=email,
            username=username,
            full_name=data.get('full_name'),
            organization=data.get('organization')
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"User registered successfully: {username}")
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
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
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
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
        user = User.query.get(current_user_id)
        
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
        'service': 'dechivo-backend'
    })

# ============= PROTECTED ROUTES =============

@app.route('/api/enhance-jd', methods=['POST'])
@jwt_required()
def enhance_jd():
    """
    Endpoint to enhance job descriptions using SFIA framework (Protected)
    """
    logger.info("POST /api/enhance-jd - Enhancement request received")
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        data = request.get_json()
        job_description = data.get('job_description', '')
        
        logger.info(f"JD enhancement requested by user: {user.username}")
        logger.info(f"JD length: {len(job_description)} characters")
        
        if not job_description:
            logger.warning("Enhancement failed: No job description provided")
            return jsonify({
                'error': 'Job description is required'
            }), 400
        
        # TODO: Implement actual JD enhancement logic
        # This is a placeholder response
        enhanced_jd = f"""Enhanced JD (SFIA-Based):

{job_description}

--- SFIA COMPETENCIES ---

Relevant Skills:
- Software Development (Level 4)
- System Design (Level 3)
- Quality Assurance (Level 3)

Enhanced by: {user.username}
Organization: {user.organization or 'N/A'}
"""
        
        logger.info(f"JD enhanced successfully. Output length: {len(enhanced_jd)} characters")
        return jsonify({
            'success': True,
            'enhanced_jd': enhanced_jd,
            'message': 'Job description enhanced successfully'
        })
    
    except Exception as e:
        logger.error(f"Error enhancing JD: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/api/upload-jd', methods=['POST'])
@jwt_required()
def upload_jd():
    """
    Endpoint to upload job description file (Protected)
    """
    logger.info("POST /api/upload-jd - File upload request received")
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
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
