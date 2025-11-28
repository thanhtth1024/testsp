import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

/**
 * Custom hook to access authentication context.
 * Provides easy access to user state, auth functions, and loading states.
 * 
 * @returns {Object} Authentication context value
 * @property {Object|null} user - Current user data
 * @property {boolean} isAuthenticated - Whether user is logged in
 * @property {boolean} loading - Loading state during auth operations
 * @property {string|null} error - Error message if any
 * @property {Function} login - Login function (username, password)
 * @property {Function} register - Register function (userData)
 * @property {Function} logout - Logout function
 * @property {Function} checkAuth - Check authentication status
 * 
 * @example
 * const { user, login, logout, isAuthenticated } = useAuth();
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};
