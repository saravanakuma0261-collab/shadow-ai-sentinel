import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldX, ArrowLeft, Lock } from 'lucide-react';
import { useAuth } from '../auth/AuthContext';

const NotAuthorized = ({ requiredRoles = ['admin'] }) => {
  const { role } = useAuth();

  return (
    <div className="main-content" style={{ display: 'flex', minHeight: '65vh', alignItems: 'center', justifyContent: 'center' }}>
      <div className="glass-card" style={{ maxWidth: '520px', width: '100%', padding: '2.5rem', textAlign: 'center' }}>
        <div style={{
          display: 'inline-flex',
          padding: '1.25rem',
          borderRadius: '50%',
          background: 'rgba(239, 68, 68, 0.15)',
          color: 'var(--risk-critical)',
          boxShadow: '0 0 25px var(--risk-critical-glow)',
          marginBottom: '1.25rem'
        }}>
          <ShieldX size={48} />
        </div>

        <h1 style={{ fontSize: '1.6rem', fontWeight: 800, marginBottom: '0.5rem', color: '#f8fafc' }}>
          403 Access Restricted
        </h1>
        
        <p className="subtitle" style={{ marginBottom: '1.5rem', lineHeight: '1.5' }}>
          Your current session role (<strong style={{ color: 'var(--primary)' }}>{role?.toUpperCase()}</strong>) does not have authorization to view this security resource or execute this administrative action.
        </p>

        <div style={{
          background: 'rgba(15, 23, 42, 0.6)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '0.85rem 1rem',
          fontSize: '0.8rem',
          color: 'var(--text-secondary)',
          marginBottom: '1.75rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '0.5rem'
        }}>
          <Lock size={14} style={{ color: 'var(--risk-high)' }} />
          <span>Required Privilege: <strong>{requiredRoles.join(' / ').toUpperCase()}</strong></span>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '0.75rem' }}>
          <Link to="/" className="btn btn-primary">
            <ArrowLeft size={16} />
            <span>Return to Dashboard</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotAuthorized;
