import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import '../styles/EnhanceJDPage.css';
import '../styles/LandingPage.css';
import {
    trackEnhancementCompleted,
    trackDownload
} from '../analytics';

const EnhanceJDPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { user, logout, authenticatedFetch } = useAuth();
    const API_BASE_URL = '';
    const [enhancedJD, setEnhancedJD] = useState('');
    const [statusMessage, setStatusMessage] = useState(null);
    const [showUserMenu, setShowUserMenu] = useState(false);
    const [resultData, setResultData] = useState(null);
    // Workflow states: 'view' (initial), 'editing', 'published'
    const [workflowState, setWorkflowState] = useState('view');
    const [interviewPlan, setInterviewPlan] = useState('');
    const [isGeneratingPlan, setIsGeneratingPlan] = useState(false);
    const [showInterviewPlan, setShowInterviewPlan] = useState(false);

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
                // Exercises/instructions/questions are longer or end with . or ?
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

    useEffect(() => {
        if (location.state?.enhancedJD) {
            setEnhancedJD(location.state.enhancedJD);
            setResultData({
                originalJD: location.state.originalJD || '',
                skillsCount: location.state.skillsCount || location.state.skills?.length || 0,
                skills: location.state.skills || [],
                extractedKeywords: location.state.extractedKeywords || [],
                kgConnected: location.state.kgConnected ?? true,
                processingTime: location.state.processingTime || 0,
                orgContext: location.state.orgContext || {}
            });

            // Track enhancement completed (only if we have processingTime)
            if (location.state.processingTime) {
                const duration = location.state.processingTime / 1000;
                const filledCount = Object.values(location.state.orgContext || {}).filter(v => v && v.trim()).length;
                trackEnhancementCompleted(location.state.skillsCount || 0, duration, filledCount);
            }
        } else {
            // No data, redirect back to create page
            navigate('/create');
        }
    }, [location.state, navigate]);

    const handleDownload = (format = 'txt') => {
        if (!enhancedJD.trim()) return;

        const blob = new Blob([enhancedJD], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `enhanced_job_description.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        setStatusMessage({ type: 'success', text: 'Enhanced JD downloaded successfully!' });
        trackDownload(format);
        setTimeout(() => setStatusMessage(null), 3000);
    };

    const handleEnhanceAnother = () => {
        navigate('/create');
    };

    const handleEdit = () => {
        setWorkflowState('editing');
    };

    const handlePublish = () => {
        setWorkflowState('published');
        setStatusMessage({ type: 'success', text: 'Job description published!' });
        setTimeout(() => setStatusMessage(null), 3000);
    };

    const handleInterviewPlan = async () => {
        if (!enhancedJD) return;

        setIsGeneratingPlan(true);
        setStatusMessage({ type: 'info', text: 'Generating comprehensive interview plan...' });

        try {
            const response = await authenticatedFetch(`${API_BASE_URL}/api/create-interview-plan`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    job_description: enhancedJD,
                    role_title: resultData?.orgContext?.role_title || '',
                    role_grade: resultData?.orgContext?.role_grade || ''
                }),
            });

            const data = await response.json();

            if (response.ok && data.success) {
                setInterviewPlan(data.interview_plan);
                setShowInterviewPlan(true);
                // Scroll to interview plan
                setTimeout(() => {
                    const el = document.getElementById('interview-plan-section');
                    if (el) el.scrollIntoView({ behavior: 'smooth' });
                }, 100);
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
            setIsGeneratingPlan(false);
            setTimeout(() => setStatusMessage(null), 3000);
        }
    };

    if (!resultData) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
            </div>
        );
    }

    return (
        <div className="results-page">
            {/* Header */}
            <header className="header">
                <div className="header-container">
                    <Link to="/" className="logo">Dechivo<span className="beta-tag">. beta</span></Link>
                    <nav className="nav">
                        <ul className="nav-links">
                            <li><a href="#about" className="nav-link">About</a></li>
                            <li><a href="#contact" className="nav-link">Contact</a></li>
                        </ul>
                    </nav>
                    {/* User Menu */}
                    <div className="user-menu-container">
                        <button
                            className="user-menu-button"
                            onClick={() => setShowUserMenu(!showUserMenu)}
                        >
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                <path d="M10 10C12.21 10 14 8.21 14 6C14 3.79 12.21 2 10 2C7.79 2 6 3.79 6 6C6 8.21 7.79 10 10 10ZM10 12C7.33 12 2 13.34 2 16V18H18V16C18 13.34 12.67 12 10 12Z" fill="currentColor" />
                            </svg>
                            <span>{user?.username || 'User'}</span>
                        </button>
                        {showUserMenu && (
                            <div className="user-dropdown">
                                <div className="user-info">
                                    <div className="user-avatar">
                                        {user?.username?.charAt(0).toUpperCase() || 'U'}
                                    </div>
                                    <div className="user-details">
                                        <div className="user-name">{user?.full_name || user?.username}</div>
                                        <div className="user-email">{user?.email}</div>
                                    </div>
                                </div>
                                <div className="dropdown-divider"></div>
                                <button
                                    className="dropdown-item logout-button"
                                    onClick={async () => {
                                        await logout();
                                        navigate('/login');
                                    }}
                                >
                                    Logout
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="results-main">
                {/* Status Message */}
                {statusMessage && (
                    <div className={`status-message ${statusMessage.type}`}>
                        {statusMessage.text}
                    </div>
                )}

                {/* Results Container */}
                <div className="results-container">
                    {/* Enhanced JD Display */}
                    <div className="enhanced-jd-section">
                        <div className="section-header-row">
                            <label className="section-label">
                                <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
                                    <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                </svg>
                                New Job Description
                            </label>
                            <div className="results-actions">
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
                                    onClick={() => handleDownload('txt')}
                                    disabled={workflowState !== 'published'}
                                >
                                    <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
                                        <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15M7 10L12 15M12 15L17 10M12 15V3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    Download
                                </button>
                                <button
                                    className={`btn btn-secondary btn-icon ${isGeneratingPlan ? 'loading' : ''}`}
                                    onClick={handleInterviewPlan}
                                    disabled={isGeneratingPlan}
                                >
                                    <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
                                        <path d="M8 7H16M8 11H16M8 15H13M17 21L12 18L7 21V5C7 3.89543 7.89543 3 9 3H15C16.1046 3 17 3.89543 17 5V21Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    {isGeneratingPlan ? 'Generating...' : 'Interview Plan'}
                                </button>
                                <button
                                    className="btn btn-ghost btn-icon"
                                    onClick={handleEnhanceAnother}
                                >
                                    <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
                                        <path d="M12 4V20M4 12H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    Create Another
                                </button>
                            </div>
                        </div>
                        <textarea
                            className={`enhanced-jd-textarea ${workflowState === 'editing' ? 'editing' : ''}`}
                            value={enhancedJD}
                            onChange={(e) => setEnhancedJD(e.target.value)}
                            rows="20"
                            readOnly={workflowState !== 'editing'}
                        />
                        <div className="char-count">
                            {enhancedJD.length} characters
                        </div>
                    </div>

                    {/* Interview Plan Section */}
                    {showInterviewPlan && (
                        <div id="interview-plan-section" className="enhanced-jd-section" style={{ marginTop: '2rem', borderTop: '1px solid #E5E7EB', paddingTop: '2rem' }}>
                            <div className="section-header-row">
                                <label className="section-label">
                                    <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
                                        <path d="M8 7H16M8 11H16M8 15H13M17 21L12 18L7 21V5C7 3.89543 7.89543 3 9 3H15C16.1046 3 17 3.89543 17 5V21Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    Technical Interview Plan
                                </label>
                                <div className="results-actions">
                                    <button
                                        className="btn btn-secondary btn-icon"
                                        onClick={() => {
                                            const blob = new Blob([interviewPlan], { type: 'text/plain' });
                                            const url = URL.createObjectURL(blob);
                                            const link = document.createElement('a');
                                            link.href = url;
                                            link.download = `interview_plan.txt`;
                                            document.body.appendChild(link);
                                            link.click();
                                            document.body.removeChild(link);
                                            URL.revokeObjectURL(url);
                                            setStatusMessage({ type: 'success', text: 'Interview plan downloaded!' });
                                            setTimeout(() => setStatusMessage(null), 3000);
                                        }}
                                    >
                                        <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
                                            <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15M7 10L12 15M12 15L17 10M12 15V3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                        </svg>
                                        Download Plan
                                    </button>
                                </div>
                            </div>
                            <div
                                className="interview-plan-content"
                                style={{
                                    padding: '1.5rem',
                                    border: '2px solid #E5E7EB',
                                    borderRadius: '0.75rem',
                                    backgroundColor: '#F9FAFB',
                                    maxHeight: '600px',
                                    overflowY: 'auto',
                                    fontSize: '0.9375rem',
                                    color: '#374151'
                                }}
                            >
                                {formatInterviewPlan(interviewPlan)}
                            </div>
                        </div>
                    )}

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

export default EnhanceJDPage;
