from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from models import User, db
import logging

logger = logging.getLogger(__name__)

def token_required(fn):
    """Decorator to protect routes that require authentication"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return jsonify({'error': 'Invalid or expired token'}), 401
    return wrapper

def admin_required(fn):
    """Decorator to protect routes that require admin privileges"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or user.role != 'admin':
                return jsonify({'error': 'Admin privileges required'}), 403
            
            return fn(*args, **kwargs)
        except Exception as e:
            logger.error(f"Admin verification failed: {str(e)}")
            return jsonify({'error': 'Authentication failed'}), 401
    return wrapper

def get_current_user():
    """Get current authenticated user"""
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        return User.query.get(current_user_id)
    except Exception as e:
        logger.error(f"Failed to get current user: {str(e)}")
        return None
