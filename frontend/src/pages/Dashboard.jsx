import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  ShieldAlert, 
  Layers, 
  Activity, 
  Sparkles, 
  TrendingUp, 
  Globe, 
  Puzzle, 
  Lock, 
  ArrowRight,
  RefreshCw,
  Clock,
  ExternalLink,
  ShieldCheck,
  AlertTriangle
} from 'lucide-react';
import client from '../api/client';
import { useAuth } from '../auth/AuthContext';
import RiskDistributionChart from '../components/RiskDistributionChart';
import RiskBadge from '../components/RiskBadge';
import ScanModal from '../components/ScanModal';

const Dashboard = () => {
  const { role, hasRole } = useAuth();
  const [findings, setFindings] = useState([]);
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isScanModalOpen, setIsScanModalOpen] = useState(false);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [findingsRes, scansRes] = await Promise.all([
        client.get('/findings'),
        client.get('/scans')
      ]);
      setFindings(findingsRes.data || []);
      setScans(scansRes.data || []);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Compute metrics
  const totalFindings = findings.length;
  const criticalCount = findings.filter(f => (f.risk_tier || '').toUpperCase() === 'CRITICAL').length;
  const highCount = findings.filter(f => (f.risk_tier || '').toUpperCase() === 'HIGH').length;
  const mediumCount = findings.filter(f => (f.risk_tier || '').toUpperCase() === 'MEDIUM').length;
  const lowCount = findings.filter(f => (f.risk_tier || '').toUpperCase() === 'LOW').length;

  const unsanctionedCount = findings.filter(f => (f.sanction_status || '').toLowerCase() === 'unsanctioned').length;
  const unsanctionedPct = totalFindings > 0 ? Math.round((unsanctionedCount / totalFindings) * 100) : 0;

  const totalEventsScanned = scans.reduce((acc, s) => acc + (s.total_events || 0), 0);

  // Top 5 Highest Risk Shadow AI Services
  const topRisks = [...findings]
    .sort((a, b) => (b.risk_score || 0) - (a.risk_score || 0))
    .slice(0, 5);

  const canRunScan = hasRole(['admin', 'analyst']);

  return (
    <div className="main-content">
      {/* Dashboard Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <h1 className="title-hero">
              Threat & Exposure <span className="title-gradient">Command Center</span>
            </h1>
          </div>
          <p className="subtitle">
            AI-Safe Data Loss Prevention (DLP) & Credential Protection: Empowering AI productivity while preventing passwords, secrets, and sensitive enterprise data leakage.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <button
            onClick={fetchDashboardData}
            className="btn btn-secondary"
            title="Refresh Metrics"
            disabled={loading}
          >
            <RefreshCw size={15} className={loading ? 'animate-spin' : ''} />
            <span>Sync</span>
          </button>

          <button
            onClick={() => setIsScanModalOpen(true)}
            className="btn btn-primary"
            style={{ fontWeight: 600 }}
          >
            <Sparkles size={16} />
            <span>Launch New Scan</span>
          </button>
        </div>
      </div>

      {/* KPI Metrics Grid */}
      <div className="metrics-grid">
        {/* Metric 1: Total Shadow AI Identified */}
        <div className="glass-card metric-card">
          <div className="metric-title">
            <span>Identified Shadow AI</span>
            <Layers size={18} style={{ color: 'var(--primary)' }} />
          </div>
          <div className="metric-value" style={{ color: '#f8fafc' }}>
            {loading ? '...' : totalFindings}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Across {scans.length} completed telemetry scans
          </div>
        </div>

        {/* Metric 2: Critical / High Exposure */}
        <div className="glass-card metric-card" style={{ borderColor: criticalCount > 0 ? 'rgba(239, 68, 68, 0.35)' : 'var(--border-subtle)' }}>
          <div className="metric-title">
            <span>Critical & High Risk</span>
            <ShieldAlert size={18} style={{ color: 'var(--risk-critical)' }} />
          </div>
          <div className="metric-value" style={{ color: 'var(--risk-critical)' }}>
            {loading ? '...' : criticalCount + highCount}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#fca5a5' }}>
            {criticalCount} Critical, {highCount} High urgency
          </div>
        </div>

        {/* Metric 3: Unsanctioned Ratio */}
        <div className="glass-card metric-card">
          <div className="metric-title">
            <span>Unsanctioned AI Ratio</span>
            <Lock size={18} style={{ color: 'var(--risk-high)' }} />
          </div>
          <div className="metric-value" style={{ color: 'var(--risk-high)' }}>
            {loading ? '...' : `${unsanctionedPct}%`}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {unsanctionedCount} of {totalFindings} entities unapproved
          </div>
        </div>

        {/* Metric 4: Scanned Events */}
        <div className="glass-card metric-card">
          <div className="metric-title">
            <span>Events Processed</span>
            <Activity size={18} style={{ color: 'var(--accent-emerald)' }} />
          </div>
          <div className="metric-value" style={{ color: 'var(--accent-emerald)' }}>
            {loading ? '...' : totalEventsScanned.toLocaleString()}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Proxy DNS logs & extensions audits
          </div>
        </div>
      </div>

      {/* Risk Distribution Chart */}
      <RiskDistributionChart
        distribution={{
          critical: criticalCount,
          high: highCount,
          medium: mediumCount,
          low: lowCount
        }}
      />

      {/* Two Column Layout: Top Risk Findings & Recent Scans */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        {/* Top Risks Card */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Priority Shadow AI Threats</h3>
              <p className="subtitle">Highest weighted risk entities requiring immediate SecOps review</p>
            </div>
            <Link to="/findings" className="btn btn-secondary btn-sm" style={{ textDecoration: 'none' }}>
              <span>View All</span>
              <ArrowRight size={13} />
            </Link>
          </div>

          {topRisks.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--text-muted)' }}>
              <ShieldCheck size={32} style={{ opacity: 0.4, margin: '0 auto 0.5rem auto' }} />
              <p>No active shadow AI findings recorded.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {topRisks.map((item) => (
                <Link
                  to={`/findings/${item.id}`}
                  key={item.id}
                  style={{
                    background: 'rgba(15, 23, 42, 0.6)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                    padding: '0.85rem 1rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    textDecoration: 'none',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.borderColor = 'var(--border-active)'}
                  onMouseLeave={(e) => e.currentTarget.style.borderColor = 'var(--border-subtle)'}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <RiskBadge tier={item.risk_tier} score={Math.round(item.risk_score)} showIcon={false} />
                    <div>
                      <div style={{ fontWeight: 700, color: '#f8fafc', fontSize: '0.9rem' }}>
                        {item.service_name}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                        {item.entity_identifier}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                      {item.category}
                    </span>
                    <ExternalLink size={14} style={{ color: 'var(--text-muted)' }} />
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Recent Scans Timeline */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Telemetry Ingestion History</h3>
              <p className="subtitle">Audit logs ingested and analyzed by the engine</p>
            </div>
            <Link to="/history" className="btn btn-secondary btn-sm" style={{ textDecoration: 'none' }}>
              <span>History</span>
              <ArrowRight size={13} />
            </Link>
          </div>

          {scans.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--text-muted)' }}>
              <Clock size={32} style={{ opacity: 0.4, margin: '0 auto 0.5rem auto' }} />
              <p>No scans performed yet.</p>
              <button
                onClick={() => setIsScanModalOpen(true)}
                className="btn btn-primary btn-sm"
                style={{ marginTop: '0.75rem' }}
              >
                Execute First Scan
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {scans.slice(0, 5).map((scan) => (
                <div
                  key={scan.id}
                  style={{
                    background: 'rgba(15, 23, 42, 0.4)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                    padding: '0.85rem 1rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{
                      padding: '0.4rem',
                      borderRadius: 'var(--radius-sm)',
                      background: 'rgba(255, 255, 255, 0.05)',
                      color: scan.scan_type === 'extension' ? 'var(--accent-purple)' : 'var(--primary)'
                    }}>
                      {scan.scan_type === 'extension' ? <Puzzle size={16} /> : <Globe size={16} />}
                    </div>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: '0.85rem', color: '#f8fafc' }}>
                        {scan.name || `Scan #${scan.id}`}
                      </div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                        {new Date(scan.created_at).toLocaleString()}
                      </div>
                    </div>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--primary)' }}>
                      {scan.findings_count || 0} findings
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                      {scan.total_events || 0} events
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Scan Modal */}
      <ScanModal
        isOpen={isScanModalOpen}
        onClose={() => setIsScanModalOpen(false)}
        onScanComplete={() => {
          fetchDashboardData();
        }}
      />
    </div>
  );
};

export default Dashboard;
