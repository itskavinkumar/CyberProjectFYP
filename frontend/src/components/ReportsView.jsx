import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Download, 
  PlusCircle, 
  RefreshCw, 
  Eye, 
  CheckCircle, 
  AlertTriangle, 
  X, 
  Layers, 
  Calendar, 
  ShieldAlert, 
  User, 
  FileDown
} from 'lucide-react';
import { listReports, generateReport, getReportDetails, getReportExportUrl } from '../api';

const REPORT_TYPES = [
  { id: 'threat_forecast', label: 'AI Threat Forecast Report', adminOnly: false, desc: 'LSTM projection, risk scoring, confidence intervals, and evaluation metrics.' },
  { id: 'risk_assessment', label: 'SOC Comprehensive Threat Risk Assessment', adminOnly: false, desc: 'Multi-category threat matrix, critical threat volume, and trend indices.' },
  { id: 'threat_trends', label: 'Historical Threat Trends Analysis', adminOnly: false, desc: 'Aggregated telemetry volumes by category and historical distribution.' },
  { id: 'model_performance', label: 'LSTM Deep Learning Model Audit', adminOnly: false, desc: 'Validation MAE, RMSE, MAPE metrics and disk artifact statuses for 8 models.' },
  { id: 'dataset_summary', label: 'Dataset Ingestion & Validation Summary', adminOnly: false, desc: 'Ingestion records, date spans, and schema validation histories.' },
  { id: 'user_activity', label: 'Personnel Activity & Access Governance', adminOnly: true, desc: 'Operator access distribution, active vs disabled ratios, and login telemetry.' },
  { id: 'audit_trail', label: 'SOC Security Audit Trail Report', adminOnly: true, desc: 'Comprehensive audit event breakdown and forensic security events.' }
];

