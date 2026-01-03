/**
 * Mixpanel Analytics Utility for Dechivo
 * 
 * Events tracked:
 * - User: signup, login, logout
 * - Enhancement: started, completed, failed
 * - File: uploaded
 * - Navigation: page views
 * - Features: org context filled, download
 */

// Get Mixpanel from window (loaded via script tag in index.html)
const getMixpanel = () => {
    if (typeof window !== 'undefined' && window.mixpanel) {
        return window.mixpanel;
    }
    return null;
};

/**
 * Identify a user for tracking
 * Call this after login/signup
 */
export const identifyUser = (userId, traits = {}) => {
    const mp = getMixpanel();
    if (mp) {
        mp.identify(userId);
        mp.people.set({
            $email: traits.email,
            $name: traits.full_name || traits.username,
            username: traits.username,
            organization: traits.organization,
            ...traits
        });
        console.log('📊 Analytics: User identified', userId);
    }
};

/**
 * Reset user identity (on logout)
 */
export const resetUser = () => {
    const mp = getMixpanel();
    if (mp) {
        mp.reset();
        console.log('📊 Analytics: User reset');
    }
};

/**
 * Track a custom event
 */
export const trackEvent = (eventName, properties = {}) => {
    const mp = getMixpanel();
    if (mp) {
        mp.track(eventName, {
            timestamp: new Date().toISOString(),
            ...properties
        });
        console.log('📊 Analytics:', eventName, properties);
    }
};

/**
 * Track page view
 */
export const trackPageView = (pageName, properties = {}) => {
    trackEvent('Page View', {
        page: pageName,
        url: window.location.pathname,
        ...properties
    });
};

// ==================== Specific Event Trackers ====================

/**
 * Track user signup
 */
export const trackSignup = (userId, email, username) => {
    trackEvent('User Signup', {
        user_id: userId,
        email,
        username,
        signup_method: 'email'
    });
};

/**
 * Track user login
 */
export const trackLogin = (userId, method = 'email') => {
    trackEvent('User Login', {
        user_id: userId,
        login_method: method
    });
};

/**
 * Track logout
 */
export const trackLogout = () => {
    trackEvent('User Logout');
};

/**
 * Track file upload
 */
export const trackFileUpload = (fileName, fileType, fileSize) => {
    trackEvent('File Uploaded', {
        file_name: fileName,
        file_type: fileType,
        file_size_bytes: fileSize
    });
};

/**
 * Track enhancement started
 */
export const trackEnhancementStarted = (jdLength, orgContextFilled) => {
    trackEvent('Enhancement Started', {
        jd_length: jdLength,
        org_context_fields_filled: orgContextFilled
    });
};

/**
 * Track enhancement completed
 */
export const trackEnhancementCompleted = (skillsCount, duration, orgContextFilled) => {
    trackEvent('Enhancement Completed', {
        skills_count: skillsCount,
        duration_seconds: duration,
        org_context_fields_filled: orgContextFilled,
        success: true
    });
};

/**
 * Track enhancement failed
 */
export const trackEnhancementFailed = (errorMessage) => {
    trackEvent('Enhancement Failed', {
        error: errorMessage,
        success: false
    });
};

/**
 * Track JD download
 */
export const trackDownload = (format = 'txt') => {
    trackEvent('JD Downloaded', {
        format
    });
};

/**
 * Track org context interaction
 */
export const trackOrgContextToggle = (isOpen) => {
    trackEvent('Org Context Toggled', {
        is_open: isOpen
    });
};

export default {
    identifyUser,
    resetUser,
    trackEvent,
    trackPageView,
    trackSignup,
    trackLogin,
    trackLogout,
    trackFileUpload,
    trackEnhancementStarted,
    trackEnhancementCompleted,
    trackEnhancementFailed,
    trackDownload,
    trackOrgContextToggle
};
