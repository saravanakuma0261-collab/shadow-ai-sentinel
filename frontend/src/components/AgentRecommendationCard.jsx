import React from 'react';
import { 
  Sparkles, 
  ShieldAlert, 
  CheckCircle, 
  Eye, 
  AlertOctagon, 
  Clock, 
  Cpu, 
  ListChecks, 
  FileText,
  Activity
} from 'lucide-react';

const AgentRecommendationCard = ({ investigation = null, loading = false, onReinvestigate = null, canTrigger = false }) => {
  if (loading) {
    return (
      <div className="glass-card" style={{ padding: '2rem', textAlign: 'center' }}>
        <div style={{
          display: 'inline-flex',
          padding: '1rem',
          borderRadius: '50%',
          background: 'rgba(56, 189, 248, 0.1)',
          color: 'var(--primary)',
          marginBottom: '1rem',
          boxShadow: '0 0 25px var(--primary-glow)'
        }}>
          <Sparkles size={32} className="animate-pulse-glow" />
        </div>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.5rem' }}>
          Autonomous LLM Triage in Progress...
        </h3>
        <p className="subtitle" style={{ maxWidth: '500px', margin: '0 auto 1.5rem auto' }}>
          Our AI security analyst agent is synthesizing finding context, permissions, organizational exposure, and compliance policies.
        </p>
        <div style={{
          height: '6px',
          background: 'rgba(255, 255, 255, 0.08)',
          borderRadius: 'var(--radius-full)',
          overflow: 'hidden',
          maxWidth: '400px',
          margin: '0 auto'
        }}>
          <div style={{
            height: '100%',
            width: '60%',
            background: 'linear-gradient(90deg, #0284c7, #38bdf8, #a855f7)',
            borderRadius: 'var(--radius-full)',
            animation: 'pulseGlow 1.5s infinite'
          }} />
        </div>
      </div>
    );
  }

  if (!investigation) {
    return (
      <div className="glass-card" style={{ padding: '2rem', textAlign: 'center' }}>
        <div style={{
          display: 'inline-flex',
          padding: '1rem',
          borderRadius: '50%',
          background: 'rgba(255, 255, 255, 0.04)',
          color: 'var(--text-muted)',
          marginBottom: '1rem'
        }}>
          <BotIcon size={32} />
        </div>
        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.4rem' }}>
          No LLM Triage Report Yet
        </h3>
        <p className="subtitle" style={{ maxWidth: '480px', margin: '0 auto 1.5rem auto' }}>
          Run an on-demand deep-dive triage report with our AI Security Investigator to receive tailored remediation steps and policy analysis.
        </p>
        {canTrigger && onReinvestigate && (
          <button
            onClick={onReinvestigate}
            className="btn btn-primary"
          >
            <Sparkles size={16} />
            <span>Launch LLM Investigation</span>
          </button>
        )}
      </div>
    );
  }

  const rec = (investigation.recommendation || 'MONITOR').toUpperCase();

  const getActionTheme = () => {
    switch (rec) {
      case 'BLOCK':
        return {
          color: 'var(--risk-critical)',
          bg: 'var(--risk-critical-bg)',
          glow: 'var(--risk-critical-glow)',
          icon: AlertOctagon,
          title: 'Immediate Block Recommended'
        };
      case 'ESCALATE':
        return {
          color: 'var(--risk-high)',
          bg: 'var(--risk-high-bg)',
          glow: 'var(--risk-high-glow)',
          icon: ShieldAlert,
          title: 'Escalate to SecOps / CISO'
        };
      case 'APPROVE':
        return {
          color: 'var(--accent-emerald)',
          bg: 'rgba(16, 185, 129, 0.15)',
          glow: 'rgba(16, 185, 129, 0.35)',
          icon: CheckCircle,
          title: 'Safe for Organizational Approval'
        };
      default:
        return {
          color: 'var(--risk-medium)',
          bg: 'var(--risk-medium-bg)',
          glow: 'var(--risk-medium-glow)',
          icon: Eye,
          title: 'Active Monitoring & DLP Policy'
        };
    }
  };

  const theme = getActionTheme();
  const Icon = theme.icon;
  const confidence = Math.round(investigation.confidence_score ? investigation.confidence_score * 100 : 85);

  return (
    <div className="glass-card" style={{ padding: '1.75rem', position: 'relative', overflow: 'hidden' }}>
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            background: 'linear-gradient(135deg, rgba(56, 189, 248, 0.2), rgba(168, 85, 247, 0.2))',
            border: '1px solid rgba(56, 189, 248, 0.4)',
            color: 'var(--primary)',
            padding: '0.65rem',
            borderRadius: 'var(--radius-md)',
            boxShadow: '0 0 15px var(--primary-glow)'
          }}>
            <Sparkles size={22} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800 }}>LLM Security Agent Triage</h3>
              <span className="badge" style={{ background: 'rgba(56, 189, 248, 0.15)', color: 'var(--primary)', border: '1px solid var(--border-active)' }}>
                {investigation.model_used || 'Claude 3.5 Sonnet'}
              </span>
            </div>
            <p className="subtitle" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Clock size={13} />
              Generated {investigation.created_at ? new Date(investigation.created_at).toLocaleString() : 'Just now'}
            </p>
          </div>
        </div>

        {canTrigger && onReinvestigate && (
          <button
            onClick={onReinvestigate}
            className="btn btn-secondary btn-sm"
          >
            <Sparkles size={14} />
            <span>Re-evaluate Finding</span>
          </button>
        )}
      </div>

      {/* Decision Banner */}
      <div style={{
        background: theme.bg,
        border: `1px solid ${theme.color}`,
        boxShadow: `0 0 20px ${theme.glow}`,
        borderRadius: 'var(--radius-md)',
        padding: '1.25rem',
        marginBottom: '1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div style={{ color: theme.color }}>
            <Icon size={28} />
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-secondary)' }}>
              Agent Triage Verdict
            </div>
            <div style={{ fontSize: '1.35rem', fontWeight: 800, color: '#f8fafc' }}>
              {rec}: {theme.title}
            </div>
          </div>
        </div>

        {/* Confidence Meter */}
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
            Model Confidence
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{
              width: '100px',
              height: '8px',
              background: 'rgba(0, 0, 0, 0.4)',
              borderRadius: 'var(--radius-full)',
              overflow: 'hidden'
            }}>
              <div style={{
                height: '100%',
                width: `${confidence}%`,
                background: theme.color
              }} />
            </div>
            <span style={{ fontWeight: 800, fontFamily: 'var(--font-mono)', color: theme.color }}>{confidence}%</span>
          </div>
        </div>
      </div>

      {/* Rationale Section */}
      <div style={{ marginBottom: '1.5rem' }}>
        <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <FileText size={16} style={{ color: 'var(--primary)' }} />
          Investigative Rationale & Context Analysis
        </h4>
        <div style={{
          background: 'rgba(15, 23, 42, 0.6)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '1.25rem',
          fontSize: '0.95rem',
          lineHeight: '1.6',
          color: '#e2e8f0',
          whiteSpace: 'pre-line'
        }}>
          {investigation.rationale || 'No detailed rationale provided.'}
        </div>
      </div>

      {/* Suggested Remediation Steps */}
      {investigation.suggested_actions && investigation.suggested_actions.length > 0 && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '0.65rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <ListChecks size={16} style={{ color: 'var(--accent-emerald)' }} />
            Prescribed SecOps Remediation Actions
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {investigation.suggested_actions.map((action, idx) => (
              <div
                key={idx}
                style={{
                  background: 'rgba(15, 23, 42, 0.4)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '0.85rem 1rem',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.65rem'
                }}
              >
                <div style={{
                  color: 'var(--primary)',
                  fontWeight: 700,
                  fontSize: '0.8rem',
                  fontFamily: 'var(--font-mono)',
                  marginTop: '1px'
                }}>
                  0{idx + 1}
                </div>
                <div style={{ fontSize: '0.9rem', color: '#cbd5e1' }}>
                  {typeof action === 'string' ? action : action.description || JSON.stringify(action)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const BotIcon = ({ size = 24 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="11" width="18" height="10" rx="2" />
    <circle cx="12" cy="5" r="2" />
    <path d="M12 7v4" />
    <line x1="8" y1="16" x2="8.01" y2="16" />
    <line x1="16" y1="16" x2="16.01" y2="16" />
  </svg>
);

export default AgentRecommendationCard;
