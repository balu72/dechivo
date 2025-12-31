import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [accessToken, setAccessToken] = useState(localStorage.getItem('access_token'));
    const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refresh_token'));

    useEffect(() => {
        // Check if user is already logged in
        const token = localStorage.getItem('access_token');
        const userData = localStorage.getItem('user');

        if (token && userData) {
            try {
                setUser(JSON.parse(userData));
                setAccessToken(token);
            } catch (error) {
                console.error('Error parsing user data:', error);
                logout();
            }
        }
        setLoading(false);
    }, []);

    const login = async (emailOrUsername, password) => {
        try {
            const response = await fetch('http://localhost:5000/api/auth/login', {
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

            return { success: true };
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, error: error.message };
        }
    };

    const register = async (userData) => {
        try {
            const response = await fetch('http://localhost:5000/api/auth/register', {
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

            return { success: true };
        } catch (error) {
            console.error('Registration error:', error);
            return { success: false, error: error.message };
        }
    };

    const logout = async () => {
        try {
            if (accessToken) {
                await fetch('http://localhost:5000/api/auth/logout', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
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
        }
    };

    const getAccessToken = () => {
        return accessToken || localStorage.getItem('access_token');
    };

    const value = {
        user,
        loading,
        login,
        register,
        logout,
        getAccessToken,
        isAuthenticated: !!user,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
