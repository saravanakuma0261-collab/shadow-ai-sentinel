import React, { useState, useEffect } from 'react';
import { Layers, Sparkles, RefreshCw, Filter, ShieldAlert } from 'lucide-react';
import client from '../api/client';
import { useAuth } from '../auth/AuthContext';
import FindingsTable from '../components/FindingsTable';
import ScanModal from '../components/ScanModal';
import { useNavigate } from 'react-router-dom';

const Findings = () => {
  const { role, hasRole } = useAuth();
  const navigate = useNavigate();
  const [findings, setFindings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isScanModalOpen, setIsScanModalOpen] = useState(false);

  const fetchFindings = async () => {
    setLoading(true);
    try {
      const res = await client.get('/findings');
      setFindings(res.data || []);
    } catch (err) {
      console.error('Failed to fetch findings:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFindings();
  }, []);

  const handleInvestigate = (finding) => {
    navigate(`/findings/${finding.id}?auto_investigate=1`);
  };

  const canRunScan = hasRole(['admin', 'analyst']);

  return (
    <div className="main-content">
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
        <div>
          <h1 className="title-hero">
            Discovered <span className="title-gradient">Shadow AI Inventory</span>
          </h1>
          <p className="subtitle">
            Comprehensive audit of unauthorized AI platforms, browser extensions, and developer endpoints
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <button
            onClick={fetchFindings}
            className="btn btn-secondary"
            title="Refresh findings"
            disabled={loading}
          >
            <RefreshCw size={15} className={loading ? 'animate-spin' : ''} />
            <span>Refresh</span>
          </button>

          {canRunScan && (
            <button
              onClick={() => setIsScanModalOpen(true)}
              className="btn btn-primary"
            >
              <Sparkles size={16} />
              <span>Ingest Log Stream</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Table */}
      <FindingsTable
        findings={findings}
        onInvestigate={handleInvestigate}
        userRole={role}
      />

      {/* Ingestion Modal */}
      <ScanModal
        isOpen={isScanModalOpen}
        onClose={() => setIsScanModalOpen(false)}
        onScanComplete={() => {
          fetchFindings();
        }}
      />
    </div>
  );
};

export default Findings;
