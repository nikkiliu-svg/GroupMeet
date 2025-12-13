/**
 * Authentication hook for managing auth state.
 */
import { useState, useEffect } from 'react';
import { authAPI } from '../services/api';
import { AuthStatus } from '../services/types';

export function useAuth() {
  const [authStatus, setAuthStatus] = useState<AuthStatus>({ authenticated: false });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const status = await authAPI.getStatus();
      setAuthStatus(status);
    } catch (error) {
      setAuthStatus({ authenticated: false });
    } finally {
      setLoading(false);
    }
  };

  const login = () => {
    authAPI.login();
  };

  const logout = () => {
    authAPI.logout();
  };

  return {
    authStatus,
    loading,
    login,
    logout,
    checkAuthStatus,
  };
}

