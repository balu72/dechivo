import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import '../styles/ResultsPage.css';
import '../styles/LandingPage.css';
import {
    trackEnhancementCompleted,
    trackDownload
} from '../analytics';

const ResultsPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { user, logout } = useAuth();
    const [enhancedJD, setEnhancedJD] = useState('');
    const [statusMessage, setStatusMessage] = useState(null);
    const [showUserMenu, setShowUserMenu] = useState(false);
    const [resultData, setResultData] = useState(null);

    useEffect(() => {
        if (location.state?.enhancedJD) {
            setEnhancedJD(location.state.enhancedJD);
            setResultData({
                originalJD: location.state.originalJD,
                skillsCount: location.state.skillsCount,
                skills: location.state.skills,
                extractedKeywords: location.state.extractedKeywords,
                kgConnected: location.state.kgConnected,
                processingTime: location.state.processingTime,
                orgContext: location.state.orgContext
            });

            // Track enhancement completed
            const duration = location.state.processingTime / 1000;
            const filledCount = Object.values(location.state.orgContext || {}).filter(v => v && v.trim()).length;
            trackEnhancementCompleted(location.state.skillsCount || 0, duration, filledCount);
        } else {
            // No data, redirect back to enhance page
            navigate('/enhance');
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
        navigate('/enhance');
    };

    const handleCopyToClipboard = () => {
        navigator.clipboard.writeText(enhancedJD);
        setStatusMessage({ type: 'success', text: 'Copied to clipboard!' });
        setTimeout(() => setStatusMessage(null), 2000);
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
                            <li><Link to="/" className="nav-link">Home</Link></li>
                            <li><Link to="/enhance" className="nav-link">Enhance</Link></li>
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

                {/* Success Banner */}
                <div className="success-banner">
                    <div className="success-icon">
                        <svg viewBox="0 0 24 24" fill="none" width="32" height="32">
                            <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </div>
                    <div className="success-content">
                        <h2>Job Description Enhanced Successfully!</h2>
                        <p>
                            <span className="stat">{resultData.skillsCount} SFIA skills</span> identified in
                            <span className="stat"> {(resultData.processingTime / 1000).toFixed(1)}s</span>
                            {resultData.kgConnected && <span className="kg-badge">Knowledge Graph Connected</span>}
                        </p>
                    </div>
                </div>

                {/* Results Container */}
                <div className="results-container">
                    {/* Action Buttons */}
                    <div className="results-actions">
                        <button
                            className="btn btn-primary btn-icon"
                            onClick={() => handleDownload('txt')}
                        >
                            <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
                                <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15M7 10L12 15M12 15L17 10M12 15V3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                            Download
                        </button>
                        <button
                            className="btn btn-secondary btn-icon"
                            onClick={handleCopyToClipboard}
                        >
                            <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
                                <path d="M8 4V16C8 17.1046 8.89543 18 10 18H18C19.1046 18 20 17.1046 20 16V7.24162C20 6.7034 19.7893 6.18789 19.4142 5.81282L16.1716 2.57121C15.7965 2.19614 15.281 1.98547 14.7428 1.98547H10C8.89543 2 8 2.89543 8 4Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                <path d="M16 18V20C16 21.1046 15.1046 22 14 22H6C4.89543 22 4 21.1046 4 20V8C4 6.89543 4.89543 6 6 6H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                            Copy
                        </button>
                        <button
                            className="btn btn-secondary btn-icon"
                            onClick={() => {/* Publish functionality */ }}
                        >
                            <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
                                <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                            Publish
                        </button>
                        <button
                            className="btn btn-ghost btn-icon"
                            onClick={handleEnhanceAnother}
                        >
                            <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
                                <path d="M12 4V20M4 12H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                            Enhance Another
                        </button>
                    </div>

                    {/* Enhanced JD Display */}
                    <div className="enhanced-jd-section">
                        <label className="section-label">
                            <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
                                <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                            Enhanced Job Description
                        </label>
                        <textarea
                            className="enhanced-jd-textarea"
                            value={enhancedJD}
                            onChange={(e) => setEnhancedJD(e.target.value)}
                            rows="20"
                        />
                        <div className="char-count">
                            {enhancedJD.length} characters
                        </div>
                    </div>

                    {/* Skills Summary */}
                    {resultData.skills && resultData.skills.length > 0 && (
                        <div className="skills-summary">
                            <h3>SFIA Skills Identified</h3>
                            <div className="skills-grid">
                                {resultData.skills.map((skill, index) => (
                                    <div key={index} className="skill-card">
                                        <div className="skill-code">{skill.code}</div>
                                        <div className="skill-name">{skill.name}</div>
                                        <div className="skill-level">Level {skill.level}</div>
                                    </div>
                                ))}
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

export default ResultsPage;
