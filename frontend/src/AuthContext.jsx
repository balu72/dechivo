import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { identifyUser, resetUser, trackLogin, trackSignup, trackLogout } from './analytics';

const AuthContext = createContext(null);

const API_BASE_URL = '';  // Use relative URL for both dev and production

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

// Helper to check if token is expired
const isTokenExpired = (token) => {
    if (!token) return true;

    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const exp = payload.exp * 1000; // Convert to milliseconds
        // Return true if token expires in less than 5 minutes
        return Date.now() > exp - (5 * 60 * 1000);
    } catch (error) {
        console.error('Error parsing token:', error);
        return true;
    }
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [accessToken, setAccessToken] = useState(localStorage.getItem('access_token'));
    const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refresh_token'));
    const [isRefreshing, setIsRefreshing] = useState(false);

    // Refresh the access token
    const refreshAccessToken = useCallback(async () => {
        const storedRefreshToken = localStorage.getItem('refresh_token');

        if (!storedRefreshToken || isRefreshing) {
            return null;
        }

        setIsRefreshing(true);

        try {
            const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${storedRefreshToken}`,
                },
            });

            if (!response.ok) {
                throw new Error('Token refresh failed');
            }

            const data = await response.json();

            if (data.access_token) {
                localStorage.setItem('access_token', data.access_token);
                setAccessToken(data.access_token);
                console.log('✅ Token refreshed successfully');
                return data.access_token;
            }

            throw new Error('No access token in response');
        } catch (error) {
            console.error('Token refresh error:', error);
            // If refresh fails, logout
            await logout();
            return null;
        } finally {
            setIsRefreshing(false);
        }
    }, [isRefreshing]);

    // Get a valid access token (refresh if needed)
    const getAccessToken = useCallback(async () => {
        const storedToken = localStorage.getItem('access_token');

        if (!storedToken) {
            return null;
        }

        // Check if token is expired or about to expire
        if (isTokenExpired(storedToken)) {
            console.log('⚠️ Token expired or expiring soon, refreshing...');
            return await refreshAccessToken();
        }

        return storedToken;
    }, [refreshAccessToken]);

    // Make an authenticated fetch request with automatic token refresh
    const authenticatedFetch = useCallback(async (url, options = {}) => {
        let token = await getAccessToken();

        if (!token) {
            throw new Error('Not authenticated');
        }

        // Make the request
        const response = await fetch(url, {
            ...options,
            headers: {
                ...options.headers,
                'Authorization': `Bearer ${token}`,
            },
        });

        // If 401 or 422 (token issue), try to refresh and retry
        if (response.status === 401 || response.status === 422) {
            console.log('🔄 Token rejected, attempting refresh...');
            token = await refreshAccessToken();

            if (!token) {
                throw new Error('Session expired. Please login again.');
            }

            // Retry the request with new token
            return fetch(url, {
                ...options,
                headers: {
                    ...options.headers,
                    'Authorization': `Bearer ${token}`,
                },
            });
        }

        return response;
    }, [getAccessToken, refreshAccessToken]);

    useEffect(() => {
        // Check if user is already logged in
        const token = localStorage.getItem('access_token');
        const userData = localStorage.getItem('user');

        if (token && userData) {
            try {
                // Check if token is valid
                if (!isTokenExpired(token)) {
                    setUser(JSON.parse(userData));
                    setAccessToken(token);
                } else {
                    // Try to refresh
                    refreshAccessToken().then(newToken => {
                        if (newToken) {
                            setUser(JSON.parse(userData));
                            setAccessToken(newToken);
                        } else {
                            logout();
                        }
                    });
                }
            } catch (error) {
                console.error('Error parsing user data:', error);
                logout();
            }
        }
        setLoading(false);
    }, []);

    const login = async (emailOrUsername, password) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email_or_username: emailOrUsername,
                    password: password,
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Login failed');
            }

            // Store tokens and user data
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            localStorage.setItem('user', JSON.stringify(data.user));

            setUser(data.user);
            setAccessToken(data.access_token);
            setRefreshToken(data.refresh_token);

            // Track login event
            identifyUser(data.user.id, data.user);
            trackLogin(data.user.id);

            return { success: true };
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, error: error.message };
        }
    };

    const register = async (userData) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Registration failed');
            }

            // Store tokens and user data
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            localStorage.setItem('user', JSON.stringify(data.user));

            setUser(data.user);
            setAccessToken(data.access_token);
            setRefreshToken(data.refresh_token);

            // Track signup event
            identifyUser(data.user.id, data.user);
            trackSignup(data.user.id, data.user.email, data.user.username);

            return { success: true };
        } catch (error) {
            console.error('Registration error:', error);
            return { success: false, error: error.message };
        }
    };

    const logout = async () => {
        try {
            const token = localStorage.getItem('access_token');
            if (token) {
                await fetch(`${API_BASE_URL}/api/auth/logout`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            // Clear local storage and state
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
            setUser(null);
            setAccessToken(null);
            setRefreshToken(null);
            // Track logout and reset user
            trackLogout();
            resetUser();
        }
    };

    const value = {
        user,
        loading,
        login,
        register,
        logout,
        getAccessToken,
        authenticatedFetch,
        refreshAccessToken,
        isAuthenticated: !!user,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
