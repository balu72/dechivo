import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import mammoth from 'mammoth';
import * as pdfjsLib from 'pdfjs-dist';
import './LandingPage.css';

// Configure PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.mjs`;

const LandingPage = () => {
    const navigate = useNavigate();
    const { isAuthenticated } = useAuth();
    const [scrolled, setScrolled] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const [fileContent, setFileContent] = useState('');

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

    const scrollToSection = (sectionId) => {
        const element = document.getElementById(sectionId);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    };

    const handleFileChange = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setSelectedFile(file);
        const fileExtension = file.name.split('.').pop().toLowerCase();

        try {
            let textContent = '';

            if (fileExtension === 'txt') {
                textContent = await new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = (e) => resolve(e.target.result);
                    reader.onerror = reject;
                    reader.readAsText(file);
                });
            } else if (fileExtension === 'pdf') {
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
                const arrayBuffer = await file.arrayBuffer();
                const result = await mammoth.extractRawText({ arrayBuffer });
                textContent = result.value;
            }

            setFileContent(textContent);
            console.log('File parsed successfully:', file.name);
        } catch (error) {
            console.error('Error parsing file:', error);
            alert('Error reading file: ' + error.message);
        }
    };

    const triggerFileInput = () => {
        document.getElementById('file-input').click();
    };

    const handleEnhanceClick = () => {
        // Redirect to login if not authenticated
        if (!isAuthenticated) {
            navigate('/login');
            return;
        }

        if (selectedFile && fileContent) {
            // Navigate with file content
            navigate('/enhance', { state: { fileContent, fileName: selectedFile.name } });
        } else {
            // Navigate without content
            navigate('/enhance');
        }
    };

    return (
        <div className="landing-page">
            {/* Header */}
            <header className={`header ${scrolled ? 'scrolled' : ''}`}>
                <div className="header-container">
                    <div className="logo">Dechivo</div>
                    <nav className="nav">
                        <ul className="nav-links">
                            <li>
                                <a href="#home" className="nav-link active" onClick={(e) => {
                                    e.preventDefault();
                                    scrollToSection('home');
                                }}>
                                    Home
                                </a>
                            </li>
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
                        <Link to="/enhance" className="btn btn-primary">Dashboard</Link>
                    )}
                </div>
            </header>

            {/* Hero Section */}
            <section className="hero" id="home">
                <div className="hero-container">
                    <div className="hero-content">
                        <h1 className="hero-title">
                            Enhance Your <span className="gradient-text">ICT Job Descriptions</span>
                        </h1>
                        <p className="hero-subtitle">
                            Dechivo leverages the SFIA framework to create comprehensive, standardized job descriptions for ICT roles
                        </p>
                        <div className="hero-cta">
                            <input
                                type="file"
                                id="file-input"
                                onChange={handleFileChange}
                                style={{ display: 'none' }}
                                accept=".txt,.pdf,.doc,.docx,.json"
                            />
                            <button className="btn btn-primary btn-large" onClick={triggerFileInput}>
                                {selectedFile ? `File: ${selectedFile.name}` : 'Load JD File'}
                            </button>
                            <button
                                className="btn btn-secondary btn-large"
                                onClick={handleEnhanceClick}
                                disabled={!selectedFile}
                                style={{ opacity: selectedFile ? 1 : 0.5 }}
                            >
                                Enhance JD
                            </button>
                        </div>
                    </div>
                    <div className="hero-image">
                        <img
                            src="/hero-illustration.png"
                            alt="SFIA Job Description Enhancement Illustration"
                            className="hero-illustration"
                        />
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