export default function ReportsView({ currentUser }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [typeFilter, setTypeFilter] = useState('all');

  // Generation Modal State
  const [isGenerateOpen, setIsGenerateOpen] = useState(false);
  const [selectedType, setSelectedType] = useState('threat_forecast');
  const [customTitle, setCustomTitle] = useState('');
  const [threatCategory, setThreatCategory] = useState('Phishing');
  const [forecastHorizon, setForecastHorizon] = useState(30);
  const [genLoading, setGenLoading] = useState(false);
  const [genError, setGenError] = useState(null);
  const [genSuccess, setGenSuccess] = useState(null);

  // View Details Modal State
  const [selectedReport, setSelectedReport] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const isAdmin = (currentUser?.role || '').toLowerCase() === 'admin';
  const isViewer = (currentUser?.role || '').toLowerCase() === 'viewer';

  const fetchReports = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listReports(typeFilter);
      setReports(res.reports || []);
    } catch (err) {
      setError(err.message || 'Failed to retrieve report archives.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [typeFilter]);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setGenLoading(true);
    setGenError(null);
    try {
      const params = {};
      if (selectedType === 'threat_forecast') {
        params.threat_type = threatCategory;
        params.forecast_days = Number(forecastHorizon);
      }
      const payload = {
        report_type: selectedType,
        title: customTitle.trim() || undefined,
        parameters: params
      };
      const created = await generateReport(payload);
      setGenSuccess(`Report '${created.title}' successfully generated!`);
      setIsGenerateOpen(false);
      setCustomTitle('');
      fetchReports();
    } catch (err) {
      setGenError(err.message || 'Report generation failed.');
    } finally {
      setGenLoading(false);
    }
  };

  const handleViewReport = async (rep) => {
    setDetailLoading(true);
    try {
      const data = await getReportDetails(rep.report_id || rep.id);
      setSelectedReport(data);
    } catch (err) {
      setError(err.message || 'Failed to load report data.');
    } finally {
      setDetailLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    try {
      const d = new Date(dateStr);
      return d.toLocaleString('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateStr;
    }
  };

  const availableTypes = REPORT_TYPES.filter(rt => !rt.adminOnly || isAdmin);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header Banner */}
      <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.35rem' }}>
            <div style={{ background: 'rgba(56, 189, 248, 0.15)', padding: '0.45rem', borderRadius: '8px', border: '1px solid var(--border-bright)' }}>
              <FileText size={22} color="#38bdf8" />
            </div>
            <h2 style={{ fontSize: '1.25rem', color: '#fff' }}>
              SOC Intelligence & Security Report Center
            </h2>
            <span className="badge badge-low" style={{ fontSize: '0.7rem' }}>
              {reports.length} Reports
            </span>
          </div>
          <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>
            Compile formal AI threat forecasts, operational risk assessments, model verification summaries, and administrative audit reports.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button onClick={() => fetchReports()} className="btn btn-secondary" title="Refresh Reports">
            <RefreshCw size={16} />
          </button>
          {!isViewer && (
            <button 
              onClick={() => {
                setGenError(null);
                setIsGenerateOpen(true);
              }} 
              className="btn btn-primary"
              id="btn-generate-report"
            >
              <PlusCircle size={16} />
              <span>Generate SOC Report</span>
            </button>
          )}
        </div>
      </div>

      {genSuccess && (
        <div style={{ background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.4)', color: '#34d399', padding: '0.85rem 1.25rem', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', fontSize: '0.85rem' }}>
            <CheckCircle size={18} />
            <span>{genSuccess}</span>
          </div>
          <button onClick={() => setGenSuccess(null)} style={{ background: 'none', border: 'none', color: '#34d399', cursor: 'pointer' }}>
            <X size={16} />
          </button>
        </div>
      )}

      {error && (
        <div style={{ background: 'rgba(244, 63, 94, 0.12)', border: '1px solid rgba(244, 63, 94, 0.4)', color: '#fda4af', padding: '0.85rem 1.25rem', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '0.65rem', fontSize: '0.85rem' }}>
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Filter Bar */}
      <div className="glass-panel" style={{ padding: '1rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.85rem', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600 }}>Filter Category:</span>
        <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
          <button
            onClick={() => setTypeFilter('all')}
            className={typeFilter === 'all' ? 'btn btn-primary' : 'btn btn-secondary'}
            style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }}
          >
            All Reports
          </button>
          {availableTypes.map((t) => (
            <button
              key={t.id}
              onClick={() => setTypeFilter(t.id)}
              className={typeFilter === t.id ? 'btn btn-primary' : 'btn btn-secondary'}
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }}
            >
              {t.label.split(' ')[0]}
            </button>
          ))}
        </div>
      </div>

      {/* Report History Table */}
      <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
        <div className="soc-table-container">
          <table className="soc-table">
            <thead>
              <tr>
                <th>Report ID & Title</th>
                <th>Classification</th>
                <th>Generated By</th>
                <th>Role</th>
                <th>Date & Time</th>
                <th>Status</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                    <RefreshCw className="spin" size={24} style={{ margin: '0 auto 0.5rem auto' }} />
                    <p>Loading generated reports...</p>
                  </td>
                </tr>
              ) : reports.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                    No reports generated yet. Click "Generate SOC Report" to create one.
                  </td>
                </tr>
              ) : (
                reports.map((rep) => {
                  const roleBadgeClass = rep.generated_by_role === 'admin' ? 'badge-critical' : 'badge-medium';
                  return (
                    <tr key={rep.id || rep.report_id}>
                      <td>
                        <div style={{ fontWeight: 600, color: '#fff' }}>{rep.title}</div>
                        <div style={{ fontSize: '0.725rem', color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
                          {rep.report_id}
                        </div>
                      </td>
                      <td>
                        <span className="badge badge-low" style={{ textTransform: 'capitalize' }}>
                          {rep.report_type.replace('_', ' ')}
                        </span>
                      </td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-primary)' }}>
                        {rep.generated_by}
                      </td>
                      <td>
                        <span className={`badge ${roleBadgeClass}`}>
                          {rep.generated_by_role}
                        </span>
                      </td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        {formatDate(rep.timestamp)}
                      </td>
                      <td>
                        <span className="badge badge-low" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>
                          COMPLETED
                        </span>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <div style={{ display: 'inline-flex', gap: '0.4rem' }}>
                          <button
                            onClick={() => handleViewReport(rep)}
                            className="btn btn-secondary"
                            title="Inspect Report Metrics"
                            style={{ padding: '0.35rem 0.6rem' }}
                          >
                            <Eye size={14} />
                          </button>
                          <a
                            href={getReportExportUrl(rep.report_id || rep.id, 'csv')}
                            download
                            className="btn btn-secondary"
                            title="Export as CSV"
                            style={{ padding: '0.35rem 0.6rem', textDecoration: 'none' }}
                          >
                            <FileDown size={14} color="#34d399" />
                          </a>
                          <a
                            href={getReportExportUrl(rep.report_id || rep.id, 'json')}
                            download
                            className="btn btn-secondary"
                            title="Export as JSON"
                            style={{ padding: '0.35rem 0.6rem', textDecoration: 'none' }}
                          >
                            <Download size={14} color="#38bdf8" />
                          </a>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* GENERATE REPORT MODAL */}
      {isGenerateOpen && (
        <div className="modal-overlay" onClick={() => setIsGenerateOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '560px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                <PlusCircle size={20} color="#06b6d4" />
                <h3 style={{ color: '#fff', fontSize: '1.15rem' }}>Generate SOC Intelligence Report</h3>
              </div>
              <button onClick={() => setIsGenerateOpen(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            {genError && (
              <div style={{ background: 'rgba(244, 63, 94, 0.15)', border: '1px solid #f43f5e', padding: '0.75rem', borderRadius: '8px', color: '#fca5a5', fontSize: '0.8rem', marginBottom: '1rem' }}>
                {genError}
              </div>
            )}

            <form onSubmit={handleGenerate} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
                  Select Report Type
                </label>
                <select
                  value={selectedType}
                  onChange={(e) => setSelectedType(e.target.value)}
                  className="input-control"
                >
                  {availableTypes.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.label} {t.adminOnly ? '🔒 (Admin Only)' : ''}
                    </option>
                  ))}
                </select>
                <p style={{ fontSize: '0.725rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
                  {REPORT_TYPES.find(r => r.id === selectedType)?.desc}
                </p>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
                  Custom Report Title (Optional)
                </label>
                <input
                  type="text"
                  placeholder="e.g. Q4 Phishing Surge & Vulnerability Forecast"
                  value={customTitle}
                  onChange={(e) => setCustomTitle(e.target.value)}
                  className="input-control"
                />
              </div>

              {selectedType === 'threat_forecast' && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', background: 'rgba(15, 23, 42, 0.5)', padding: '0.85rem', borderRadius: '8px' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
                      Threat Category
                    </label>
                    <select
                      value={threatCategory}
                      onChange={(e) => setThreatCategory(e.target.value)}
                      className="input-control"
                    >
                      <option value="Phishing">Phishing</option>
                      <option value="Malware">Malware</option>
                      <option value="Brute Force">Brute Force</option>
                      <option value="DDoS">DDoS</option>
                      <option value="Botnet">Botnet</option>
                      <option value="SQL Injection">SQL Injection</option>
                      <option value="Ransomware">Ransomware</option>
                      <option value="Data Breach">Data Breach</option>
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
                      Forecast Horizon
                    </label>
                    <select
                      value={forecastHorizon}
                      onChange={(e) => setForecastHorizon(e.target.value)}
                      className="input-control"
                    >
                      <option value={7}>7 Days (Tactical)</option>
                      <option value={14}>14 Days (Operational)</option>
                      <option value={30}>30 Days (Strategic)</option>
                    </select>
                  </div>
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button type="button" onClick={() => setIsGenerateOpen(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" disabled={genLoading} className="btn btn-primary">
                  {genLoading ? 'Compiling Metrics...' : 'Generate & Store Report'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* VIEW REPORT DETAILS MODAL */}
      {selectedReport && (
        <div className="modal-overlay" onClick={() => setSelectedReport(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '650px', maxHeight: '85vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.85rem' }}>
              <div>
                <h3 style={{ color: '#fff', fontSize: '1.2rem' }}>{selectedReport.title}</h3>
                <div style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
                  {selectedReport.report_id} • Compiled {formatDate(selectedReport.timestamp)}
                </div>
              </div>
              <button onClick={() => setSelectedReport(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', fontSize: '0.825rem', marginBottom: '1.5rem' }}>
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
                <div>Operator: <strong style={{ color: '#fff' }}>{selectedReport.generated_by}</strong></div>
                <div>Role: <span className="badge badge-low">{selectedReport.generated_by_role}</span></div>
                <div>Type: <span className="badge badge-medium">{selectedReport.report_type}</span></div>
              </div>

              {/* Summary Metrics Display */}
              <div>
                <h4 style={{ color: '#fff', fontSize: '0.9rem', marginBottom: '0.5rem' }}>Executive Summary & Metrics</h4>
                <div style={{
                  background: 'rgba(7, 10, 19, 0.8)',
                  padding: '1rem',
                  borderRadius: '8px',
                  border: '1px solid var(--border-subtle)'
                }}>
                  {selectedReport.summary_data && typeof selectedReport.summary_data === 'object' ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                      {Object.entries(selectedReport.summary_data).map(([key, value]) => (
                        <div key={key} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(51, 65, 85, 0.3)', paddingBottom: '0.35rem' }}>
                          <span style={{ color: 'var(--text-secondary)', textTransform: 'capitalize' }}>
                            {key.replace(/_/g, ' ')}:
                          </span>
                          <span style={{ color: '#fff', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
                            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p style={{ color: 'var(--text-muted)' }}>No structured summary data recorded.</p>
                  )}
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <a
                  href={getReportExportUrl(selectedReport.report_id || selectedReport.id, 'csv')}
                  download
                  className="btn btn-secondary"
                  style={{ textDecoration: 'none', padding: '0.45rem 0.85rem', fontSize: '0.8rem' }}
                >
                  <FileDown size={15} color="#34d399" />
                  <span>Download CSV</span>
                </a>
                <a
                  href={getReportExportUrl(selectedReport.report_id || selectedReport.id, 'json')}
                  download
                  className="btn btn-secondary"
                  style={{ textDecoration: 'none', padding: '0.45rem 0.85rem', fontSize: '0.8rem' }}
                >
                  <Download size={15} color="#38bdf8" />
                  <span>Download JSON</span>
                </a>
              </div>

              <button onClick={() => setSelectedReport(null)} className="btn btn-secondary">
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
