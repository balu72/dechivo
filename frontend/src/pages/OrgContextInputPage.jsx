import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import '../styles/OrgContextInputPage.css';
import '../styles/LandingPage.css';

const OrgContextInputPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { user, logout, authenticatedFetch } = useAuth();
    const API_BASE_URL = '';

    const [statusMessage, setStatusMessage] = useState(null);
    const [showUserMenu, setShowUserMenu] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);

    // Form state for interview context
    const [interviewContext, setInterviewContext] = useState({
        customer_mandates: '',
        org_discretion: '',
        previous_hiring_decisions: '',
        additional_notes: ''
    });

    // Data from EnhanceJDPage
    const [enhancedJD, setEnhancedJD] = useState('');
    const [roleTitle, setRoleTitle] = useState('');
    const [roleGrade, setRoleGrade] = useState('');

    useEffect(() => {
        if (location.state?.enhancedJD) {
            setEnhancedJD(location.state.enhancedJD);
            setRoleTitle(location.state.roleTitle || '');
            setRoleGrade(location.state.roleGrade || '');
        } else {
            // No JD provided, redirect back
            navigate('/enhance');
        }
    }, [location.state, navigate]);

    const handleInputChange = (field, value) => {
        setInterviewContext(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    const handleGenerateInterviewPlan = async () => {
        if (!enhancedJD) {
            setStatusMessage({ type: 'error', text: 'No job description available' });
            return;
        }

        setIsGenerating(true);
        setStatusMessage({ type: 'info', text: 'Generating comprehensive interview plan...' });

        try {
            const response = await authenticatedFetch(`${API_BASE_URL}/api/create-interview-plan`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    job_description: enhancedJD,
                    role_title: roleTitle,
                    role_grade: roleGrade,
                    interview_context: {
                        customer_mandates: interviewContext.customer_mandates || '',
                        org_discretion: interviewContext.org_discretion || '',
                        previous_hiring_decisions: interviewContext.previous_hiring_decisions || '',
                        additional_notes: interviewContext.additional_notes || ''
                    }
                }),
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Navigate to InterviewPlanDisplayPage with the generated plan
                navigate('/interview-plan', {
                    state: {
                        interviewPlan: data.interview_plan,
                        seniorityLevel: data.seniority_level,
                        roleTitle: roleTitle,
                        enhancedJD: enhancedJD,
                        interviewContext: interviewContext
                    }
                });
            } else {
                setStatusMessage({
                    type: 'error',
                    text: data.error || 'Failed to generate interview plan'
                });
            }
        } catch (error) {
            console.error('Interview plan error:', error);
            setStatusMessage({
                type: 'error',
                text: 'Network error. Please try again.'
            });
        } finally {
            setIsGenerating(false);
            setTimeout(() => setStatusMessage(null), 5000);
        }
    };

    const handleBack = () => {
        navigate(-1); // Go back in browser history
    };

    return (
        <div className="org-context-input-page">
            {/* Header */}
            <header className="header">
                <div className="header-container">
                    <Link to="/" className="logo">
                        Dechivo<span className="beta-tag">beta</span>
                    </Link>
                    <nav className="nav">
                        {user && (
                            <div className="user-menu-container">
                                <button
                                    className="user-menu-button"
                                    onClick={() => setShowUserMenu(!showUserMenu)}
                                >
                                    <span>{user.username}</span>
                                    <svg viewBox="0 0 24 24" fill="none" width="16" height="16">
                                        <path d="M19 9L12 16L5 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                </button>
                                {showUserMenu && (
                                    <div className="user-dropdown">
                                        <div className="user-info">
                                            <div className="user-avatar">
                                                {user.username.charAt(0).toUpperCase()}
                                            </div>
                                            <div className="user-details">
                                                <span className="user-name">{user.full_name || user.username}</span>
                                                <span className="user-email">{user.email}</span>
                                            </div>
                                        </div>
                                        <div className="dropdown-divider"></div>
                                        <button className="dropdown-item logout" onClick={handleLogout}>
                                            <svg viewBox="0 0 24 24" fill="none" width="16" height="16">
                                                <path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9M16 17L21 12M21 12L16 7M21 12H9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                            </svg>
                                            Sign Out
                                        </button>
                                    </div>
                                )}
                            </div>
                        )}
                    </nav>
                </div>
            </header>

            {/* Main Content */}
            <main className="main-content">
                <div className="context-form-container">
                    {/* Back Link - Top Left */}
                    <a className="back-link" onClick={handleBack}>
                        ← Back
                    </a>

                    {/* Status Message */}
                    {statusMessage && (
                        <div className={`status-message ${statusMessage.type}`}>
                            {statusMessage.text}
                        </div>
                    )}

                    <div className="context-card">
                        <div className="card-header">
                            <svg viewBox="0 0 24 24" fill="none" width="24" height="24">
                                <path d="M8 7H16M8 11H16M8 15H13M17 21L12 18L7 21V5C7 3.89543 7.89543 3 9 3H15C16.1046 3 17 3.89543 17 5V21Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                            <h2>Additional Contexts (Optional)</h2>
                        </div>

                        <form className="context-form" onSubmit={(e) => { e.preventDefault(); handleGenerateInterviewPlan(); }}>
                            <div className="form-field">
                                <label htmlFor="customer_mandates">Any mandates from customer/org</label>
                                <input
                                    type="text"
                                    id="customer_mandates"
                                    placeholder="e.g., Must include diversity hiring assessment, security clearance requirements..."
                                    value={interviewContext.customer_mandates}
                                    onChange={(e) => handleInputChange('customer_mandates', e.target.value)}
                                />
                            </div>

                            <div className="form-field">
                                <label htmlFor="org_discretion">Any specific discretion with the org/customer</label>
                                <input
                                    type="text"
                                    id="org_discretion"
                                    placeholder="e.g., Prefer candidates with startup experience, open to remote candidates..."
                                    value={interviewContext.org_discretion}
                                    onChange={(e) => handleInputChange('org_discretion', e.target.value)}
                                />
                            </div>

                            <div className="form-field">
                                <label htmlFor="previous_hiring_decisions">Any decision taken from previous hiring</label>
                                <input
                                    type="text"
                                    id="previous_hiring_decisions"
                                    placeholder="e.g., Add system design round, reduce coding rounds to 2..."
                                    value={interviewContext.previous_hiring_decisions}
                                    onChange={(e) => handleInputChange('previous_hiring_decisions', e.target.value)}
                                />
                            </div>

                            <div className="form-field">
                                <label htmlFor="additional_notes">Additional Notes</label>
                                <textarea
                                    id="additional_notes"
                                    placeholder="Any other context that would help create a better interview plan..."
                                    value={interviewContext.additional_notes}
                                    onChange={(e) => handleInputChange('additional_notes', e.target.value)}
                                    rows="3"
                                />
                            </div>

                            <div className="form-actions">
                                <button
                                    type="submit"
                                    className="btn btn-primary"
                                    disabled={isGenerating}
                                >
                                    {isGenerating ? (
                                        <>
                                            <span className="spinner"></span>
                                            Generating...
                                        </>
                                    ) : (
                                        <>
                                            Generate Interview Plan
                                            <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
                                                <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                            </svg>
                                        </>
                                    )}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </main>

            {/* Footer */}
            <footer className="footer">
                <div className="footer-container">
                    <p className="footer-text">© 2024 All rights reserved.</p>
                </div>
            </footer>
        </div>
    );
};

export default OrgContextInputPage;
