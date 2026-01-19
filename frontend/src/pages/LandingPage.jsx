import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import '../styles/LandingPage.css';

const LandingPage = () => {
    const navigate = useNavigate();
    const { isAuthenticated, user, logout } = useAuth();
    const [scrolled, setScrolled] = useState(false);
    const [showUserMenu, setShowUserMenu] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            const isScrolled = window.scrollY > 20;
            if (isScrolled !== scrolled) {
                setScrolled(isScrolled);
            }
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, [scrolled]);

    const handleEnhanceClick = () => {
        if (!isAuthenticated) {
            navigate('/login');
            return;
        }
        navigate('/create');
    };

    return (
        <div className="landing-page">
            {/* Header */}
            <header className={`header ${scrolled ? 'scrolled' : ''}`}>
                <div className="header-container">
                    <div className="logo">Dechivo<span className="beta-tag">. beta</span></div>
                    <nav className="nav">
                        <ul className="nav-links">
                            <li>
                                <a href="#about" className="nav-link">About</a>
                            </li>
                            <li>
                                <a href="#contact" className="nav-link">Contact</a>
                            </li>
                        </ul>
                    </nav>
                    {!isAuthenticated && (
                        <div className="auth-buttons">
                            <Link to="/login" className="btn btn-ghost">Login</Link>
                            <Link to="/register" className="btn btn-primary">Sign Up</Link>
                        </div>
                    )}
                    {isAuthenticated && (
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
                    )}
                </div>
            </header>

            {/* Hero Section - Split Layout */}
            <section className="hero hero-split" id="home">
                <div className="hero-container hero-container-split">
                    {/* Left Side - Image */}
                    <div className="hero-image-section">
                        <img
                            src="/hero-illustration.png"
                            alt="AI-Powered Job Description Enhancement"
                            className="hero-illustration"
                        />
                    </div>

                    {/* Right Side - Content */}
                    <div className="hero-content-section">
                        <div className="hero-content">
                            <h2 className="hero-title">
                                <span className="gradient-text">Elevate Your Hiring Blueprint!</span>
                            </h2>
                            <ul className="hero-value-props">
                                <li>Create JD from role context</li>
                                <li>Enhance with global skills intelligence.</li>
                                <li>Generate structured interview plans.</li>
                            </ul>
                            <p className="hero-features-title">Capabilities include:</p>
                            <div className="hero-features">
                                <div className="feature-item">
                                    <svg viewBox="0 0 24 24" fill="none" width="24" height="24">
                                        <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    <span>Skill enrichment from 15,000+ global competencies</span>
                                </div>
                                <div className="feature-item">
                                    <svg viewBox="0 0 24 24" fill="none" width="24" height="24">
                                        <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    <span>Alignment with leading global frameworks (SFIA, ESCO, O*NET, Singapore, OASIS)</span>
                                </div>
                                <div className="feature-item">
                                    <svg viewBox="0 0 24 24" fill="none" width="24" height="24">
                                        <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    <span>AI-powered role and competency augmentation</span>
                                </div>
                                <div className="feature-item">
                                    <svg viewBox="0 0 24 24" fill="none" width="24" height="24">
                                        <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    <span>Structured interview plans mapped to role skills and proficiency levels</span>
                                </div>
                            </div>
                        </div>

                        {/* CTA Button - Bottom Right */}
                        <div className="hero-cta-bottom">
                            <button
                                className="btn btn-primary btn-large btn-enhance"
                                onClick={handleEnhanceClick}
                            >
                                <svg viewBox="0 0 24 24" fill="none" width="24" height="24">
                                    <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                </svg>
                                Try It Free
                            </button>
                        </div>
                    </div>
                </div>
            </section>

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

export default LandingPage;
