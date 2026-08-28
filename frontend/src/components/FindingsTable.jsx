import React, { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { 
  Search, 
  Filter, 
  ArrowUpDown, 
  ExternalLink, 
  ShieldAlert, 
  Globe, 
  Puzzle, 
  Bot, 
  User, 
  HardDrive,
  CheckCircle2,
  XCircle,
  Clock,
  Sparkles
} from 'lucide-react';
import RiskBadge from './RiskBadge';

const FindingsTable = ({ findings = [], onInvestigate = null, userRole = 'viewer' }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTier, setSelectedTier] = useState('ALL');
  const [selectedType, setSelectedType] = useState('ALL');
  const [selectedSanction, setSelectedSanction] = useState('ALL');
  const [sortField, setSortField] = useState('risk_score');
  const [sortOrder, setSortOrder] = useState('desc'); // 'asc' or 'desc'

  const filteredFindings = useMemo(() => {
    return findings.filter((item) => {
      const matchSearch = 
        (item.service_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
        (item.entity_identifier || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
        (item.user_or_host || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
        (item.category || '').toLowerCase().includes(searchTerm.toLowerCase());

      const matchTier = selectedTier === 'ALL' || (item.risk_tier || '').toUpperCase() === selectedTier;
      const matchType = selectedType === 'ALL' || (item.entity_type || '').toUpperCase() === selectedType;
      const matchSanction = selectedSanction === 'ALL' || (item.sanction_status || '').toUpperCase() === selectedSanction;

      return matchSearch && matchTier && matchType && matchSanction;
    }).sort((a, b) => {
      let valA = a[sortField];
      let valB = b[sortField];

      if (sortField === 'risk_score') {
        valA = Number(valA || 0);
        valB = Number(valB || 0);
      } else {
        valA = String(valA || '').toLowerCase();
        valB = String(valB || '').toLowerCase();
      }

      if (valA < valB) return sortOrder === 'asc' ? -1 : 1;
      if (valA > valB) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
  }, [findings, searchTerm, selectedTier, selectedType, selectedSanction, sortField, sortOrder]);

  const toggleSort = (field) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  const getTypeIcon = (type) => {
    switch ((type || '').toLowerCase()) {
      case 'extension':
        return <Puzzle size={15} style={{ color: 'var(--accent-purple)' }} title="Browser Extension" />;
      case 'domain':
        return <Globe size={15} style={{ color: 'var(--primary)' }} title="Network / DNS Domain" />;
      default:
        return <Bot size={15} style={{ color: 'var(--accent-cyan)' }} title="AI Entity" />;
    }
  };

  return (
    <div className="glass-card" style={{ padding: '1.5rem' }}>
      {/* Controls / Filter Bar */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '1rem',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '1.5rem',
        paddingBottom: '1.25rem',
        borderBottom: '1px solid var(--border-subtle)'
      }}>
        {/* Search */}
        <div style={{ position: 'relative', minWidth: '280px', flex: '1 1 300px' }}>
          <Search size={16} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            className="form-input"
            style={{ paddingLeft: '2.5rem' }}
            placeholder="Search service, domain, host, user, category..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', alignItems: 'center' }}>
          {/* Risk Tier */}
          <select
            className="form-select"
            style={{ width: 'auto', padding: '0.6rem 0.85rem', fontSize: '0.85rem' }}
            value={selectedTier}
            onChange={(e) => setSelectedTier(e.target.value)}
          >
            <option value="ALL">All Risk Tiers</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          {/* Entity Type */}
          <select
            className="form-select"
            style={{ width: 'auto', padding: '0.6rem 0.85rem', fontSize: '0.85rem' }}
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
          >
            <option value="ALL">All Asset Types</option>
            <option value="DOMAIN">Network Domain</option>
            <option value="EXTENSION">Browser Extension</option>
          </select>

          {/* Sanction Status */}
          <select
            className="form-select"
            style={{ width: 'auto', padding: '0.6rem 0.85rem', fontSize: '0.85rem' }}
            value={selectedSanction}
            onChange={(e) => setSelectedSanction(e.target.value)}
          >
            <option value="ALL">All Statuses</option>
            <option value="UNSANCTIONED">Unsanctioned</option>
            <option value="SANCTIONED">Sanctioned</option>
            <option value="UNKNOWN">Unknown / Review</option>
          </select>

          {(searchTerm || selectedTier !== 'ALL' || selectedType !== 'ALL' || selectedSanction !== 'ALL') && (
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedTier('ALL');
                setSelectedType('ALL');
                setSelectedSanction('ALL');
              }}
              className="btn btn-secondary btn-sm"
              title="Reset Filters"
            >
              Reset
            </button>
          )}
        </div>
      </div>

      {/* Findings Table */}
      <div className="table-container">
        <table className="custom-table">
          <thead>
            <tr>
              <th onClick={() => toggleSort('risk_score')} style={{ cursor: 'pointer', width: '130px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  Risk Score <ArrowUpDown size={13} />
                </div>
              </th>
              <th onClick={() => toggleSort('service_name')} style={{ cursor: 'pointer' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  AI Service / Entity <ArrowUpDown size={13} />
                </div>
              </th>
              <th>Category</th>
              <th>Sanction Status</th>
              <th onClick={() => toggleSort('user_or_host')} style={{ cursor: 'pointer' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  User / Host <ArrowUpDown size={13} />
                </div>
              </th>
              <th>Data Exposure</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredFindings.length === 0 ? (
              <tr>
                <td colSpan="7" style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
                  <ShieldAlert size={36} style={{ opacity: 0.4, marginBottom: '0.75rem', display: 'block', margin: '0 auto' }} />
                  <p style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>No shadow AI findings match current criteria.</p>
                  <p style={{ fontSize: '0.8rem', marginTop: '0.25rem' }}>Try clearing your filters or ingest a new proxy/extension audit log.</p>
                </td>
              </tr>
            ) : (
              filteredFindings.map((item) => {
                const isUnsanctioned = (item.sanction_status || '').toLowerCase() === 'unsanctioned';
                return (
                  <tr key={item.id}>
                    {/* Risk Badge */}
                    <td>
                      <RiskBadge tier={item.risk_tier} score={Math.round(item.risk_score)} />
                    </td>

                    {/* Service & Identifier */}
                    <td>
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.65rem' }}>
                        <div style={{
                          marginTop: '2px',
                          background: 'rgba(255, 255, 255, 0.05)',
                          padding: '0.35rem',
                          borderRadius: 'var(--radius-sm)'
                        }}>
                          {getTypeIcon(item.entity_type)}
                        </div>
                        <div>
                          <div style={{ fontWeight: 700, color: '#f8fafc', fontSize: '0.95rem' }}>
                            {item.service_name || 'Unknown AI Service'}
                          </div>
                          <div style={{
                            fontSize: '0.75rem',
                            color: 'var(--text-muted)',
                            fontFamily: 'var(--font-mono)',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.35rem'
                          }}>
                            {item.entity_identifier}
                          </div>
                        </div>
                      </div>
                    </td>

                    {/* Category */}
                    <td>
                      <span style={{
                        fontSize: '0.8rem',
                        color: 'var(--text-secondary)',
                        background: 'rgba(255, 255, 255, 0.04)',
                        padding: '0.2rem 0.5rem',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--border-subtle)'
                      }}>
                        {item.category || 'General AI'}
                      </span>
                    </td>

                    {/* Sanction Status */}
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem' }}>
                        {isUnsanctioned ? (
                          <>
                            <XCircle size={15} style={{ color: 'var(--risk-critical)' }} />
                            <span style={{ color: '#fca5a5', fontWeight: 600 }}>Unsanctioned</span>
                          </>
                        ) : (
                          <>
                            <CheckCircle2 size={15} style={{ color: 'var(--accent-emerald)' }} />
                            <span style={{ color: '#a7f3d0' }}>Sanctioned</span>
                          </>
                        )}
                      </div>
                    </td>

                    {/* User / Host */}
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                        <User size={14} style={{ color: 'var(--text-muted)' }} />
                        <span>{item.user_or_host || 'System / Network'}</span>
                      </div>
                    </td>

                    {/* Data Exposure */}
                    <td>
                      <span style={{
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        color: item.data_exposure_risk === 'HIGH' ? '#f87171' : item.data_exposure_risk === 'MEDIUM' ? '#fde047' : '#94a3b8'
                      }}>
                        {item.data_exposure_risk || 'LOW'}
                      </span>
                    </td>

                    {/* Actions */}
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', gap: '0.5rem', alignItems: 'center' }}>
                        {onInvestigate && (userRole === 'admin' || userRole === 'analyst') && (
                          <button
                            onClick={() => onInvestigate(item)}
                            className="btn btn-secondary btn-sm"
                            title="Run LLM Agent Investigation"
                            style={{ padding: '0.35rem 0.65rem', borderColor: 'rgba(56, 189, 248, 0.4)', color: '#38bdf8' }}
                          >
                            <Sparkles size={14} />
                            <span style={{ fontSize: '0.75rem' }}>Agent</span>
                          </button>
                        )}

                        <Link
                          to={`/findings/${item.id}`}
                          className="btn btn-secondary btn-sm"
                          style={{ padding: '0.35rem 0.65rem' }}
                          title="View Finding Details"
                        >
                          <ExternalLink size={14} />
                        </Link>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Footer Info */}
      <div style={{
        marginTop: '1.25rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        fontSize: '0.8rem',
        color: 'var(--text-muted)'
      }}>
        <div>Showing <strong>{filteredFindings.length}</strong> of <strong>{findings.length}</strong> findings</div>
        <div style={{ fontFamily: 'var(--font-mono)' }}>AI-Assisted Risk Engine v1.0</div>
      </div>
    </div>
  );
};

export default FindingsTable;
