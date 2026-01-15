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
    const { user, logout } = useAuth();
    const [enhancedJD, setEnhancedJD] = useState('');
    const [statusMessage, setStatusMessage] = useState(null);
    const [showUserMenu, setShowUserMenu] = useState(false);
    const [resultData, setResultData] = useState(null);
    // Workflow states: 'view' (initial), 'editing', 'published'
    const [workflowState, setWorkflowState] = useState('view');

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
