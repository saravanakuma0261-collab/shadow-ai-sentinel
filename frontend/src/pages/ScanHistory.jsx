import React, { useState, useEffect } from 'react';
import { History, Globe, Puzzle, Calendar, Activity, Layers, Sparkles, RefreshCw } from 'lucide-react';
import client from '../api/client';
import { useAuth } from '../auth/AuthContext';
import ScanModal from '../components/ScanModal';

const ScanHistory = () => {
  const { hasRole } = useAuth();
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isScanModalOpen, setIsScanModalOpen] = useState(false);

  const fetchScans = async () => {
    setLoading(true);
    try {
      const res = await client.get('/scans');
      setScans(res.data || []);
    } catch (err) {
      console.error('Failed to load scan history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchScans();
  }, []);

  const canRunScan = hasRole(['admin', 'analyst']);

  return (
    <div className="main-content">
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
        <div>
          <h1 className="title-hero">
            Ingestion & Telemetry <span className="title-gradient">Scan History</span>
          </h1>
          <p className="subtitle">
            Timeline of ingested network proxy logs and browser extension inventory audits
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <button
            onClick={fetchScans}
            className="btn btn-secondary"
            title="Refresh Scan History"
            disabled={loading}
          >
            <RefreshCw size={15} className={loading ? 'animate-spin' : ''} />
            <span>Refresh</span>
          </button>

          <button
            onClick={() => setIsScanModalOpen(true)}
            className="btn btn-primary"
          >
            <Sparkles size={16} />
            <span>Launch Scan</span>
          </button>
        </div>
      </div>

      {/* Scans Table */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <div className="table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Scan Name</th>
                <th>Type</th>
                <th>Events Ingested</th>
                <th>Shadow AI Findings</th>
                <th>Execution Time</th>
                <th>Triggered By</th>
              </tr>
            </thead>
            <tbody>
              {scans.length === 0 ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
                    <History size={36} style={{ opacity: 0.4, marginBottom: '0.75rem', display: 'block', margin: '0 auto' }} />
                    <p style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>No telemetry scans found.</p>
                    <p style={{ fontSize: '0.8rem', marginTop: '0.25rem' }}>Execute your first proxy DNS or extension scan to begin detection.</p>
                  </td>
                </tr>
              ) : (
                scans.map((scan) => (
                  <tr key={scan.id}>
                    <td>
                      <div style={{ fontWeight: 700, color: '#f8fafc' }}>
                        {scan.name || `Scan #${scan.id}`}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                        ID: {scan.id}
                      </div>
                    </td>

                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem' }}>
                        {scan.scan_type === 'extension' ? (
                          <>
                            <Puzzle size={15} style={{ color: 'var(--accent-purple)' }} />
                            <span>Browser Extension</span>
                          </>
                        ) : (
                          <>
                            <Globe size={15} style={{ color: 'var(--primary)' }} />
                            <span>DNS / Proxy Log</span>
                          </>
                        )}
                      </div>
                    </td>

                    <td>
                      <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                        {scan.total_events ? scan.total_events.toLocaleString() : 0}
                      </span>
                    </td>

                    <td>
                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.35rem',
                        background: scan.findings_count > 0 ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                        color: scan.findings_count > 0 ? 'var(--risk-critical)' : 'var(--accent-emerald)',
                        padding: '0.2rem 0.6rem',
                        borderRadius: 'var(--radius-full)',
                        fontSize: '0.8rem',
                        fontWeight: 700
                      }}>
                        <Layers size={13} />
                        {scan.findings_count || 0} Identified
                      </span>
                    </td>

                    <td>
                      <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                        {scan.created_at ? new Date(scan.created_at).toLocaleString() : 'N/A'}
                      </div>
                    </td>

                    <td>
                      <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                        {scan.user_id ? `User #${scan.user_id}` : 'SecOps Admin'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Ingestion Modal */}
      <ScanModal
        isOpen={isScanModalOpen}
        onClose={() => setIsScanModalOpen(false)}
        onScanComplete={() => {
          fetchScans();
        }}
      />
    </div>
  );
};

export default ScanHistory;
