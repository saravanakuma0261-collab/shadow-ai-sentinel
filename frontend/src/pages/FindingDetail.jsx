import React, { useState, useEffect } from 'react';
import { useParams, Link, useSearchParams } from 'react-router-dom';
import { 
  ArrowLeft, 
  ShieldAlert, 
  Sparkles, 
  Globe, 
  Puzzle, 
  Bot, 
  User, 
  Calendar, 
  Activity, 
  Cpu, 
  HardDrive, 
  Info,
  CheckCircle,
  XCircle,
  HelpCircle,
  Sliders,
  Terminal,
  Lock,
  ChevronRight
} from 'lucide-react';
import client from '../api/client';
import { useAuth } from '../auth/AuthContext';
import RiskBadge from '../components/RiskBadge';
import AgentRecommendationCard from '../components/AgentRecommendationCard';

const FindingDetail = () => {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const { role, hasRole } = useAuth();

  const [finding, setFinding] = useState(null);
  const [investigation, setInvestigation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [agentLoading, setAgentLoading] = useState(false);
  const [error, setError] = useState(null);

  const canInvestigate = hasRole(['admin', 'analyst']);

  const fetchFindingData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await client.get(`/findings/${id}`);
      setFinding(res.data);
      if (res.data.investigation) {
        setInvestigation(res.data.investigation);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load finding details.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunAgent = async () => {
    setAgentLoading(true);
    try {
      const res = await client.post(`/findings/${id}/investigate`);
      setInvestigation(res.data);
      // Refresh finding to get updated state
      const updatedFinding = await client.get(`/findings/${id}`);
      setFinding(updatedFinding.data);
    } catch (err) {
      alert(err.response?.data?.detail || 'LLM Agent investigation failed.');
    } finally {
      setAgentLoading(false);
    }
  };

  useEffect(() => {
    fetchFindingData().then(() => {
      if (searchParams.get('auto_investigate') === '1' && canInvestigate) {
        handleRunAgent();
      }
    });
  }, [id]);

  if (loading) {
    return (
      <div className="main-content" style={{ display: 'flex', height: '60vh', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ color: 'var(--primary)', fontFamily: 'var(--font-mono)' }}>Loading threat telemetry...</div>
      </div>
    );
  }

  if (error || !finding) {
    return (
      <div className="main-content">
        <div className="glass-card" style={{ padding: '3rem', textAlign: 'center' }}>
          <ShieldAlert size={48} style={{ color: 'var(--risk-critical)', margin: '0 auto 1rem auto' }} />
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>Finding Not Found</h2>
          <p className="subtitle" style={{ marginBottom: '1.5rem' }}>{error || 'Unable to locate finding with specified ID.'}</p>
          <Link to="/findings" className="btn btn-secondary">
            <ArrowLeft size={16} />
            <span>Return to Findings Inventory</span>
          </Link>
        </div>
      </div>
    );
  }

  // Parse explanation breakdown
  const breakdown = finding.explanation_breakdown || {
    category_score: 50,
    sanction_score: 50,
    data_exposure_score: 50,
    usage_spread_score: 50,
    weights: { category: 0.35, sanction: 0.25, data_exposure: 0.25, usage_spread: 0.15 }
  };

  return (
    <div className="main-content">
      {/* Top Breadcrumb & Actions */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <Link to="/findings" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
          <ArrowLeft size={14} />
          <span>Back to Findings Inventory</span>
        </Link>

        {canInvestigate && (
          <button
            onClick={handleRunAgent}
            className="btn btn-primary btn-sm"
            disabled={agentLoading}
          >
            <Sparkles size={15} />
            <span>{investigation ? 'Re-run LLM Triage' : 'Execute LLM Agent Triage'}</span>
          </button>
        )}
      </div>

      {/* Main Title Banner */}
      <div className="glass-card" style={{ padding: '2rem', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1.5rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <h1 style={{ fontSize: '1.85rem', fontWeight: 800, color: '#f8fafc' }}>
                {finding.service_name || 'Unknown AI Entity'}
              </h1>
              <RiskBadge tier={finding.risk_tier} score={Math.round(finding.risk_score)} size="lg" />
            </div>

            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '1.25rem',
              color: 'var(--text-secondary)',
              fontSize: '0.85rem',
              flexWrap: 'wrap'
            }}>
              <span style={{ fontFamily: 'var(--font-mono)', background: 'rgba(255,255,255,0.06)', padding: '0.2rem 0.5rem', borderRadius: 'var(--radius-sm)' }}>
                {finding.entity_identifier}
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <User size={14} /> {finding.user_or_host || 'System / Network'}
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <Calendar size={14} /> {finding.first_seen ? new Date(finding.first_seen).toLocaleString() : 'N/A'}
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <Activity size={14} /> {finding.occurrence_count || 1} Occurrences
              </span>
            </div>
          </div>

          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Calculated Risk Score
            </div>
            <div style={{
              fontSize: '2.5rem',
              fontWeight: 900,
              fontFamily: 'var(--font-main)',
              color: finding.risk_tier === 'CRITICAL' ? 'var(--risk-critical)' :
                     finding.risk_tier === 'HIGH' ? 'var(--risk-high)' :
                     finding.risk_tier === 'MEDIUM' ? 'var(--risk-medium)' : 'var(--risk-low)'
            }}>
              {Math.round(finding.risk_score)}<span style={{ fontSize: '1.2rem', color: 'var(--text-muted)' }}>/100</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              Weighted Heuristic Formulation
            </div>
          </div>
        </div>
      </div>

      {/* Grid: 4-Signal Explainable Scoring & Technical Metadata */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        {/* Signal Breakdown Card */}
        <div className="glass-card" style={{ padding: '1.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
            <Sliders size={18} style={{ color: 'var(--primary)' }} />
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>AI-Assisted Explainable Risk Weights</h3>
          </div>
          <p className="subtitle" style={{ marginBottom: '1.5rem' }}>
            Transparent 4-dimensional score synthesis as defined in enterprise security governance
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {/* Signal 1: Category Sensitivity */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                <span style={{ fontWeight: 600 }}>1. Category Sensitivity (35% weight)</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--primary)' }}>
                  {breakdown.category_score || 0} / 100
                </span>
              </div>
              <div style={{ height: '8px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${breakdown.category_score || 0}%`, background: 'var(--primary)' }} />
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                Class: {finding.category || 'General AI'}
              </div>
            </div>

            {/* Signal 2: Sanction Status */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                <span style={{ fontWeight: 600 }}>2. Sanction & Governance Status (25% weight)</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--risk-high)' }}>
                  {breakdown.sanction_score || 0} / 100
                </span>
              </div>
              <div style={{ height: '8px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${breakdown.sanction_score || 0}%`, background: 'var(--risk-high)' }} />
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                Status: {finding.sanction_status}
              </div>
            </div>

            {/* Signal 3: Data Exposure */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                <span style={{ fontWeight: 600 }}>3. Data Exposure Potential (25% weight)</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--risk-critical)' }}>
                  {breakdown.data_exposure_score || 0} / 100
                </span>
              </div>
              <div style={{ height: '8px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${breakdown.data_exposure_score || 0}%`, background: 'var(--risk-critical)' }} />
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                Exposure Rating: {finding.data_exposure_risk || 'LOW'}
              </div>
            </div>

            {/* Signal 4: Usage Spread */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                <span style={{ fontWeight: 600 }}>4. Usage Spread & Traffic (15% weight)</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-emerald)' }}>
                  {breakdown.usage_spread_score || 0} / 100
                </span>
              </div>
              <div style={{ height: '8px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${breakdown.usage_spread_score || 0}%`, background: 'var(--accent-emerald)' }} />
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                Occurrences: {finding.occurrence_count || 1} hits
              </div>
            </div>
          </div>
        </div>

        {/* Technical Telemetry Metadata */}
        <div className="glass-card" style={{ padding: '1.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
            <Terminal size={18} style={{ color: 'var(--accent-cyan)' }} />
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Telemetry & Ingestion Attributes</h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem' }}>
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Asset Type</span>
              <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{finding.entity_type?.toUpperCase()}</span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem' }}>
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Detection Mechanism</span>
              <span style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--primary)' }}>
                {finding.fingerprint_matched ? 'Fingerprint DB Exact Match' : 'Unknown Entity Classifier'}
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.5rem' }}>
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Sanction Compliance</span>
              <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{finding.sanction_status}</span>
            </div>

            {/* Raw Metadata Details */}
            {finding.raw_metadata && (
              <div style={{ marginTop: '0.5rem' }}>
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', display: 'block', marginBottom: '0.4rem' }}>
                  Raw Extracted Metadata (Permissions / Logs):
                </span>
                <pre style={{
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid var(--border-subtle)',
                  padding: '0.75rem',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.75rem',
                  color: '#94a3b8',
                  overflowX: 'auto',
                  fontFamily: 'var(--font-mono)'
                }}>
                  {JSON.stringify(finding.raw_metadata, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* LLM Agent Investigation Section */}
      <AgentRecommendationCard
        investigation={investigation}
        loading={agentLoading}
        onReinvestigate={handleRunAgent}
        canTrigger={canInvestigate}
      />
    </div>
  );
};

export default FindingDetail;
