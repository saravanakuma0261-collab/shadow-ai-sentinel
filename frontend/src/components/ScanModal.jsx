import React, { useState } from 'react';
import { 
  X, 
  UploadCloud, 
  FileText, 
  Puzzle, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle,
  Loader2,
  FileCode
} from 'lucide-react';
import client from '../api/client';

const SAMPLE_NETWORK_LOGS = `timestamp,client_ip,user_id,domain,query_type,response_code,bytes_sent,bytes_received
2026-08-24T08:15:30Z,10.0.1.45,saravana.kumar,api.openai.com,A,NOERROR,1420,8920
2026-08-24T08:16:12Z,10.0.1.45,saravana.kumar,chatgpt.com,A,NOERROR,3200,15400
2026-08-24T08:22:04Z,10.0.2.112,david.chen,claude.ai,A,NOERROR,2100,12300
2026-08-24T08:35:10Z,10.0.3.89,alicia.vance,chat.deepseek.com,A,NOERROR,4500,28900
2026-08-24T08:41:55Z,10.0.1.78,marcus.brooks,otter.ai,A,NOERROR,18900,4500
2026-08-24T08:50:22Z,10.0.4.15,elena.rostova,api.groq.com,A,NOERROR,890,3400
2026-08-24T09:05:14Z,10.0.2.66,kevin.wright,jasper.ai,A,NOERROR,1200,6700
2026-08-24T09:12:00Z,10.0.1.45,saravana.kumar,internal-wiki.corp.local,A,NOERROR,500,1200`;

const SAMPLE_EXTENSION_LOGS = JSON.stringify([
  {
    "id": "cjpalhdlnbpafiamejdnhcphjbkeiagm",
    "name": "uBlock Origin",
    "version": "1.58.0",
    "permissions": ["tabs", "storage"],
    "user_email": "saravana.kumar@enterprise.com",
    "device_hostname": "DEV-SARAVANA-WIN11"
  },
  {
    "id": "kbfnbcaeplbcioakkpcpgfkobkghlhen",
    "name": "Grammarly: AI Writing and Grammar Checker",
    "version": "14.1120.0",
    "permissions": ["<all_urls>", "webRequest", "storage", "cookies"],
    "user_email": "alicia.vance@enterprise.com",
    "device_hostname": "FIN-ALICIA-MAC"
  },
  {
    "id": "ammjkodgmmoknidbannedaihelperext",
    "name": "AutoChatGPT: Prompt & Screen Scraper AI",
    "version": "1.0.4",
    "permissions": ["<all_urls>", "webRequest", "webRequestBlocking", "clipboardRead", "activeTab"],
    "user_email": "david.chen@enterprise.com",
    "device_hostname": "ENG-DAVID-UBUNTU"
  },
  {
    "id": "notionaimateextensionhelperid123",
    "name": "Notion AI Web Clipper",
    "version": "2.4.1",
    "permissions": ["activeTab", "storage", "tabs"],
    "user_email": "kevin.wright@enterprise.com",
    "device_hostname": "MKT-KEVIN-WIN11"
  }
], null, 2);

