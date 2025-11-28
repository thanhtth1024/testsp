import React, { createContext, useState, useEffect } from 'react';
import { apiService } from '../services/api';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is already logged in on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const response = await apiService.getCurrentUser();
      setUser(response.data);
      setIsAuthenticated(true);
    } catch (error) {
      // Token invalid or expired
      localStorage.removeItem('token');
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      setError(null);
      const response = await apiService.login({ username, password });
      const { access_token } = response.data;
      
      // Save token to localStorage
      localStorage.setItem('token', access_token);
      
      // Get user info
      const userResponse = await apiService.getCurrentUser();
      setUser(userResponse.data);
      setIsAuthenticated(true);
      
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Đăng nhập thất bại. Vui lòng thử lại.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const register = async (userData) => {
    try {
      setError(null);
      const response = await apiService.register(userData);
      
      // Auto login after successful registration
      const loginResult = await login(userData.username, userData.password);
      
      if (loginResult.success) {
        return { success: true, user: response.data };
      } else {
        return { success: false, error: 'Đăng ký thành công nhưng đăng nhập thất bại. Vui lòng đăng nhập thủ công.' };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Đăng ký thất bại. Vui lòng thử lại.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const logout = async () => {
    try {
      await apiService.logout();
    } catch (error) {
      // Ignore logout API errors
      console.error('Logout error:', error);
    } finally {
      // Always clear local state and token
      localStorage.removeItem('token');
      setUser(null);
      setIsAuthenticated(false);
      setError(null);
    }
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    error,
    login,
    register,
    logout,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
