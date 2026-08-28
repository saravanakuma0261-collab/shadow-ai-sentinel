import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Shield, Mail, ArrowRight, ArrowLeft, CheckCircle2, AlertCircle } from 'lucide-react';
import client from '../api/client';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [resetData, setResetData] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await client.post('/auth/forgot-password', { email });
      setResetData(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process password reset request.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem 1rem',
      background: 'radial-gradient(ellipse at top, rgba(56, 189, 248, 0.1), transparent 70%)'
    }}>
      <div style={{ width: '100%', maxWidth: '440px' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div style={{
            display: 'inline-flex',
            padding: '0.85rem',
            borderRadius: 'var(--radius-lg)',
            background: 'linear-gradient(135deg, #0284c7, #38bdf8)',
            color: '#0f172a',
            boxShadow: '0 0 25px var(--primary-glow)',
            marginBottom: '1rem'
          }}>
            <Shield size={32} strokeWidth={2.5} />
          </div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>
            Reset <span className="title-gradient">Password</span>
          </h1>
          <p className="subtitle">We will generate a secure reset token</p>
        </div>

        <div className="glass-card" style={{ padding: '2rem' }}>
          {resetData ? (
            <div>
              <div style={{
                textAlign: 'center',
                padding: '1rem 0',
                color: 'var(--accent-emerald)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '0.75rem'
              }}>
                <CheckCircle2 size={40} />
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f8fafc' }}>
                  Reset Token Generated
                </h3>
                <p className="subtitle" style={{ fontSize: '0.85rem' }}>
                  {resetData.message || 'Check your inbox for the reset link.'}
                </p>
              </div>

              {/* Dev token convenience box */}
              {resetData.dev_reset_token && (
                <div style={{
                  marginTop: '1rem',
                  background: 'rgba(56, 189, 248, 0.1)',
                  border: '1px dashed var(--border-active)',
                  borderRadius: 'var(--radius-md)',
                  padding: '1rem',
                  fontSize: '0.8rem'
                }}>
                  <div style={{ fontWeight: 700, color: 'var(--primary)', marginBottom: '0.35rem' }}>
                    Local Development Mock Token:
                  </div>
                  <div style={{
                    fontFamily: 'var(--font-mono)',
                    wordBreak: 'break-all',
                    background: 'rgba(0, 0, 0, 0.4)',
                    padding: '0.5rem',
                    borderRadius: 'var(--radius-sm)',
                    color: '#e2e8f0',
                    userSelect: 'all'
                  }}>
                    {resetData.dev_reset_token}
                  </div>
                  <Link
                    to={`/reset-password?token=${resetData.dev_reset_token}`}
                    className="btn btn-primary btn-sm"
                    style={{ width: '100%', marginTop: '0.75rem', textDecoration: 'none' }}
                  >
                    Proceed with this Token
                  </Link>
                </div>
              )}

              <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
                <Link to="/login" className="btn btn-secondary" style={{ width: '100%' }}>
                  Back to Login
                </Link>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              {error && (
                <div style={{
                  background: 'rgba(239, 68, 68, 0.15)',
                  border: '1px solid rgba(239, 68, 68, 0.4)',
                  borderRadius: 'var(--radius-md)',
                  padding: '0.85rem 1rem',
                  color: '#fca5a5',
                  fontSize: '0.85rem',
                  marginBottom: '1.25rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}>
                  <AlertCircle size={16} />
                  <span>{error}</span>
                </div>
              )}

              <div className="form-group">
                <label className="form-label">Registered Work Email</label>
                <div style={{ position: 'relative' }}>
                  <Mail size={16} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                  <input
                    type="email"
                    required
                    className="form-input"
                    style={{ paddingLeft: '2.5rem' }}
                    placeholder="analyst@enterprise.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
              </div>

              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
                style={{ width: '100%', marginTop: '0.5rem' }}
              >
                {loading ? 'Sending Request...' : 'Generate Reset Token'}
                <ArrowRight size={16} />
              </button>

              <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
                <Link to="/login" style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
                  <ArrowLeft size={14} /> Back to Sign In
                </Link>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
