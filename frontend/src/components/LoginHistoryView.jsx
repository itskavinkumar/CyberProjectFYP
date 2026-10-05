import React, { useState, useEffect } from 'react';
import { 
  Key, 
  Search, 
  Filter, 
  CheckCircle, 
  AlertTriangle, 
  LogOut, 
  ChevronLeft, 
  ChevronRight, 
  RefreshCw, 
  Eye, 
  X,
  Laptop,
  ShieldAlert
} from 'lucide-react';
import { getLoginHistory } from '../api';

export default function LoginHistoryView() {
  const [history, setHistory] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const limit = 15;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [selectedEvent, setSelectedEvent] = useState(null);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getLoginHistory({
        status: statusFilter,
        search,
        page,
        limit
      });
      setHistory(res.history || []);
      setTotal(res.total || 0);
    } catch (err) {
      setError(err.message || 'Failed to load login telemetry.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page, statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    fetchHistory();
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

  const totalPages = Math.ceil(total / limit) || 1;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Header */}
      <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.35rem' }}>
            <div style={{ background: 'rgba(59, 130, 246, 0.15)', padding: '0.45rem', borderRadius: '8px', border: '1px solid var(--accent-blue)' }}>
              <Key size={22} color="#3b82f6" />
            </div>
            <h2 style={{ fontSize: '1.25rem', color: '#fff' }}>
              Authentication & Session Telemetry Log
            </h2>
            <span className="badge badge-medium" style={{ fontSize: '0.7rem' }}>
              {total} Total Sessions Recorded
            </span>
          </div>
          <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>
            Real-time verification stream capturing successful access, failed authentication attempts, brute force alerts, and explicit session termination.
          </p>
        </div>

        <button onClick={() => fetchHistory()} className="btn btn-secondary" style={{ padding: '0.6rem 0.85rem' }} title="Refresh">
          <RefreshCw size={16} />
        </button>
      </div>

      {error && (
        <div style={{ background: 'rgba(244, 63, 94, 0.12)', border: '1px solid rgba(244, 63, 94, 0.4)', color: '#fda4af', padding: '0.85rem 1.25rem', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '0.65rem', fontSize: '0.85rem' }}>
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Filter Bar */}
      <div className="glass-panel" style={{ padding: '1.25rem' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '0.85rem' }}>
          <div style={{ flex: '1 1 260px', position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search by operator email, callsign, or IP..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input-control"
              style={{ paddingLeft: '2.4rem' }}
              id="login-search-input"
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Status:</label>
            <select
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
              className="input-control"
              style={{ width: '140px' }}
              id="login-filter-status"
            >
              <option value="all">All Outcomes</option>
              <option value="success">Success Only</option>
              <option value="failed">Failed Only</option>
            </select>
          </div>

          <button type="submit" className="btn btn-secondary">
            Filter Log
          </button>
        </form>
      </div>

      {/* Table */}
      <div className="glass-panel" style={{ padding: '0', overflow: 'hidden' }}>
        <div className="soc-table-container">
          <table className="soc-table">
            <thead>
              <tr>
                <th>Operator / Identity</th>
                <th>Role</th>
                <th>Action Type</th>
                <th>Timestamp</th>
                <th>Result Status</th>
                <th>Client IP</th>
                <th>Device / Client</th>
                <th style={{ textAlign: 'right' }}>Inspect</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={8} style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                    <RefreshCw className="spin" size={24} style={{ margin: '0 auto 0.5rem auto' }} />
                    <p>Loading session telemetry...</p>
                  </td>
                </tr>
              ) : history.length === 0 ? (
                <tr>
                  <td colSpan={8} style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                    No authentication events recorded matching filter.
                  </td>
                </tr>
              ) : (
                history.map((ev) => {
                  const isSuccess = ev.status === 'success';
                  const isFailed = ev.status === 'failed';
                  const isLogout = ev.action === 'LOGOUT';

                  return (
                    <tr key={ev.id}>
                      <td>
                        <div style={{ fontWeight: 600, color: '#fff' }}>
                          {ev.user_name || (ev.email ? ev.email.split('@')[0] : 'Unknown Operator')}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                          {ev.email || 'Unregistered IP'}
                        </div>
                      </td>
                      <td>
                        <span className="badge badge-low" style={{ textTransform: 'capitalize' }}>
                          {ev.role || 'Visitor'}
                        </span>
                      </td>
                      <td>
                        <span style={{ 
                          fontFamily: 'var(--font-mono)', 
                          fontSize: '0.775rem',
                          fontWeight: 600,
                          color: isLogout ? 'var(--text-secondary)' : (isSuccess ? '#34d399' : '#f87171')
                        }}>
                          {ev.action}
                        </span>
                      </td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                        {formatDate(ev.timestamp)}
                      </td>
                      <td>
                        {isSuccess ? (
                          <span className="badge badge-low" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>
                            <CheckCircle size={12} /> SUCCESS
                          </span>
                        ) : (
                          <span className="badge badge-critical">
                            <ShieldAlert size={12} /> FAILED
                          </span>
                        )}
                      </td>
                      <td>
                        <code style={{ fontSize: '0.775rem', color: 'var(--accent-cyan)' }}>
                          {ev.ip_address || '127.0.0.1'}
                        </code>
                      </td>
                      <td style={{ fontSize: '0.75rem', color: 'var(--text-muted)', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={ev.user_agent}>
                        {ev.user_agent || 'Standard HTTP Client'}
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <button
                          onClick={() => setSelectedEvent(ev)}
                          className="btn btn-secondary"
                          title="View Technical Event Details"
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
            Page <span style={{ color: '#fff', fontWeight: 600 }}>{page}</span> of <span style={{ color: '#fff', fontWeight: 600 }}>{totalPages}</span> ({total} events)
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

      {/* Detail Inspection Modal */}
      {selectedEvent && (
        <div className="modal-overlay" onClick={() => setSelectedEvent(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '520px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                <Key size={20} color="#06b6d4" />
                <h3 style={{ color: '#fff', fontSize: '1.15rem' }}>Authentication Audit Record</h3>
              </div>
              <button onClick={() => setSelectedEvent(null)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.825rem', marginBottom: '1.25rem' }}>
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem', borderRadius: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Action:</span>
                  <strong style={{ color: '#fff' }}>{selectedEvent.action}</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Result:</span>
                  <span className={`badge ${selectedEvent.status === 'success' ? 'badge-low' : 'badge-critical'}`}>
                    {selectedEvent.status.toUpperCase()}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Timestamp:</span>
                  <span style={{ color: '#fff', fontFamily: 'var(--font-mono)' }}>{formatDate(selectedEvent.timestamp)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Subject Identity:</span>
                  <span style={{ color: 'var(--accent-cyan)' }}>{selectedEvent.email || 'N/A'}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Role:</span>
                  <span style={{ color: '#fff' }}>{selectedEvent.role || 'viewer'}</span>
                </div>
              </div>

              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem', borderRadius: '8px' }}>
                <div style={{ color: 'var(--text-muted)', marginBottom: '0.3rem' }}>Client Environment:</div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: '#fff', marginBottom: '0.4rem' }}>
                  IP: {selectedEvent.ip_address}
                </div>
                <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.725rem', color: 'var(--text-secondary)', wordBreak: 'break-all' }}>
                  UA: {selectedEvent.user_agent}
                </div>
              </div>

              {selectedEvent.details && Object.keys(selectedEvent.details).length > 0 && (
                <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem', borderRadius: '8px' }}>
                  <div style={{ color: 'var(--text-muted)', marginBottom: '0.3rem' }}>Diagnostic Details:</div>
                  <pre style={{ margin: 0, fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: '#93c5fd', whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(selectedEvent.details, null, 2)}
                  </pre>
                </div>
              )}
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button onClick={() => setSelectedEvent(null)} className="btn btn-secondary">
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
