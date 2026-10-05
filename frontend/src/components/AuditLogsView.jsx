import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Search, 
  Filter, 
  CheckCircle, 
  AlertTriangle, 
  ChevronLeft, 
  ChevronRight, 
  RefreshCw, 
  Eye, 
  X,
  Shield,
  Layers,
  Database,
  Activity,
  Cpu,
  BarChart2
} from 'lucide-react';
import { getAuditLogs } from '../api';

const ACTION_OPTIONS = [
  'ALL',
  'LOGIN_SUCCESS',
  'LOGIN_FAILED',
  'LOGOUT',
  'REGISTER',
  'USER_CREATED',
  'ROLE_CHANGED',
  'USER_ENABLED',
  'USER_DISABLED',
  'FORECAST_GENERATED',
  'DATASET_UPLOADED',
  'DATASET_REJECTED',
  'REPORT_GENERATED'
];

export default function AuditLogsView() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const limit = 20;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [actionFilter, setActionFilter] = useState('ALL');
  const [resourceFilter, setResourceFilter] = useState('all');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [selectedLog, setSelectedLog] = useState(null);

  const fetchLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getAuditLogs({
        action: actionFilter,
        resource_type: resourceFilter,
        role: roleFilter,
        status: statusFilter,
        search,
        page,
        limit
      });
      setLogs(res.logs || []);
      setTotal(res.total || 0);
    } catch (err) {
      setError(err.message || 'Failed to fetch audit log stream.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [page, actionFilter, resourceFilter, roleFilter, statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchLogs();
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
        minute: '2-digit',
        second: '2-digit'
      });
    } catch {
      return dateStr;
    }
  };

  const getActionColor = (action) => {
    if (action.includes('LOGIN_SUCCESS')) return '#34d399';
    if (action.includes('LOGIN_FAILED')) return '#f87171';
    if (action.includes('FORECAST')) return 'var(--accent-purple)';
    if (action.includes('DATASET')) return 'var(--accent-cyan)';
    if (action.includes('ROLE') || action.includes('USER_')) return 'var(--accent-amber)';
    if (action.includes('REPORT')) return '#38bdf8';
    return 'var(--text-primary)';
  };

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.35rem' }}>
            <div style={{ background: 'rgba(139, 92, 246, 0.15)', padding: '0.45rem', borderRadius: '8px', border: '1px solid var(--accent-purple)' }}>
              <Shield size={22} color="#8b5cf6" />
            </div>
            <h2 style={{ fontSize: '1.25rem', color: '#fff' }}>
              Centralized SOC Audit Trail & Governance Log
            </h2>
            <span className="badge badge-low" style={{ fontSize: '0.7rem' }}>
              {total} Total Audit Records
            </span>
          </div>
          <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>
            Immutable forensic audit records of all operational threat forecasts, dataset uploads, user provisioning, role adjustments, and security state modifications.
          </p>
        </div>

        <button onClick={() => fetchLogs()} className="btn btn-secondary" style={{ padding: '0.6rem 0.85rem' }} title="Refresh">
          <RefreshCw size={16} />
        </button>
      </div>

      {error && (
        <div style={{ background: 'rgba(244, 63, 94, 0.12)', border: '1px solid rgba(244, 63, 94, 0.4)', color: '#fda4af', padding: '0.85rem 1.25rem', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '0.65rem', fontSize: '0.85rem' }}>
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Filter and Query Controls */}
      <div className="glass-panel" style={{ padding: '1.25rem' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div style={{ flex: '1 1 220px', position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search by action, email, resource ID, or IP..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input-control"
              style={{ paddingLeft: '2.4rem' }}
              id="audit-search-input"
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Action:</label>
            <select
              value={actionFilter}
              onChange={(e) => { setActionFilter(e.target.value); setPage(1); }}
              className="input-control"
              style={{ width: '180px' }}
              id="audit-filter-action"
            >
              {ACTION_OPTIONS.map((act) => (
                <option key={act} value={act}>{act}</option>
              ))}
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Resource:</label>
            <select
              value={resourceFilter}
              onChange={(e) => { setResourceFilter(e.target.value); setPage(1); }}
              className="input-control"
              style={{ width: '120px' }}
              id="audit-filter-resource"
            >
              <option value="all">All</option>
              <option value="forecast">Forecast</option>
              <option value="dataset">Dataset</option>
              <option value="user">User</option>
              <option value="report">Report</option>
              <option value="auth">Auth</option>
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Status:</label>
            <select
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
              className="input-control"
              style={{ width: '110px' }}
              id="audit-filter-status"
            >
              <option value="all">All</option>
              <option value="success">Success</option>
              <option value="failed">Failed</option>
            </select>
          </div>

          <button type="submit" className="btn btn-secondary">
            Filter
          </button>
        </form>
      </div>

      {/* Audit Log Table */}
      <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
        <div className="soc-table-container">
          <table className="soc-table">
            <thead>
              <tr>
                <th>Timestamp (UTC)</th>
                <th>Operator / Identity</th>
                <th>Role</th>
                <th>Action</th>
                <th>Resource</th>
                <th>Outcome</th>
                <th>Client IP</th>
                <th style={{ textAlign: 'right' }}>Details</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={8} style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                    <RefreshCw className="spin" size={24} style={{ margin: '0 auto 0.5rem auto' }} />
                    <p>Loading security audit logs...</p>
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={8} style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                    No audit records match the current filters.
                  </td>
                </tr>
              ) : (
                logs.map((log) => {
                  const isSuccess = log.status === 'success';
                  const actionColor = getActionColor(log.action);
                  return (
                    <tr key={log.id}>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
                        {formatDate(log.timestamp)}
                      </td>
                      <td>
                        <div style={{ fontWeight: 600, color: '#fff' }}>
                          {log.user_name || 'System / Daemon'}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                          {log.email || 'Automated Internal'}
                        </div>
                      </td>
                      <td>
                        <span className="badge badge-low" style={{ textTransform: 'capitalize' }}>
                          {log.role || 'viewer'}
                        </span>
                      </td>
                      <td>
                        <span style={{ 
                          fontFamily: 'var(--font-mono)', 
                          fontSize: '0.775rem',
                          fontWeight: 700,
                          color: actionColor
                        }}>
                          {log.action}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)' }}>
                          {log.resource_type ? `${log.resource_type}${log.resource_id ? ` (${log.resource_id})` : ''}` : '-'}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${isSuccess ? 'badge-low' : 'badge-critical'}`}>
                          {log.status.toUpperCase()}
                        </span>
                      </td>
                      <td>
                        <code style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {log.ip_address || '127.0.0.1'}
                        </code>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <button
                          onClick={() => setSelectedLog(log)}
                          className="btn btn-secondary"
                          title="Inspect Event JSON Payload"
                          style={{ padding: '0.35rem 0.6rem' }}
                        >
                          <Eye size={14} />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div style={{
          padding: '1rem 1.5rem',
          borderTop: '1px solid var(--border-subtle)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '0.8rem',
          color: 'var(--text-secondary)'
        }}>
          <div>
            Showing Page <span style={{ color: '#fff', fontWeight: 600 }}>{page}</span> of <span style={{ color: '#fff', fontWeight: 600 }}>{totalPages}</span> ({total} logs)
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              disabled={page <= 1 || loading}
              onClick={() => setPage(page - 1)}
              className="btn btn-secondary"
              style={{ padding: '0.4rem 0.75rem' }}
            >
              <ChevronLeft size={16} />
              <span>Previous</span>
            </button>
            <button
              disabled={page >= totalPages || loading}
              onClick={() => setPage(page + 1)}
              className="btn btn-secondary"
              style={{ padding: '0.4rem 0.75rem' }}
            >
              <span>Next</span>
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Details Modal */}
      {selectedLog && (
        <div className="modal-overlay" onClick={() => setSelectedLog(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '580px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                <Shield size={20} color="#8b5cf6" />
                <h3 style={{ color: '#fff', fontSize: '1.15rem' }}>Audit Event Inspection</h3>
              </div>
              <button onClick={() => setSelectedLog(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.825rem', marginBottom: '1.25rem' }}>
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Action:</span>
                  <strong style={{ color: getActionColor(selectedLog.action) }}>{selectedLog.action}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Operator:</span>
                  <span style={{ color: '#fff' }}>{selectedLog.user_name} ({selectedLog.email || 'System'})</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Timestamp:</span>
                  <span style={{ color: '#fff', fontFamily: 'var(--font-mono)' }}>{formatDate(selectedLog.timestamp)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Resource:</span>
                  <span style={{ color: 'var(--accent-cyan)' }}>{selectedLog.resource_type || 'N/A'} (ID: {selectedLog.resource_id || 'N/A'})</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Status:</span>
                  <span className={`badge ${selectedLog.status === 'success' ? 'badge-low' : 'badge-critical'}`}>
                    {selectedLog.status.toUpperCase()}
                  </span>
                </div>
              </div>

              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem', borderRadius: '8px' }}>
                <div style={{ color: 'var(--text-muted)', marginBottom: '0.35rem' }}>Client Metadata:</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: '#fff', marginBottom: '0.25rem' }}>
                  IP: {selectedLog.ip_address}
                </div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.725rem', color: 'var(--text-secondary)', wordBreak: 'break-all' }}>
                  User-Agent: {selectedLog.user_agent}
                </div>
              </div>

              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem', borderRadius: '8px' }}>
                <div style={{ color: 'var(--text-muted)', marginBottom: '0.35rem' }}>Sanitized Details Payload:</div>
                <pre style={{
                  margin: 0,
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.75rem',
                  color: '#93c5fd',
                  background: 'rgba(7, 10, 19, 0.7)',
                  padding: '0.75rem',
                  borderRadius: '6px',
                  maxHeight: '180px',
                  overflowY: 'auto',
                  whiteSpace: 'pre-wrap'
                }}>
                  {JSON.stringify(selectedLog.details, null, 2)}
                </pre>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button onClick={() => setSelectedLog(null)} className="btn btn-secondary">
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
