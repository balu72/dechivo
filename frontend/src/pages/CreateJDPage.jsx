import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import '../styles/EnhancementPage.css';
import '../styles/LandingPage.css';

const API_BASE_URL = '';

const CreateJDPage = () => {
    const navigate = useNavigate();
    const { user, logout, authenticatedFetch } = useAuth();
    const [showUserMenu, setShowUserMenu] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [statusMessage, setStatusMessage] = useState(null);

    // Organizational context state
    const [orgContext, setOrgContext] = useState({
        org_industry: '',
        company_name: '',
        company_description: '',
        company_culture: '',
        company_values: '',
        business_context: '',
        role_context: '',
        role_title: '',
        role_type: '',
        role_grade: '',
        location: '',
        work_environment: '',
        reporting_to: '',
        additional_context: ''
    });

    // Autocomplete state for skills
    const [skillSuggestions, setSkillSuggestions] = useState([]);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [isSearching, setIsSearching] = useState(false);

    const handleOrgContextChange = (field, value) => {
        setOrgContext(prev => ({ ...prev, [field]: value }));

        // Trigger skill search for role_context field
        if (field === 'role_context') {
            searchSkills(value);
        }
    };

    const searchSkills = async (query) => {
        if (!query || query.length < 2) {
            setSkillSuggestions([]);
            setShowSuggestions(false);
            return;
        }

        setIsSearching(true);
        try {
            const response = await authenticatedFetch(`${API_BASE_URL}/api/search-skills?query=${encodeURIComponent(query)}&limit=10`);
            const data = await response.json();

            if (response.ok && data.skills) {
                setSkillSuggestions(data.skills);
                setShowSuggestions(true);
            }
        } catch (error) {
            console.error('Error searching skills:', error);
        } finally {
            setIsSearching(false);
        }
    };

    const handleSkillSelect = (skillName) => {
        const currentSkills = orgContext.role_context || '';
        const skillsArray = currentSkills.split(',').map(s => s.trim()).filter(s => s);

        // Replace the last (partial) entry with the selected skill
        if (skillsArray.length > 0) {
            // Remove the last partial entry and add the selected skill
            skillsArray[skillsArray.length - 1] = skillName;
        } else {
            // No existing skills, just add the selected one
            skillsArray.push(skillName);
        }

        // Remove duplicates
        const uniqueSkills = [...new Set(skillsArray)];

        setOrgContext(prev => ({ ...prev, role_context: uniqueSkills.join(', ') }));
        setShowSuggestions(false);
        setSkillSuggestions([]);
    };

    const getFilledContextCount = () => {
        return Object.values(orgContext).filter(v => v.trim()).length;
    };

    // Required fields that must be filled before proceeding
    const requiredContextFields = [
        'company_name', 'company_description',
        'role_title', 'role_type', 'role_grade', 'reporting_to',
        'location', 'work_environment'
    ];

    const isContextComplete = () => {
        return requiredContextFields.every(field => orgContext[field]?.trim());
    };

    const handleCreate = async () => {
        if (!isContextComplete()) {
            setStatusMessage({ type: 'error', text: 'Please fill all required fields' });
            return;
        }

        setIsLoading(true);
        setStatusMessage({ type: 'info', text: 'Creating your job description...' });

        try {
            const response = await authenticatedFetch(`${API_BASE_URL}/api/create-jd`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    org_context: orgContext
                }),
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // Navigate to enhance page with the created JD
                navigate('/enhance', {
                    state: {
                        enhancedJD: data.job_description,
                        regeneratedJD: data.job_description,
                        skills: data.skills || [],
                        extractedKeywords: data.extracted_keywords || [],
                        orgContext: orgContext
                    }
                });
            } else {
                setStatusMessage({
                    type: 'error',
                    text: data.error || 'Failed to create job description'
                });
            }
        } catch (error) {
            console.error('Create JD error:', error);
            setStatusMessage({
                type: 'error',
                text: 'Network error. Please try again.'
            });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="enhancement-page">
            {/* Header */}
            <header className="enhancement-header">
                <div className="header-container">
                    <Link to="/" className="logo">Dechivo<span className="beta-tag">. beta</span></Link>
                    <div className="header-actions">
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
                <div className="enhance-input-container">
                    <h1 className="page-highlight">Tell us about the company & role</h1>

                    {/* Organizational Context Section */}
                    <div className="input-section create-jd-section">
                        {getFilledContextCount() > 0 && (
                            <div className="context-badge-row">
                                <span className="context-badge">{getFilledContextCount()} fields filled</span>
                            </div>
                        )}

                        <div className="create-jd-grid">
                            {/* Company Information */}
                            <div className="org-context-group">
                                <h4>Company Information</h4>
                                <div className="form-row-inline">
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
                                        <label>Company Description</label>
                                        <textarea
                                            placeholder="Brief description of the company..."
                                            rows="2"
                                            value={orgContext.company_description}
                                            onChange={(e) => handleOrgContextChange('company_description', e.target.value)}
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Role Details */}
                            <div className="org-context-group">
                                <h4>Role Details</h4>
                                <div className="form-row-inline">
                                    <div className="form-field">
                                        <label>Role Title</label>
                                        <input
                                            type="text"
                                            placeholder="e.g., Senior Software Engineer"
                                            value={orgContext.role_title}
                                            onChange={(e) => handleOrgContextChange('role_title', e.target.value)}
                                        />
                                    </div>
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
                                </div>
                                <div className="form-row-inline">
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
                                </div>
                            </div>

                            {/* Skills Details */}
                            <div className="org-context-group">
                                <h4>Skills Details</h4>
                                <div className="form-row-inline">
                                    <div className="form-field" style={{ position: 'relative' }}>
                                        <label>Key Skills</label>
                                        <input
                                            type="text"
                                            placeholder="e.g., Python, AWS, Agile, Leadership"
                                            value={orgContext.role_context || ''}
                                            onChange={(e) => handleOrgContextChange('role_context', e.target.value)}
                                            onFocus={() => {
                                                if (skillSuggestions.length > 0) {
                                                    setShowSuggestions(true);
                                                }
                                            }}
                                            onBlur={() => {
                                                // Delay hiding to allow click on suggestion
                                                setTimeout(() => setShowSuggestions(false), 200);
                                            }}
                                        />
                                        {isSearching && (
                                            <div style={{ position: 'absolute', right: '10px', top: '35px' }}>
                                                <div className="loading-spinner" style={{ width: '16px', height: '16px' }}></div>
                                            </div>
                                        )}
                                        {showSuggestions && skillSuggestions.length > 0 && (
                                            <div className="autocomplete-dropdown">
                                                {skillSuggestions.map((skill, index) => (
                                                    <div
                                                        key={index}
                                                        className="autocomplete-item"
                                                        onClick={() => handleSkillSelect(skill.name)}
                                                    >
                                                        <div className="autocomplete-name">{skill.name}</div>
                                                        <div className="autocomplete-desc">{skill.description}</div>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                    <div className="form-field">
                                        <label>Experience Level</label>
                                        <input
                                            type="text"
                                            placeholder="e.g., 3-4 years / 4+ years software development"
                                            value={orgContext.business_context || ''}
                                            onChange={(e) => handleOrgContextChange('business_context', e.target.value)}
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Work Environment */}
                            <div className="org-context-group">
                                <h4>Work Environment</h4>
                                <div className="form-row-inline">
                                    <div className="form-field">
                                        <label>Location</label>
                                        <input
                                            type="text"
                                            placeholder="e.g., Bangalore, India"
                                            value={orgContext.location}
                                            onChange={(e) => handleOrgContextChange('location', e.target.value)}
                                        />
                                    </div>
                                    <div className="form-field">
                                        <label>Work Model</label>
                                        <select
                                            value={orgContext.work_environment}
                                            onChange={(e) => handleOrgContextChange('work_environment', e.target.value)}
                                        >
                                            <option value="">Select model...</option>
                                            <option value="Onsite">Onsite</option>
                                            <option value="Remote">Remote</option>
                                            <option value="Hybrid">Hybrid</option>
                                            <option value="Flexible">Flexible</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            {/* Additional Context */}
                            <div className="org-context-group" style={{ gridColumn: '1 / -1' }}>
                                <h4>Additional Context (optional)</h4>
                                <div className="form-field">

                                    <textarea
                                        placeholder="Enter any additional details, requirements, or context that would help create a better job description..."
                                        value={orgContext.additional_context}
                                        onChange={(e) => handleOrgContextChange('additional_context', e.target.value)}
                                        rows="4"
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Status Message */}
                    {statusMessage && (
                        <div className={`status-message ${statusMessage.type}`}>
                            {statusMessage.text}
                        </div>
                    )}

                    {/* Loading Overlay */}
                    {isLoading && (
                        <div className="loading-overlay-fullpage">
                            <div className="loading-spinner"></div>
                            <p>Creating your job description...</p>
                        </div>
                    )}

                    {/* Create Button */}
                    <div className="enhance-action-right">
                        <button
                            className="btn btn-primary btn-large btn-enhance-main"
                            onClick={handleCreate}
                            disabled={isLoading || !isContextComplete()}
                        >
                            <svg viewBox="0 0 24 24" fill="none" width="24" height="24">
                                <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                            {isLoading ? 'Creating...' : 'Create'}
                        </button>
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

export default CreateJDPage;
