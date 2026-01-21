import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import '../styles/InterviewPlanDisplayPage.css';
import '../styles/LandingPage.css';

const InterviewPlanDisplayPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { user, logout } = useAuth();

    const [statusMessage, setStatusMessage] = useState(null);
    const [showUserMenu, setShowUserMenu] = useState(false);
    // Workflow states: 'view' (initial), 'editing', 'published'
    const [workflowState, setWorkflowState] = useState('view');

    // Data from OrgContextInputPage
    const [interviewPlan, setInterviewPlan] = useState('');
    const [seniorityLevel, setSeniorityLevel] = useState('');
    const [roleTitle, setRoleTitle] = useState('');
    const [enhancedJD, setEnhancedJD] = useState('');

    useEffect(() => {
        if (location.state?.interviewPlan) {
            setInterviewPlan(location.state.interviewPlan);
            setSeniorityLevel(location.state.seniorityLevel || 'individual_contributor');
            setRoleTitle(location.state.roleTitle || '');
            setEnhancedJD(location.state.enhancedJD || '');
        } else {
            // No interview plan provided, redirect back
            navigate('/enhance');
        }
    }, [location.state, navigate]);

    // Helper to format interview plan: remove markdown and style headings
    const formatInterviewPlan = (text) => {
        if (!text) return null;

        // Split into lines
        const lines = text.split('\n');
        const elements = [];
        let currentParagraph = [];

        const flushParagraph = () => {
            if (currentParagraph.length > 0) {
                elements.push(
                    <p key={`p-${elements.length}`} style={{ margin: '0.5rem 0', lineHeight: '1.6' }}>
                        {currentParagraph.join(' ')}
                    </p>
                );
                currentParagraph = [];
            }
        };

        lines.forEach((line, index) => {
            const trimmed = line.trim();

            // Skip empty lines but flush paragraph
            if (!trimmed) {
                flushParagraph();
                return;
            }

            // Any markdown heading (####, ###, ##, #) - strip the # characters
            if (/^#{1,6}\s/.test(trimmed)) {
                flushParagraph();
                const headingText = trimmed.replace(/^#+\s*/, '');
                const hashCount = trimmed.match(/^#+/)[0].length;

                // Style based on heading level - questions/subsections smaller
                const styles = {
                    1: { fontSize: '1.5rem', fontWeight: '700', color: '#1F2937', marginTop: '1.5rem', marginBottom: '0.75rem', borderBottom: '2px solid #3B82F6', paddingBottom: '0.5rem' },
                    2: { fontSize: '0.95rem', fontWeight: '600', color: '#374151', marginTop: '0.75rem', marginBottom: '0.35rem' },
                    3: { fontSize: '0.9rem', fontWeight: '600', color: '#4B5563', marginTop: '0.5rem', marginBottom: '0.25rem' },
                    4: { fontSize: '0.875rem', fontWeight: '500', color: '#4B5563', marginTop: '0.5rem', marginBottom: '0.25rem' },
                    5: { fontSize: '0.85rem', fontWeight: '500', color: '#6B7280', marginTop: '0.35rem', marginBottom: '0.2rem' },
                    6: { fontSize: '0.825rem', fontWeight: '500', color: '#6B7280', marginTop: '0.35rem', marginBottom: '0.2rem' }
                };

                const style = styles[Math.min(hashCount, 6)] || styles[4];
                const Tag = hashCount <= 2 ? 'h2' : hashCount <= 4 ? 'h3' : 'h4';

                elements.push(
                    <Tag key={`h-${index}`} style={style}>
                        {headingText}
                    </Tag>
                );
                return;
            }

            // Numbered items (e.g., "1. Role Context" or "1. Solve a coding challenge...")
            if (/^\d+\.\s+[A-Z]/.test(trimmed)) {
                flushParagraph();

                // Section titles are typically SHORT (< 50 chars), don't have parentheses, 
                // don't end with period or question mark
                const isSectionTitle = trimmed.length < 50 && !trimmed.includes('(') && !trimmed.endsWith('.') && !trimmed.endsWith('?');

                if (isSectionTitle) {
                    // Section title - larger, prominent
                    elements.push(
                        <h2 key={`num-${index}`} style={{
                            fontSize: '1.35rem',
                            fontWeight: '700',
                            color: '#1F2937',
                            marginTop: '1.75rem',
                            marginBottom: '0.75rem'
                        }}>
                            {trimmed}
                        </h2>
                    );
                } else {
                    // Numbered instruction/exercise/question - smaller font
                    elements.push(
                        <p key={`numitem-${index}`} style={{
                            fontSize: '0.9rem',
                            fontWeight: '500',
                            color: '#374151',
                            marginTop: '0.5rem',
                            marginBottom: '0.25rem',
                            paddingLeft: '0.5rem'
                        }}>
                            {trimmed}
                        </p>
                    );
                }
                return;
            }

            // Bullet points: - or * or •
            if (/^[-*•]\s/.test(trimmed)) {
                flushParagraph();
                const bulletText = trimmed.replace(/^[-*•]\s*/, '').replace(/\*\*/g, '');
                elements.push(
                    <div key={`bullet-${index}`} style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '0.5rem',
                        marginLeft: '1rem',
                        marginBottom: '0.25rem'
                    }}>
                        <span style={{ color: '#10B981', fontWeight: 'bold' }}>•</span>
                        <span>{bulletText}</span>
                    </div>
                );
                return;
            }

            // Bold text sections (e.g., **Purpose:**)
            if (trimmed.startsWith('**') && trimmed.includes(':**')) {
                flushParagraph();
                const cleanText = trimmed.replace(/\*\*/g, '');
                const [label, ...rest] = cleanText.split(':');
                elements.push(
                    <p key={`bold-${index}`} style={{ margin: '0.5rem 0' }}>
                        <strong style={{ color: '#1F2937' }}>{label}:</strong>
                        {rest.length > 0 ? ` ${rest.join(':')}` : ''}
                    </p>
                );
                return;
            }

            // Regular text - accumulate into paragraph
            const cleanLine = trimmed.replace(/\*\*/g, '').replace(/\*/g, '');
            currentParagraph.push(cleanLine);
        });

        // Flush remaining paragraph
        flushParagraph();

        return elements;
    };

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    const handleDownload = () => {
        const blob = new Blob([interviewPlan], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        const fileName = roleTitle ? `interview_plan_${roleTitle.replace(/\s+/g, '_')}.txt` : 'interview_plan.txt';
        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        setStatusMessage({ type: 'success', text: 'Interview plan downloaded!' });
        setTimeout(() => setStatusMessage(null), 3000);
    };

    const handleEdit = () => {
        setWorkflowState('editing');
    };

    const handlePublish = () => {
        setWorkflowState('published');
        setStatusMessage({ type: 'success', text: 'Interview plan published!' });
        setTimeout(() => setStatusMessage(null), 3000);
    };

    const handleBack = () => {
        navigate(-1); // Go back in browser history
    };

    const getSeniorityLabel = (level) => {
        const labels = {
            'individual_contributor': 'Individual Contributor',
            'team_lead': 'Team Lead',
            'manager': 'Manager',
            'senior_manager': 'Senior Manager',
            'director': 'Director'
        };
        return labels[level] || level;
    };

    return (
        <div className="interview-plan-display-page">
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
                <div className="plan-container">
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

                    <div className="plan-card">
                        <div className="card-header-row">
                            <div className="card-header">
                                <svg viewBox="0 0 24 24" fill="none" width="24" height="24">
                                    <path d="M8 7H16M8 11H16M8 15H13M17 21L12 18L7 21V5C7 3.89543 7.89543 3 9 3H15C16.1046 3 17 3.89543 17 5V21Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                </svg>
                                <h2>Interview Plan</h2>
                            </div>
                            <div className="header-actions">
                                <button
                                    className={`btn btn-icon ${workflowState === 'view' ? 'btn-primary' : 'btn-secondary'}`}
                                    onClick={handleEdit}
                                    disabled={workflowState !== 'view'}
                                >
                                    <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
                                        <path d="M11 4H7C5.89543 4 5 4.89543 5 6V18C5 19.1046 5.89543 20 7 20H17C18.1046 20 19 19.1046 19 18V14M17.5 2.5C18.3284 1.67157 19.6716 1.67157 20.5 2.5C21.3284 3.32843 21.3284 4.67157 20.5 5.5L11 15H8V12L17.5 2.5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    Edit
                                </button>
                                <button
                                    className={`btn btn-icon ${workflowState === 'editing' ? 'btn-primary' : 'btn-secondary'}`}
                                    onClick={handlePublish}
                                    disabled={workflowState !== 'editing'}
                                >
                                    <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
                                        <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    Publish
                                </button>
                                <button
                                    className={`btn btn-icon ${workflowState === 'published' ? 'btn-primary' : 'btn-secondary'}`}
                                    onClick={handleDownload}
                                    disabled={workflowState !== 'published'}
                                >
                                    <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
                                        <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15M7 10L12 15M12 15L17 10M12 15V3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    Download
                                </button>
                            </div>
                        </div>

                        <div className="plan-content">
                            {formatInterviewPlan(interviewPlan)}
                        </div>
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

export default InterviewPlanDisplayPage;
