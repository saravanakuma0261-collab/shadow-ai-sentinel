import React, { useState, useEffect } from 'react';
import { 
  Users, 
  UserCheck, 
  UserX, 
  Shield, 
  AlertCircle, 
  CheckCircle2, 
  RefreshCw, 
  Mail, 
  Calendar,
  Lock,
  ChevronDown
} from 'lucide-react';
import client from '../../api/client';
import { useAuth } from '../../auth/AuthContext';

const UserManagement = () => {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await client.get('/admin/users');
      setUsers(res.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load user list.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleRoleChange = async (userId, newRole) => {
    setActionLoading(userId);
    setMessage(null);
    setError(null);
    try {
      await client.patch(`/admin/users/${userId}/role`, { role: newRole });
      setUsers(users.map(u => u.id === userId ? { ...u, role: newRole } : u));
      setMessage(`User role updated to ${newRole.toUpperCase()} successfully.`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update user role.');
    } finally {
      setActionLoading(null);
    }
  };

  const handleToggleStatus = async (userId, currentStatus) => {
    setActionLoading(userId);
    setMessage(null);
    setError(null);
    const newStatus = !currentStatus;
    try {
      await client.patch(`/admin/users/${userId}/status`, { is_active: newStatus });
      setUsers(users.map(u => u.id === userId ? { ...u, is_active: newStatus } : u));
      setMessage(`User account ${newStatus ? 'activated' : 'deactivated'} successfully.`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update user status.');
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="main-content">
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span className="badge badge-role badge-role-admin" style={{ fontSize: '0.75rem' }}>ADMIN ONLY</span>
          </div>
          <h1 className="title-hero" style={{ marginTop: '0.25rem' }}>
            SecOps User & <span className="title-gradient">Access Control</span>
          </h1>
          <p className="subtitle">
            Manage organization members, assign role-based access privileges (Admin, Analyst, Viewer)
          </p>
        </div>

        <button
          onClick={fetchUsers}
          className="btn btn-secondary"
          title="Refresh User List"
          disabled={loading}
        >
          <RefreshCw size={15} className={loading ? 'animate-spin' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Feedback Alerts */}
      {message && (
        <div style={{
          background: 'rgba(16, 185, 129, 0.15)',
          border: '1px solid rgba(16, 185, 129, 0.4)',
          borderRadius: 'var(--radius-md)',
          padding: '0.85rem 1rem',
          color: '#a7f3d0',
          fontSize: '0.85rem',
          marginBottom: '1.5rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <CheckCircle2 size={16} />
          <span>{message}</span>
        </div>
      )}

      {error && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.15)',
          border: '1px solid rgba(239, 68, 68, 0.4)',
          borderRadius: 'var(--radius-md)',
          padding: '0.85rem 1rem',
          color: '#fca5a5',
          fontSize: '0.85rem',
          marginBottom: '1.5rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* Users Table */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <div className="table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>User / Identity</th>
                <th>Assigned Role</th>
                <th>Account Status</th>
                <th>Registered Date</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.length === 0 ? (
                <tr>
                  <td colSpan="5" style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
                    <Users size={36} style={{ opacity: 0.4, margin: '0 auto 0.75rem auto', display: 'block' }} />
                    <p style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>No registered users found.</p>
                  </td>
                </tr>
              ) : (
                users.map((u) => {
                  const isSelf = currentUser?.email === u.email || currentUser?.id === u.id;
                  return (
                    <tr key={u.id}>
                      {/* Name & Email */}
                      <td>
                        <div style={{ fontWeight: 700, color: '#f8fafc' }}>
                          {u.name || 'Unnamed Analyst'} {isSelf && <span style={{ color: 'var(--primary)', fontSize: '0.75rem' }}>(You)</span>}
                        </div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                          <Mail size={13} /> {u.email}
                        </div>
                      </td>

                      {/* Role Selector */}
                      <td>
                        <select
                          className="form-select"
                          style={{
                            width: 'auto',
                            padding: '0.4rem 0.75rem',
                            fontSize: '0.8rem',
                            fontFamily: 'var(--font-mono)',
                            fontWeight: 600
                          }}
                          value={u.role || 'viewer'}
                          disabled={actionLoading === u.id || isSelf}
                          onChange={(e) => handleRoleChange(u.id, e.target.value)}
                        >
                          <option value="admin">ADMIN (Full Control)</option>
                          <option value="analyst">ANALYST (Scan & Triage)</option>
                          <option value="viewer">VIEWER (Read Only)</option>
                        </select>
                      </td>

                      {/* Status */}
                      <td>
                        {u.is_active ? (
                          <span style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.35rem',
                            color: 'var(--accent-emerald)',
                            fontSize: '0.8rem',
                            fontWeight: 600
                          }}>
                            <UserCheck size={15} /> Active
                          </span>
                        ) : (
                          <span style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.35rem',
                            color: 'var(--risk-critical)',
                            fontSize: '0.8rem',
                            fontWeight: 600
                          }}>
                            <UserX size={15} /> Deactivated
                          </span>
                        )}
                      </td>

                      {/* Created At */}
                      <td>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                          <Calendar size={13} />
                          {u.created_at ? new Date(u.created_at).toLocaleDateString() : 'N/A'}
                        </div>
                      </td>

                      {/* Toggle Active Button */}
                      <td style={{ textAlign: 'right' }}>
                        {!isSelf && (
                          <button
                            onClick={() => handleToggleStatus(u.id, u.is_active)}
                            disabled={actionLoading === u.id}
                            className={`btn btn-sm ${u.is_active ? 'btn-danger' : 'btn-secondary'}`}
                          >
                            {u.is_active ? 'Deactivate' : 'Activate'}
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default UserManagement;
