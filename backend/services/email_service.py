"""
Email Service using Brevo (formerly Sendinblue)
Handles email verification and other transactional emails
"""

import os
import logging
import requests

logger = logging.getLogger(__name__)

# Brevo API configuration
BREVO_API_KEY = os.getenv('BREVO_API_KEY', '')
BREVO_SENDER_EMAIL = os.getenv('BREVO_SENDER_EMAIL', 'noreply@dechivo.com')
BREVO_SENDER_NAME = os.getenv('BREVO_SENDER_NAME', 'Dechivo')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

BREVO_API_URL = 'https://api.brevo.com/v3/smtp/email'


def send_verification_email(email: str, token: str, name: str = None) -> bool:
    """
    Send email verification link to user.
    
    Args:
        email: User's email address
        token: Verification token
        name: User's name (optional)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    if not BREVO_API_KEY:
        logger.warning("BREVO_API_KEY not configured, skipping email send")
        return False
    
    verification_link = f"{FRONTEND_URL}/verify-email?token={token}"
    
    # Email content
    subject = "Verify your Dechivo account"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
            .button {{ display: inline-block; background: #667eea; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 20px 0; }}
            .button:hover {{ background: #5a67d8; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to Dechivo!</h1>
            </div>
            <div class="content">
                <p>Hi{' ' + name if name else ''},</p>
                <p>Thank you for signing up for Dechivo. Please verify your email address by clicking the button below:</p>
                <p style="text-align: center;">
                    <a href="{verification_link}" class="button">Verify Email Address</a>
                </p>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #667eea;">{verification_link}</p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't create an account with Dechivo, you can safely ignore this email.</p>
            </div>
            <div class="footer">
                <p>© 2024 Dechivo. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Welcome to Dechivo!
    
    Hi{' ' + name if name else ''},
    
    Thank you for signing up for Dechivo. Please verify your email address by clicking the link below:
    
    {verification_link}
    
    This link will expire in 24 hours.
    
    If you didn't create an account with Dechivo, you can safely ignore this email.
    
    © 2024 Dechivo. All rights reserved.
    """
    
    # Prepare API request
    headers = {
        'accept': 'application/json',
        'api-key': BREVO_API_KEY,
        'content-type': 'application/json'
    }
    
    payload = {
        'sender': {
            'name': BREVO_SENDER_NAME,
            'email': BREVO_SENDER_EMAIL
        },
        'to': [
            {
                'email': email,
                'name': name or email
            }
        ],
        'subject': subject,
        'htmlContent': html_content,
        'textContent': text_content
    }
    
    try:
        response = requests.post(BREVO_API_URL, json=payload, headers=headers)
        
        if response.status_code in [200, 201]:
            logger.info(f"Verification email sent successfully to {email}")
            return True
        else:
            logger.error(f"Failed to send verification email: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending verification email: {str(e)}")
        return False


def send_password_reset_email(email: str, token: str, name: str = None) -> bool:
    """
    Send password reset link to user.
    
    Args:
        email: User's email address
        token: Password reset token
        name: User's name (optional)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    if not BREVO_API_KEY:
        logger.warning("BREVO_API_KEY not configured, skipping email send")
        return False
    
    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"
    
    subject = "Reset your Dechivo password"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
            .button {{ display: inline-block; background: #667eea; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Password Reset</h1>
            </div>
            <div class="content">
                <p>Hi{' ' + name if name else ''},</p>
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                <p style="text-align: center;">
                    <a href="{reset_link}" class="button">Reset Password</a>
                </p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request a password reset, you can safely ignore this email.</p>
            </div>
            <div class="footer">
                <p>© 2024 Dechivo. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    headers = {
        'accept': 'application/json',
        'api-key': BREVO_API_KEY,
        'content-type': 'application/json'
    }
    
    payload = {
        'sender': {'name': BREVO_SENDER_NAME, 'email': BREVO_SENDER_EMAIL},
        'to': [{'email': email, 'name': name or email}],
        'subject': subject,
        'htmlContent': html_content
    }
    
    try:
        response = requests.post(BREVO_API_URL, json=payload, headers=headers)
        
        if response.status_code in [200, 201]:
            logger.info(f"Password reset email sent successfully to {email}")
            return True
        else:
            logger.error(f"Failed to send password reset email: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending password reset email: {str(e)}")
        return False
