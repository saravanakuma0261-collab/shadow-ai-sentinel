import React, { createContext, useContext, useState, useEffect } from 'react';
import client from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('shadow_ai_token'));
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('shadow_ai_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(true);

  // Parse JWT payload safely
  const parseJwt = (jwtToken) => {
    try {
      const base64Url = jwtToken.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      return JSON.parse(jsonPayload);
    } catch (e) {
      return null;
    }
  };

  const setAuthData = (jwtToken, userData = null) => {
    localStorage.setItem('shadow_ai_token', jwtToken);
    setToken(jwtToken);

    if (userData) {
      localStorage.setItem('shadow_ai_user', JSON.stringify(userData));
      setUser(userData);
    } else {
      const payload = parseJwt(jwtToken);
      if (payload) {
        const extractedUser = {
          id: payload.sub,
          email: payload.email,
          role: payload.role,
          name: payload.name || payload.email.split('@')[0],
        };
        localStorage.setItem('shadow_ai_user', JSON.stringify(extractedUser));
        setUser(extractedUser);
      }
    }
  };

  const login = async (email, password) => {
    const response = await client.post('/auth/login', { email, password });
    const { access_token, user: userData } = response.data;
    setAuthData(access_token, userData);
    return userData;
  };

  const register = async (name, email, password) => {
    const response = await client.post('/auth/register', { name, email, password });
    const { access_token, user: userData } = response.data;
    setAuthData(access_token, userData);
    return userData;
  };

  const logout = () => {
    try {
      client.post('/auth/logout').catch(() => {});
    } finally {
      localStorage.removeItem('shadow_ai_token');
      localStorage.removeItem('shadow_ai_user');
      setToken(null);
      setUser(null);
    }
  };

  const hasRole = (allowedRoles) => {
    if (!user || !user.role) return false;
    const list = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles];
    return list.map((r) => r.toLowerCase()).includes(user.role.toLowerCase());
  };

  // Refresh profile on mount if token exists
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('shadow_ai_token');
      if (storedToken) {
        try {
          const res = await client.get('/auth/me');
          setUser(res.data);
          localStorage.setItem('shadow_ai_user', JSON.stringify(res.data));
        } catch (err) {
          // Handled by client interceptor if 401
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        role: user?.role || 'viewer',
        isAuthenticated: !!token && !!user,
        loading,
        login,
        register,
        logout,
        setAuthData,
        hasRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