const ScanModal = ({ isOpen, onClose, onScanComplete }) => {
  const [scanType, setScanType] = useState('network'); // 'network' or 'extension'
  const [scanName, setScanName] = useState('');
  const [logData, setLogData] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successResult, setSuccessResult] = useState(null);

  if (!isOpen) return null;

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      setLogData(event.target.result);
      if (!scanName) {
        setScanName(`Ingestion_${file.name.replace(/\.[^/.]+$/, '')}_${new Date().toLocaleDateString()}`);
      }
    };
    reader.readAsText(file);
  };

  const loadSample = () => {
    if (scanType === 'network') {
      setLogData(SAMPLE_NETWORK_LOGS);
      setScanName(`Sample_DNS_Proxy_Audit_${new Date().toISOString().slice(0, 10)}`);
    } else {
      setLogData(SAMPLE_EXTENSION_LOGS);
      setScanName(`Sample_Chrome_Extension_Audit_${new Date().toISOString().slice(0, 10)}`);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!logData.trim()) {
      setError('Please provide log data or upload a file.');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccessResult(null);

    try {
      const payload = {
        name: scanName || `${scanType.toUpperCase()} Audit - ${new Date().toLocaleTimeString()}`,
        scan_type: scanType,
        raw_data: logData,
      };

      const response = await client.post('/scan', payload);
      setSuccessResult(response.data);
      if (onScanComplete) {
        onScanComplete(response.data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to execute shadow AI scan. Please verify data format.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="glass-card modal-content" style={{ position: 'relative' }}>
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1.25rem',
            right: '1.25rem',
            background: 'transparent',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer'
          }}
        >
          <X size={20} />
        </button>

        {/* Modal Header */}
        <div style={{ marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>
            Run Shadow AI <span className="title-gradient">Detection Scan</span>
          </h2>
          <p className="subtitle">
            Ingest network proxy logs or browser extension inventories for automated heuristic classification.
          </p>
        </div>

        {/* Success View */}
        {successResult ? (
          <div style={{ textAlign: 'center', padding: '1.5rem 0' }}>
            <div style={{
              display: 'inline-flex',
              padding: '1rem',
              borderRadius: '50%',
              background: 'rgba(16, 185, 129, 0.15)',
              color: 'var(--accent-emerald)',
              marginBottom: '1rem'
            }}>
              <CheckCircle2 size={36} />
            </div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f8fafc', marginBottom: '0.4rem' }}>
              Scan Executed Successfully!
            </h3>
            <p className="subtitle" style={{ marginBottom: '1.5rem' }}>
              Processed <strong>{successResult.total_events || successResult.findings_count || 0}</strong> events, 
              identified <strong>{successResult.findings_count || 0}</strong> shadow AI entities.
            </p>

            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
              <button
                onClick={() => {
                  setSuccessResult(null);
                  setLogData('');
                  setScanName('');
                  onClose();
                }}
                className="btn btn-primary"
              >
                Done & View Findings
              </button>
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

            {/* Ingestion Source Tabs */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1.25rem' }}>
              <button
                type="button"
                onClick={() => {
                  setScanType('network');
                  setLogData('');
                }}
                className={`btn ${scanType === 'network' ? 'btn-primary' : 'btn-secondary'}`}
                style={{ justifyContent: 'center' }}
              >
                <FileText size={16} />
                <span>Network / DNS Proxy (CSV)</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  setScanType('extension');
                  setLogData('');
                }}
                className={`btn ${scanType === 'extension' ? 'btn-primary' : 'btn-secondary'}`}
                style={{ justifyContent: 'center' }}
              >
                <Puzzle size={16} />
                <span>Browser Extensions (JSON)</span>
              </button>
            </div>

            {/* Scan Name */}
            <div className="form-group">
              <label className="form-label">Scan Label / Identifier</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. Q3 Gateway DNS Proxy Log"
                value={scanName}
                onChange={(e) => setScanName(e.target.value)}
              />
            </div>

            {/* Upload or Sample Helper */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
              <label className="form-label">Log Payload / Raw Content</label>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  type="button"
                  onClick={loadSample}
                  className="btn btn-secondary btn-sm"
                  style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem' }}
                >
                  <Sparkles size={12} />
                  <span>Insert Sample Data</span>
                </button>
                <label className="btn btn-secondary btn-sm" style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem', cursor: 'pointer' }}>
                  <UploadCloud size={12} />
                  <span>Upload File</span>
                  <input type="file" style={{ display: 'none' }} accept=".csv,.json,.txt,.log" onChange={handleFileUpload} />
                </label>
              </div>
            </div>

            {/* Textarea */}
            <div className="form-group">
              <textarea
                className="form-textarea"
                rows={8}
                style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', whiteSpace: 'pre' }}
                placeholder={scanType === 'network' 
                  ? "timestamp,client_ip,user_id,domain,query_type,response_code,bytes_sent,bytes_received\n2026-08-24T08:15:30Z,10.0.1.45,saravana,api.openai.com,A,NOERROR,1420,8920..."
                  : "[\n  {\n    \"id\": \"extension_id\",\n    \"name\": \"AI Helper Extension\",\n    \"permissions\": [\"<all_urls>\"]\n  }\n]"}
                value={logData}
                onChange={(e) => setLogData(e.target.value)}
              />
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.5rem' }}>
              <button
                type="button"
                onClick={onClose}
                className="btn btn-secondary"
                disabled={loading}
              >
                Cancel
              </button>

              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    <span>Analyzing Log Stream...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={16} />
                    <span>Start Detection Engine</span>
                  </>
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default ScanModal;
