import React from 'react';
import { ShieldAlert, AlertTriangle, AlertCircle, ShieldCheck } from 'lucide-react';

const RiskBadge = ({ tier = 'low', score = null, showIcon = true, size = 'normal' }) => {
  const normalized = (tier || 'low').toLowerCase();

  const getIcon = () => {
    switch (normalized) {
      case 'critical':
        return <ShieldAlert size={14} />;
      case 'high':
        return <AlertTriangle size={14} />;
      case 'medium':
        return <AlertCircle size={14} />;
      default:
        return <ShieldCheck size={14} />;
    }
  };

  return (
    <span className={`badge badge-${normalized} ${size === 'lg' ? 'text-base py-1 px-3' : ''}`}>
      {showIcon && getIcon()}
      <span>{normalized.toUpperCase()}</span>
      {score !== null && <span style={{ opacity: 0.8, marginLeft: '2px' }}>({score})</span>}
    </span>
  );
};

export default RiskBadge;
