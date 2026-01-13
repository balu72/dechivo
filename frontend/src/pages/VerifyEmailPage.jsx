import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import './VerifyEmailPage.css';

const API_BASE_URL = '';

const VerifyEmailPage = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [status, setStatus] = useState('verifying'); // verifying, success, error, expired
    const [message, setMessage] = useState('Verifying your email...');

    useEffect(() => {
        const token = searchParams.get('token');

        if (!token) {
            setStatus('error');
            setMessage('Invalid verification link. No token provided.');
            return;
        }

        verifyEmail(token);
    }, [searchParams]);

    const verifyEmail = async (token) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/auth/verify-email`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ token })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                setStatus('success');
                setMessage(data.message || 'Email verified successfully!');

                // Redirect to login after 3 seconds
                setTimeout(() => {
                    navigate('/login', {
                        state: { message: 'Email verified! Please log in.' }
                    });
                }, 3000);
            } else {
                if (data.expired) {
                    setStatus('expired');
                    setMessage('This verification link has expired.');
                } else {
                    setStatus('error');
                    setMessage(data.error || 'Verification failed.');
                }
            }
        } catch (error) {
            console.error('Verification error:', error);
            setStatus('error');
            setMessage('An error occurred during verification. Please try again.');
        }
    };

    const getIcon = () => {
        switch (status) {
            case 'verifying':
                return (
                    <div className="verify-spinner">
                        <div className="spinner"></div>
                    </div>
                );
            case 'success':
                return (
                    <div className="verify-icon success">
                        <svg viewBox="0 0 24 24" fill="none" width="48" height="48">
                            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                                stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </div>
                );
            case 'error':
            case 'expired':
                return (
                    <div className="verify-icon error">
                        <svg viewBox="0 0 24 24" fill="none" width="48" height="48">
                            <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                                stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </div>
                );
            default:
                return null;
        }
    };

    return (
        <div className="verify-page">
            <div className="verify-container">
                <div className="verify-card">
                    {getIcon()}

                    <h1 className="verify-title">
                        {status === 'verifying' && 'Verifying Email'}
                        {status === 'success' && 'Email Verified!'}
                        {status === 'error' && 'Verification Failed'}
                        {status === 'expired' && 'Link Expired'}
                    </h1>

                    <p className="verify-message">{message}</p>

                    {status === 'success' && (
                        <p className="verify-redirect">
                            Redirecting to login page...
                        </p>
                    )}

                    {(status === 'error' || status === 'expired') && (
                        <div className="verify-actions">
                            <Link to="/login" className="btn btn-primary">
                                Go to Login
                            </Link>
                            {status === 'expired' && (
                                <p className="resend-hint">
                                    You can request a new verification email from the login page.
                                </p>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default VerifyEmailPage;
