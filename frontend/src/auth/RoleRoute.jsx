import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from './AuthContext';
import NotAuthorized from '../pages/NotAuthorized';

export const RoleRoute = ({ allow = [], children }) => {
  const { hasRole, isAuthenticated, loading } = useAuth();

  if (loading) {
    return null;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (!hasRole(allow)) {
    return <NotAuthorized requiredRoles={allow} />;
  }

  return children;
};
