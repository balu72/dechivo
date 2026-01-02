import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import mammoth from 'mammoth';
import * as pdfjsLib from 'pdfjs-dist';
import './EnhancementPage.css';
import './LandingPage.css'; // Reuse header and footer styles

// Configure PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.mjs`;

const API_BASE_URL = '';  // Use relative URL for both dev and production

const EnhancementPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { user, logout, authenticatedFetch } = useAuth();
    const [originalJD, setOriginalJD] = useState('');
    const [enhancedJD, setEnhancedJD] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [statusMessage, setStatusMessage] = useState(null);
    const [backendMessage, setBackendMessage] = useState('Ready to enhance job descriptions...');
    const [showUserMenu, setShowUserMenu] = useState(false);
    const [showOrgContext, setShowOrgContext] = useState(false);

    // Organizational context state
    const [orgContext, setOrgContext] = useState({
        org_industry: '',
        company_name: '',
        company_description: '',
        company_culture: '',
        company_values: '',
        business_context: '',
        role_context: '',
        role_type: '',
        role_grade: '',
        location: '',
        work_environment: '',
        reporting_to: ''
    });

    const handleOrgContextChange = (field, value) => {
        setOrgContext(prev => ({ ...prev, [field]: value }));
    };

    const getFilledContextCount = () => {
        return Object.values(orgContext).filter(v => v.trim()).length;
    };

    // Load file content when passed from landing page (no auto-enhance)
    useEffect(() => {
        if (location.state?.fileContent) {
            const { fileContent, fileName } = location.state;
            setEnhancedJD(fileContent);
            setBackendMessage(`Loaded: ${fileName} - Fill in organizational context and click Enhance`);
            // Expand org context section to prompt user to fill it
            setShowOrgContext(true);
            setStatusMessage({ type: 'info', text: 'Fill in organizational context below, then click Enhance' });
            setTimeout(() => setStatusMessage(null), 5000);
        }
    }, [location.state]);

    const enhanceWithBackend = async (content, fileName = 'uploaded file') => {
        setIsLoading(true);
        setBackendMessage('Processing...');

        try {
            const response = await authenticatedFetch(`${API_BASE_URL}/api/enhance-jd`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    job_description: content,
                    org_context: orgContext
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                setEnhancedJD(data.enhanced_jd);
                setBackendMessage(data.message || 'Enhancement completed');
            } else {
                throw new Error(data.error || 'Failed to enhance job description');
            }
        } catch (error) {
            console.error('Error enhancing JD:', error);
            const errorMessage = error.message || 'Failed to connect to backend';
            setStatusMessage({ type: 'error', text: errorMessage });
            setBackendMessage(`Error: ${errorMessage}`);

            // If session expired, redirect to login
            if (errorMessage.includes('Session expired') || errorMessage.includes('Not authenticated')) {
                setTimeout(() => {
                    logout();
                    navigate('/login');
                }, 2000);
            }
            setTimeout(() => setStatusMessage(null), 3000);
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileChange = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const fileExtension = file.name.split('.').pop().toLowerCase();
        setIsLoading(true);
        setStatusMessage({ type: 'info', text: `Loading ${file.name}...` });
        setBackendMessage(`Reading file: ${file.name}`);

        try {
            let textContent = '';

            if (fileExtension === 'txt') {
                // Handle text files
                textContent = await new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = (e) => resolve(e.target.result);
                    reader.onerror = reject;
                    reader.readAsText(file);
                });
            } else if (fileExtension === 'pdf') {
                // Handle PDF files
                const arrayBuffer = await file.arrayBuffer();
                const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
                const textPromises = [];

                for (let i = 1; i <= pdf.numPages; i++) {
                    const page = await pdf.getPage(i);
                    const content = await page.getTextContent();
                    const text = content.items.map(item => item.str).join(' ');
                    textPromises.push(text);
                }

                textContent = textPromises.join('\n\n');
            } else if (fileExtension === 'docx' || fileExtension === 'doc') {
                // Handle DOCX/DOC files
                const arrayBuffer = await file.arrayBuffer();
                const result = await mammoth.extractRawText({ arrayBuffer });
                textContent = result.value;
            } else {
                throw new Error('Unsupported file type. Please upload .txt, .pdf, .doc, or .docx files.');
            }

            setEnhancedJD(textContent);
            setStatusMessage({ type: 'success', text: `Loaded: ${file.name}` });
            setBackendMessage(`File loaded successfully: ${file.name}`);
            setTimeout(() => setStatusMessage(null), 3000);
        } catch (error) {
            console.error('Error reading file:', error);
            setStatusMessage({ type: 'error', text: error.message || 'Failed to read file' });
            setBackendMessage(`Error: ${error.message}`);
            setTimeout(() => setStatusMessage(null), 3000);
        } finally {
            setIsLoading(false);
        }
    };

    const triggerFileInput = () => {
        document.getElementById('jd-file-input').click();
    };

    const handleEnhanceJD = async () => {
        if (!enhancedJD.trim()) {
            setStatusMessage({ type: 'error', text: 'Please enter a job description first' });
            setTimeout(() => setStatusMessage(null), 3000);
            return;
        }

        setIsLoading(true);
        setStatusMessage({ type: 'info', text: 'Enhancing job description...' });
        setBackendMessage('Sending request to backend...');

        try {
            const response = await authenticatedFetch(`${API_BASE_URL}/api/enhance-jd`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    job_description: enhancedJD,
                    org_context: orgContext
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                setEnhancedJD(data.enhanced_jd);
                setStatusMessage({ type: 'success', text: 'Job description enhanced successfully!' });
                setBackendMessage(data.message || 'Enhancement completed');
                setTimeout(() => setStatusMessage(null), 3000);
            } else {
                throw new Error(data.error || 'Failed to enhance job description');
            }
        } catch (error) {
            console.error('Error enhancing JD:', error);
            const errorMessage = error.message || 'Failed to connect to backend';
            setStatusMessage({ type: 'error', text: errorMessage });
            setBackendMessage(`Error: ${errorMessage}`);

            // If session expired, redirect to login
            if (errorMessage.includes('Session expired') || errorMessage.includes('Not authenticated')) {
                setTimeout(() => {
                    logout();
                    navigate('/login');
                }, 2000);
            }
            setTimeout(() => setStatusMessage(null), 3000);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSaveEnhancedJD = () => {
        if (!enhancedJD.trim()) {
            setStatusMessage({ type: 'error', text: 'No enhanced job description to save' });
            setTimeout(() => setStatusMessage(null), 3000);
            return;
        }

        // Create blob and download
        const blob = new Blob([enhancedJD], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'enhanced_job_description.txt';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

        setStatusMessage({ type: 'success', text: 'Enhanced JD saved successfully!' });
        setTimeout(() => setStatusMessage(null), 3000);
    };

    return (
        <div className="enhancement-page">
            {/* Header */}
            <header className="header">
                <div className="header-container">
                    <div className="logo">Dechivo<span className="beta-tag">. beta</span></div>
                    <nav className="nav">
                        <ul className="nav-links">
                            <li>
                                <Link to="/" className="nav-link">Home</Link>
                            </li>
                            <li>
                                <Link to="/enhance" className="nav-link">Enhance</Link>
                            </li>
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
                            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                                <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
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
                                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                        <path d="M6 14H3.33333C2.97971 14 2.64057 13.8595 2.39052 13.6095C2.14048 13.3594 2 13.0203 2 12.6667V3.33333C2 2.97971 2.14048 2.64057 2.39052 2.39052C2.64057 2.14048 2.97971 2 3.33333 2H6M10.6667 11.3333L14 8M14 8L10.6667 4.66667M14 8H6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    Logout
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="enhancement-main">
                {/* Back Navigation */}
                <div className="back-navigation">
                    <Link to="/" className="back-link">
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M19 12H5M5 12L12 19M5 12L12 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                        Back
                    </Link>
                </div>

                {/* Status Message */}
                {statusMessage && (
                    <div className={`status-message ${statusMessage.type}`}>
                        {statusMessage.text}
                    </div>
                )}

                {/* Organizational Context Section */}
                <div className="org-context-section">
                    <button
                        className="org-context-toggle"
                        onClick={() => setShowOrgContext(!showOrgContext)}
                    >
                        <svg viewBox="0 0 24 24" fill="none" width="20" height="20">
                            <path d="M19 21V19C19 17.9391 18.5786 16.9217 17.8284 16.1716C17.0783 15.4214 16.0609 15 15 15H9C7.93913 15 6.92172 15.4214 6.17157 16.1716C5.42143 16.9217 5 17.9391 5 19V21M16 7C16 9.20914 14.2091 11 12 11C9.79086 11 8 9.20914 8 7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                        <span>Organizational Context</span>
                        {getFilledContextCount() > 0 && (
                            <span className="context-badge">{getFilledContextCount()} filled</span>
                        )}
                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            width="16"
                            height="16"
                            style={{ transform: showOrgContext ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }}
                        >
                            <path d="M6 9L12 15L18 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </button>

                    {showOrgContext && (
                        <div className="org-context-form">
                            <div className="org-context-grid">
                                {/* Company Information */}
                                <div className="org-context-group">
                                    <h4>Company Information</h4>
                                    <div className="form-field">
                                        <label>Company Name</label>
                                        <input
                                            type="text"
                                            placeholder="e.g., TechCorp Ltd"
                                            value={orgContext.company_name}
                                            onChange={(e) => handleOrgContextChange('company_name', e.target.value)}
                                        />
                                    </div>
                                    <div className="form-field">
                                        <label>Industry</label>
                                        <input
                                            type="text"
                                            placeholder="e.g., Financial Services, Healthcare"
                                            value={orgContext.org_industry}
                                            onChange={(e) => handleOrgContextChange('org_industry', e.target.value)}
                                        />
                                    </div>
                                    <div className="form-field">
                                        <label>Company Description</label>
                                        <textarea
                                            placeholder="Brief description of the company..."
                                            rows="2"
                                            value={orgContext.company_description}
                                            onChange={(e) => handleOrgContextChange('company_description', e.target.value)}
                                        />
                                    </div>
                                    <div className="form-field">
                                        <label>Company Culture</label>
                                        <input
                                            type="text"
                                            placeholder="e.g., Innovation-focused, collaborative"
                                            value={orgContext.company_culture}
                                            onChange={(e) => handleOrgContextChange('company_culture', e.target.value)}
                                        />
                                    </div>
                                    <div className="form-field">
                                        <label>Company Values</label>
                                        <input
                                            type="text"
                                            placeholder="e.g., Integrity, Excellence, Innovation"
                                            value={orgContext.company_values}
                                            onChange={(e) => handleOrgContextChange('company_values', e.target.value)}
                                        />
                                    </div>
                                </div>

                                {/* Role Details */}
                                <div className="org-context-group">
                                    <h4>Role Details</h4>
                                    <div className="form-field">
                                        <label>Role Type</label>
                                        <select
                                            value={orgContext.role_type}
                                            onChange={(e) => handleOrgContextChange('role_type', e.target.value)}
                                        >
                                            <option value="">Select type...</option>
                                            <option value="Permanent">Permanent</option>
                                            <option value="Contract">Contract</option>
                                            <option value="Fixed-term">Fixed-term</option>
                                            <option value="Part-time">Part-time</option>
                                            <option value="Internship">Internship</option>
                                        </select>
                                    </div>
                                    <div className="form-field">
                                        <label>Role Grade/Band</label>
                                        <input
                                            type="text"
                                            placeholder="e.g., Senior (L5), Manager (M2)"
                                            value={orgContext.role_grade}
                                            onChange={(e) => handleOrgContextChange('role_grade', e.target.value)}
                                        />
                                    </div>
                                    <div className="form-field">
                                        <label>Reports To</label>
                                        <input
                                            type="text"
                                            placeholder="e.g., Engineering Manager, CTO"
                                            value={orgContext.reporting_to}
                                            onChange={(e) => handleOrgContextChange('reporting_to', e.target.value)}
                                        />
                                    </div>
                                    <div className="form-field">
                                        <label>Business Context</label>
                                        <textarea
                                            placeholder="Business context for this role..."
                                            rows="2"
                                            value={orgContext.business_context}
                                            onChange={(e) => handleOrgContextChange('business_context', e.target.value)}
                                        />
                                    </div>
                                    <div className="form-field">
                                        <label>Role-Specific Context</label>
                                        <textarea
                                            placeholder="Any company-specific context for this role..."
                                            rows="2"
                                            value={orgContext.role_context}
                                            onChange={(e) => handleOrgContextChange('role_context', e.target.value)}
                                        />
                                    </div>
                                </div>

                                {/* Work Environment */}
                                <div className="org-context-group">
                                    <h4>Work Environment</h4>
                                    <div className="form-field">
                                        <label>Location</label>
                                        <input
                                            type="text"
                                            placeholder="e.g., London, UK / New York, NY"
                                            value={orgContext.location}
                                            onChange={(e) => handleOrgContextChange('location', e.target.value)}
                                        />
                                    </div>
                                    <div className="form-field">
                                        <label>Work Environment</label>
                                        <select
                                            value={orgContext.work_environment}
                                            onChange={(e) => handleOrgContextChange('work_environment', e.target.value)}
                                        >
                                            <option value="">Select environment...</option>
                                            <option value="Onsite">Onsite</option>
                                            <option value="Remote">Remote</option>
                                            <option value="Hybrid">Hybrid</option>
                                            <option value="Flexible">Flexible</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Editor Container */}
                <div className="editor-container" style={{ gridTemplateColumns: '1fr' }}>
                    {/* Enhanced JD */}
                    <div className="editor-section" style={{ position: 'relative' }}>
                        {isLoading && (
                            <div className="loading-overlay">
                                <div className="loading-spinner"></div>
                            </div>
                        )}
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', gap: '1rem' }}>
                            <label className="editor-label" style={{ marginBottom: 0 }}>
                                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                </svg>
                                Enhanced JD
                            </label>

                            {/* Backend Message Display */}
                            <div className="backend-message-display">
                                <div className="backend-message-content">
                                    {backendMessage}
                                </div>
                            </div>

                            {/* Action Buttons */}
                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                                <input
                                    type="file"
                                    id="jd-file-input"
                                    className="file-input-hidden"
                                    onChange={handleFileChange}
                                    accept=".txt,.doc,.docx,.pdf"
                                />
                                <button
                                    className="btn btn-primary btn-icon"
                                    onClick={handleEnhanceJD}
                                    disabled={isLoading}
                                    style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
                                >
                                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    Enhance
                                </button>
                                <button className="btn btn-secondary btn-icon" onClick={() => {/* Edit functionality */ }} style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}>
                                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M11 4H7C5.89543 4 5 4.89543 5 6V18C5 19.1046 5.89543 20 7 20H17C18.1046 20 19 19.1046 19 18V14M17.5 2.5C18.3284 1.67157 19.6716 1.67157 20.5 2.5C21.3284 3.32843 21.3284 4.67157 20.5 5.5L11 15H8V12L17.5 2.5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    Edit JD
                                </button>
                                <button
                                    className="btn btn-secondary btn-icon"
                                    onClick={() => {/* Publish functionality */ }}
                                    disabled={!enhancedJD.trim()}
                                    style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
                                >
                                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    Publish
                                </button>
                                <button
                                    className={`btn btn-secondary btn-icon ${!enhancedJD.trim() ? 'btn-disabled' : ''}`}
                                    onClick={handleSaveEnhancedJD}
                                    disabled={!enhancedJD.trim()}
                                    style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
                                >
                                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15M7 10L12 15M12 15L17 10M12 15V3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    Download
                                </button>
                            </div>
                        </div>
                        <textarea
                            className="editor-textarea"
                            placeholder="Enhanced job description will appear here..."
                            value={enhancedJD}
                            onChange={(e) => setEnhancedJD(e.target.value)}
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
                    <p className="footer-text">
                        © 2024 All rights reserved.
                    </p>
                </div>
            </footer>
        </div>
    );
};

export default EnhancementPage;
