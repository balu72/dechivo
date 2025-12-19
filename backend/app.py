from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['DEBUG'] = True

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

@app.route('/')
def index():
    logger.info("Index endpoint accessed")
    return jsonify({
        'message': 'Dechivo Backend API',
        'status': 'running',
        'version': '1.0.0'
    })

@app.route('/api/health')
def health_check():
    logger.info("Health check endpoint accessed")
    return jsonify({
        'status': 'healthy',
        'service': 'dechivo-backend'
    })

@app.route('/api/enhance-jd', methods=['POST'])
def enhance_jd():
    """
    Endpoint to enhance job descriptions using SFIA framework
    """
    logger.info("POST /api/enhance-jd - Enhancement request received")
    try:
        data = request.get_json()
        job_description = data.get('job_description', '')
        
        logger.info(f"JD length: {len(job_description)} characters")
        logger.info(f"JD content: {job_description}")

        
        if not job_description:
            logger.warning("Enhancement failed: No job description provided")
            return jsonify({
                'error': 'Job description is required'
            }), 400
        
        # TODO: Implement actual JD enhancement logic
        # This is a placeholder response
        enhanced_jd = f"Enhanced JD (SFIA-Based):\n\n{job_description}\n\n--- SFIA COMPETENCIES ---\n\nRelevant Skills:\n- Software Development (Level 4)\n- System Design (Level 3)\n- Quality Assurance (Level 3)"
        
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
def upload_jd():
    """
    Endpoint to upload job description file
    """
    logger.info("POST /api/upload-jd - File upload request received")
    try:
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
        
        logger.info(f"Processing file: {file.filename}")
        
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
