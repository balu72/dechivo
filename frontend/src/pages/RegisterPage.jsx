import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import '../styles/RegisterPage.css';

const RegisterPage = () => {
    const navigate = useNavigate();
    const { register } = useAuth();
    const [formData, setFormData] = useState({
        email: '',
        username: '',
        password: '',
        confirmPassword: '',
        full_name: '',
        organization: '',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
        setError(''); // Clear error when user types
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        // Validation
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (formData.password.length < 6) {
            setError('Password must be at least 6 characters');
            return;
        }

        setLoading(true);

        try {
            const { confirmPassword, ...registerData } = formData;
            const result = await register(registerData);

            if (result.success) {
                navigate('/enhance');
            } else {
                setError(result.error || 'Registration failed. Please try again.');
            }
        } catch (err) {
            setError('An unexpected error occurred. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="register-container">
            <div className="register-background">
                <div className="gradient-orb orb-1"></div>
                <div className="gradient-orb orb-2"></div>
                <div className="gradient-orb orb-3"></div>
            </div>

            <div className="register-card">
                <div className="register-header">
                    <h1 className="register-title">Create Account</h1>
                    <p className="register-subtitle">Join Dechivo and start enhancing your job descriptions</p>
                </div>

                {error && (
                    <div className="error-message">
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                            <path d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM11 15H9V13H11V15ZM11 11H9V5H11V11Z" fill="currentColor" />
                        </svg>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="register-form">
                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="email">Email *</label>
                            <div className="input-wrapper">
                                <svg className="input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                                    <path d="M18 4H2C0.9 4 0.01 4.9 0.01 6L0 14C0 15.1 0.9 16 2 16H18C19.1 16 20 15.1 20 14V6C20 4.9 19.1 4 18 4ZM18 8L10 12L2 8V6L10 10L18 6V8Z" fill="currentColor" />
                                </svg>
                                <input
                                    type="email"
                                    id="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    required
                                    placeholder="you@example.com"
                                    disabled={loading}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label htmlFor="username">Username *</label>
                            <div className="input-wrapper">
                                <svg className="input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                                    <path d="M10 10C12.21 10 14 8.21 14 6C14 3.79 12.21 2 10 2C7.79 2 6 3.79 6 6C6 8.21 7.79 10 10 10ZM10 12C7.33 12 2 13.34 2 16V18H18V16C18 13.34 12.67 12 10 12Z" fill="currentColor" />
                                </svg>
                                <input
                                    type="text"
                                    id="username"
                                    name="username"
                                    value={formData.username}
                                    onChange={handleChange}
                                    required
                                    placeholder="johndoe"
                                    disabled={loading}
                                />
                            </div>
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="full_name">Full Name</label>
                        <div className="input-wrapper">
                            <svg className="input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                                <path d="M9 11H7V13H9V11ZM13 11H11V13H13V11ZM17 6H3C1.9 6 1 6.9 1 8V16C1 17.1 1.9 18 3 18H17C18.1 18 19 17.1 19 16V8C19 6.9 18.1 6 17 6ZM17 16H3V8H17V16Z" fill="currentColor" />
                            </svg>
                            <input
                                type="text"
                                id="full_name"
                                name="full_name"
                                value={formData.full_name}
                                onChange={handleChange}
                                placeholder="John Doe"
                                disabled={loading}
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label htmlFor="organization">Organization</label>
                        <div className="input-wrapper">
                            <svg className="input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                                <path d="M4 5V18H11V13H16V5H4ZM6 16V14H8V16H6ZM6 13V11H8V13H6ZM6 10V8H8V10H6ZM10 16V14H12V16H10ZM10 13V11H12V13H10ZM10 10V8H12V10H10ZM14 11V9H16V11H14Z" fill="currentColor" />
                            </svg>
                            <input
                                type="text"
                                id="organization"
                                name="organization"
                                value={formData.organization}
                                onChange={handleChange}
                                placeholder="Your Company"
                                disabled={loading}
                            />
                        </div>
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label htmlFor="password">Password *</label>
                            <div className="input-wrapper">
                                <svg className="input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                                    <path d="M15 7H14V5C14 2.79 12.21 1 10 1C7.79 1 6 2.79 6 5V7H5C3.9 7 3 7.9 3 9V18C3 19.1 3.9 20 5 20H15C16.1 20 17 19.1 17 18V9C17 7.9 16.1 7 15 7ZM10 15C8.9 15 8 14.1 8 13C8 11.9 8.9 11 10 11C11.1 11 12 11.9 12 13C12 14.1 11.1 15 10 15ZM8 7V5C8 3.9 8.9 3 10 3C11.1 3 12 3.9 12 5V7H8Z" fill="currentColor" />
                                </svg>
                                <input
                                    type="password"
                                    id="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    required
                                    placeholder="••••••••"
                                    disabled={loading}
                                    minLength="6"
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label htmlFor="confirmPassword">Confirm Password *</label>
                            <div className="input-wrapper">
                                <svg className="input-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                                    <path d="M15 7H14V5C14 2.79 12.21 1 10 1C7.79 1 6 2.79 6 5V7H5C3.9 7 3 7.9 3 9V18C3 19.1 3.9 20 5 20H15C16.1 20 17 19.1 17 18V9C17 7.9 16.1 7 15 7ZM10 15C8.9 15 8 14.1 8 13C8 11.9 8.9 11 10 11C11.1 11 12 11.9 12 13C12 14.1 11.1 15 10 15ZM8 7V5C8 3.9 8.9 3 10 3C11.1 3 12 3.9 12 5V7H8Z" fill="currentColor" />
                                </svg>
                                <input
                                    type="password"
                                    id="confirmPassword"
                                    name="confirmPassword"
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                    required
                                    placeholder="••••••••"
                                    disabled={loading}
                                    minLength="6"
                                />
                            </div>
                        </div>
                    </div>

                    <button type="submit" className="register-button" disabled={loading}>
                        {loading ? (
                            <>
                                <span className="spinner"></span>
                                Creating Account...
                            </>
                        ) : (
                            'Create Account'
                        )}
                    </button>
                </form>

                <div className="register-footer">
                    <p>Already have an account? <Link to="/login">Sign in</Link></p>
                </div>

                <div className="back-home">
                    <Link to="/">← Back to Home</Link>
                </div>
            </div>
        </div>
    );
};

export default RegisterPage;
