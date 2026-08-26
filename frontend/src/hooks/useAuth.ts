import { useState, useEffect } from 'react';
import { User } from '@/types';
import AuthService from '@/lib/auth';

export function useAuth() {
  const [user, setUser] = useState<User | null>(AuthService.getCurrentUser());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check authentication status on mount
    const checkAuth = () => {
      try {
        const currentUser = AuthService.getCurrentUser();
        setUser(currentUser);
        setLoading(false);
      } catch (err) {
        setError('Failed to check authentication status');
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (username: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const loggedInUser = await AuthService.login(username, password);
      setUser(loggedInUser);
      return loggedInUser;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (
    username: string,
    email: string,
    password: string,
    role: 'ADMIN' | 'ANALYST' | 'VIEWER'
  ) => {
    setLoading(true);
    setError(null);
    try {
      const registeredUser = await AuthService.register(username, email, password, role);
      return registeredUser;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    setError(null);
    try {
      await AuthService.logout();
      setUser(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Logout failed');
    } finally {
      setLoading(false);
    }
  };

  const isAuthenticated = AuthService.isAuthenticated();
  const hasRole = (role: 'ADMIN' | 'ANALYST' | 'VIEWER') => AuthService.hasRole(role);
  const hasPermission = (permission: string) => AuthService.hasPermission(permission);

  return {
    user,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    hasRole,
    hasPermission,
  };
}