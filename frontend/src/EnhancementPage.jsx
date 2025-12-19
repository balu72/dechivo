import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import mammoth from 'mammoth';
import * as pdfjsLib from 'pdfjs-dist';
import './EnhancementPage.css';
import './LandingPage.css'; // Reuse header and footer styles

// Configure PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.mjs`;

const API_BASE_URL = 'http://localhost:5000';

const EnhancementPage = () => {
    const location = useLocation();
    const [originalJD, setOriginalJD] = useState('');
    const [enhancedJD, setEnhancedJD] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [statusMessage, setStatusMessage] = useState(null);
    const [backendMessage, setBackendMessage] = useState('Ready to enhance job descriptions...');

    // Auto-enhance when content is passed from landing page
    useEffect(() => {
        if (location.state?.fileContent) {
            const { fileContent, fileName } = location.state;
            setEnhancedJD(fileContent);
            setBackendMessage(`Loaded file: ${fileName}`);
            // Automatically call backend API
            enhanceWithBackend(fileContent, fileName);
        }
    }, [location.state]);

    const enhanceWithBackend = async (content, fileName = 'uploaded file') => {
        setIsLoading(true);
        setBackendMessage('Processing...');

        try {
            const response = await fetch(`${API_BASE_URL}/api/enhance-jd`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    job_description: content
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
            setStatusMessage({ type: 'error', text: error.message || 'Failed to connect to backend' });
            setBackendMessage(`Error: ${error.message}`);
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
            const response = await fetch(`${API_BASE_URL}/api/enhance-jd`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    job_description: enhancedJD
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
            setStatusMessage({ type: 'error', text: error.message || 'Failed to connect to backend' });
            setBackendMessage(`Error: ${error.message}`);
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
                    <div className="logo">Dechivo</div>
                    <nav className="nav">
                        <ul className="nav-links">
                            <li>
                                <a href="/" className="nav-link">Home</a>
                            </li>
                            <li>
                                <a href="#about" className="nav-link">About</a>
                            </li>
                            <li>
                                <a href="#contact" className="nav-link">Contact</a>
                            </li>
                        </ul>
                    </nav>
                </div>
            </header>

            {/* Main Content */}
            <main className="enhancement-main">
                {/* Back Navigation */}
                <div className="back-navigation">
                    <Link to="/" className="back-link">
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M19 12H5M5 12L12 19M5 12L12 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
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
                                <button className="btn btn-secondary btn-icon" onClick={() => {/* Edit functionality */ }} style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}>
                                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M11 4H7C5.89543 4 5 4.89543 5 6V18C5 19.1046 5.89543 20 7 20H17C18.1046 20 19 19.1046 19 18V14M17.5 2.5C18.3284 1.67157 19.6716 1.67157 20.5 2.5C21.3284 3.32843 21.3284 4.67157 20.5 5.5L11 15H8V12L17.5 2.5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                    Edit JD
                                </button>
                                <button
                                    className="btn btn-secondary btn-icon"
                                    onClick={handleEnhanceJD}
                                    disabled={isLoading}
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
