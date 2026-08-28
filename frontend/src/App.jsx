import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import { ProtectedRoute } from './auth/ProtectedRoute';
import { RoleRoute } from './auth/RoleRoute';

// Components
import NavBar from './components/NavBar';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import Dashboard from './pages/Dashboard';
import Findings from './pages/Findings';
import FindingDetail from './pages/FindingDetail';
import ScanHistory from './pages/ScanHistory';
import NotAuthorized from './pages/NotAuthorized';
import UserManagement from './pages/admin/UserManagement';

const AppLayout = ({ children }) => {
  return (
    <div className="app-container">
      <NavBar />
      {children}
    </div>
  );
};

const App = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public Auth Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/not-authorized" element={<AppLayout><NotAuthorized /></AppLayout>} />

          {/* Protected Routes (All Authenticated Users) */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AppLayout>
                  <Dashboard />
                </AppLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/findings"
            element={
              <ProtectedRoute>
                <AppLayout>
                  <Findings />
                </AppLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/findings/:id"
            element={
              <ProtectedRoute>
                <AppLayout>
                  <FindingDetail />
                </AppLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/history"
            element={
              <ProtectedRoute>
                <AppLayout>
                  <ScanHistory />
                </AppLayout>
              </ProtectedRoute>
            }
          />

          {/* Admin-Only Routes */}
          <Route
            path="/admin/users"
            element={
              <RoleRoute allow={['admin']}>
                <AppLayout>
                  <UserManagement />
                </AppLayout>
              </RoleRoute>
            }
          />

          {/* Catch-all Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
