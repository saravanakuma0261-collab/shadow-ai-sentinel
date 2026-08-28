import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { 
  Shield, 
  LayoutDashboard, 
  Layers, 
  History, 
  Users, 
  LogOut, 
  Sparkles
} from 'lucide-react';
import ScanModal from './ScanModal';

const NavBar = () => {
  const { user, role, logout, hasRole } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [isScanModalOpen, setIsScanModalOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <header style={{
      background: 'rgba(8, 12, 20, 0.85)',
      backdropFilter: 'blur(16px)',
      borderBottom: '1px solid var(--border-subtle)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <div style={{
        maxWidth: '1380px',
        margin: '0 auto',
        padding: '0.85rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        {/* Brand Logo */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', textDecoration: 'none' }}>
          <div style={{
            background: 'linear-gradient(135deg, #0284c7, #38bdf8)',
            color: '#0f172a',
            padding: '0.5rem',
            borderRadius: 'var(--radius-md)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 15px var(--primary-glow)'
          }}>
            <Shield size={22} strokeWidth={2.5} />
          </div>
          <div>
            <div style={{ fontWeight: 800, fontSize: '1.15rem', letterSpacing: '-0.02em', color: '#f8fafc' }}>
              SHADOW AI <span className="title-gradient">SENTINEL</span>
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              Traceforce Enterprise Defense
            </div>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Link
            to="/"
            className={`btn btn-sm ${isActive('/') ? 'btn-primary' : 'btn-secondary'}`}
            style={{ textDecoration: 'none' }}
          >
            <LayoutDashboard size={16} />
            <span>Dashboard</span>
          </Link>

          <Link
            to="/findings"
            className={`btn btn-sm ${isActive('/findings') ? 'btn-primary' : 'btn-secondary'}`}
            style={{ textDecoration: 'none' }}
          >
            <Layers size={16} />
            <span>Findings</span>
          </Link>

          <Link
            to="/history"
            className={`btn btn-sm ${isActive('/history') ? 'btn-primary' : 'btn-secondary'}`}
            style={{ textDecoration: 'none' }}
          >
            <History size={16} />
            <span>Scan History</span>
          </Link>

          {/* Admin-Only User Management Link */}
          {hasRole('admin') && (
            <Link
              to="/admin/users"
              className={`btn btn-sm ${isActive('/admin/users') ? 'btn-primary' : 'btn-secondary'}`}
              style={{
                textDecoration: 'none',
                borderColor: isActive('/admin/users') ? 'transparent' : 'rgba(168, 85, 247, 0.4)',
                color: isActive('/admin/users') ? '#0f172a' : '#c084fc'
              }}
            >
              <Users size={16} />
              <span>User Management</span>
            </Link>
          )}

          {/* Persistent Scan Trigger Button */}
          <button
            onClick={() => setIsScanModalOpen(true)}
            className="btn btn-primary btn-sm"
            style={{ marginLeft: '0.5rem', background: 'linear-gradient(135deg, #0284c7, #38bdf8)', color: '#0f172a', fontWeight: 700 }}
          >
            <Sparkles size={14} />
            <span>Launch Scan</span>
          </button>
        </nav>

        {/* User Badge & Logout */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', textAlign: 'right' }}>
            <div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f8fafc' }}>
                {user?.name || user?.email}
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '2px' }}>
                <span className={`badge-role badge-role-${(role || 'viewer').toLowerCase()}`}>
                  {role?.toUpperCase()}
                </span>
              </div>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="btn btn-secondary btn-sm"
            title="Sign Out"
            style={{ padding: '0.5rem', color: '#94a3b8' }}
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>

      {/* Global Ingestion / Scan Modal */}
      <ScanModal
        isOpen={isScanModalOpen}
        onClose={() => setIsScanModalOpen(false)}
        onScanComplete={() => {
          if (location.pathname === '/' || location.pathname === '/history' || location.pathname === '/findings') {
            window.location.reload();
          }
        }}
      />
    </header>
  );
};

export default NavBar;
