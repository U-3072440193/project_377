// boards/frontend/src/context/UserContext.js
import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from '../components/axios';

const UserContext = createContext();

export const UserProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = async () => {
        try {
            const response = await axios.get('/api/check-auth/');
            if (response.data.isAuthenticated) {
                setUser(response.data.user);
                setIsAuthenticated(true);
            }
        } catch (error) {
            console.error('Auth check failed:', error);
        } finally {
            setLoading(false);
        }
    };

    const logout = async () => {
        try {
            await axios.post('/logout/');
            setUser(null);
            setIsAuthenticated(false);
            window.location.href = '/';
        } catch (error) {
            console.error('Logout failed:', error);
        }
    };

    return (
        <UserContext.Provider value={{
            user,
            isAuthenticated,
            loading,
            checkAuth,
            logout
        }}>
            {children}
        </UserContext.Provider>
    );
};

export const useUser = () => useContext(UserContext);