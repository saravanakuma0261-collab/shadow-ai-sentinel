import React from 'react';
import { ShieldAlert, AlertTriangle, AlertCircle, ShieldCheck } from 'lucide-react';

const RiskDistributionChart = ({ distribution = { critical: 0, high: 0, medium: 0, low: 0 } }) => {
  const { critical = 0, high = 0, medium = 0, low = 0 } = distribution;
  const total = critical + high + medium + low;

  const pct = (val) => (total > 0 ? ((val / total) * 100).toFixed(1) : 0);

  const tiers = [
    { label: 'Critical', count: critical, color: 'var(--risk-critical)', bg: 'var(--risk-critical-bg)', icon: ShieldAlert },
    { label: 'High', count: high, color: 'var(--risk-high)', bg: 'var(--risk-high-bg)', icon: AlertTriangle },
    { label: 'Medium', count: medium, color: 'var(--risk-medium)', bg: 'var(--risk-medium-bg)', icon: AlertCircle },
    { label: 'Low', count: low, color: 'var(--risk-low)', bg: 'var(--risk-low-bg)', icon: ShieldCheck },
  ];

  return (
    <div className="glass-card" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Risk Tier Distribution</h3>
          <p className="subtitle">Breakdown of active findings across 4 heuristic risk bands</p>
        </div>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
          Total Identified: <strong style={{ color: 'var(--text-primary)' }}>{total}</strong>
        </div>
      </div>

      {/* Segmented Distribution Bar */}
      <div style={{
        display: 'flex',
        height: '14px',
        borderRadius: 'var(--radius-full)',
        overflow: 'hidden',
        background: 'rgba(255, 255, 255, 0.05)',
        marginBottom: '1.5rem',
        border: '1px solid var(--border-subtle)'
      }}>
        {total === 0 ? (
          <div style={{ width: '100%', background: 'rgba(255, 255, 255, 0.1)' }} />
        ) : (
          <>
            {critical > 0 && <div style={{ width: `${pct(critical)}%`, background: 'var(--risk-critical)', transition: 'width 0.4s ease' }} title={`Critical: ${critical}`} />}
            {high > 0 && <div style={{ width: `${pct(high)}%`, background: 'var(--risk-high)', transition: 'width 0.4s ease' }} title={`High: ${high}`} />}
            {medium > 0 && <div style={{ width: `${pct(medium)}%`, background: 'var(--risk-medium)', transition: 'width 0.4s ease' }} title={`Medium: ${medium}`} />}
            {low > 0 && <div style={{ width: `${pct(low)}%`, background: 'var(--risk-low)', transition: 'width 0.4s ease' }} title={`Low: ${low}`} />}
          </>
        )}
      </div>

      {/* Grid of Tiers */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
        {tiers.map((t) => {
          const Icon = t.icon;
          return (
            <div
              key={t.label}
              style={{
                background: 'rgba(15, 23, 42, 0.5)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '1rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.85rem'
              }}
            >
              <div style={{
                color: t.color,
                background: t.bg,
                padding: '0.5rem',
                borderRadius: 'var(--radius-sm)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Icon size={20} />
              </div>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>
                  {t.label}
                </div>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color: t.color }}>
                  {t.count} <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 400 }}>({pct(t.count)}%)</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default RiskDistributionChart;
