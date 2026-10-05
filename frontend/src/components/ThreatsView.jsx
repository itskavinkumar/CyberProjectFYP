import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Filter, 
  PlusCircle, 
  ChevronLeft, 
  ChevronRight, 
  Search,
  CheckCircle,
  X,
  AlertTriangle,
  RefreshCw
} from 'lucide-react';
import { getThreatEvents, createThreatEvent } from '../api';

const THREAT_TYPES = [
  'All',
  'Phishing',
  'Malware',
  'Brute Force',
  'DDoS',
  'Botnet',
  'SQL Injection',
  'Ransomware',
  'Data Breach'
];

const SEVERITIES = ['All', 'Critical', 'High', 'Medium', 'Low'];

export default function ThreatsView({ currentUser }) {
  const isViewer = (currentUser?.role || '').toLowerCase() === 'viewer';
  const [events, setEvents] = useState([]);
  const [total, setTotal] = useState(0);
  const [threatFilter, setThreatFilter] = useState('All');
  const [severityFilter, setSeverityFilter] = useState('All');
  const [page, setPage] = useState(0);
  const limit = 25;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // New Event Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newDate, setNewDate] = useState(new Date().toISOString().split('T')[0]);
  const [newThreat, setNewThreat] = useState('Phishing');
  const [newSeverity, setNewSeverity] = useState('High');
  const [newSource, setNewSource] = useState('Firewall-IDS');
  const [newLocation, setNewLocation] = useState('North America');
  const [newCount, setNewCount] = useState(12);
  const [newDesc, setNewDesc] = useState('');
  const [modalLoading, setModalLoading] = useState(false);
  const [modalError, setModalError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const fetchEvents = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        limit,
        skip: page * limit,
      };
      if (threatFilter !== 'All') params.threat_type = threatFilter;
      if (severityFilter !== 'All') params.severity = severityFilter;

      const data = await getThreatEvents(params);
      setEvents(data.data);
      setTotal(data.total);
    } catch (err) {
      setError(err.message || 'Failed to fetch threat telemetry.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [threatFilter, severityFilter, page]);

  const handleCreateEvent = async (e) => {
    e.preventDefault();
    setModalLoading(true);
    setModalError(null);
    try {
      await createThreatEvent({
        date: newDate,
        threat_type: newThreat,
        severity: newSeverity,
        source: newSource,
        location: newLocation,
        count: Number(newCount),
        description: newDesc || `${newThreat} incident flagged via ${newSource}`
      });
      setSuccessMsg(`Successfully logged ${newThreat} event!`);
      setTimeout(() => setSuccessMsg(null), 4000);
      setIsModalOpen(false);
      fetchEvents();
    } catch (err) {
      setModalError(err.message || 'Failed to create threat event.');
    } finally {
      setModalLoading(false);
    }
  };

  const getSeverityBadgeClass = (sev) => {
    switch (sev) {
      case 'Critical': return 'badge-critical';
      case 'High': return 'badge-high';
      case 'Medium': return 'badge-medium';
      default: return 'badge-low';
    }
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Top Header & Actions */}
      <div className="glass-panel" style={{ padding: '1.25rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', color: '#fff' }}>SOC Threat Telemetry Logs</h2>
          <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>
            Total Indexed Events: <strong style={{ color: 'var(--accent-cyan)' }}>{total.toLocaleString()}</strong> records in database
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
          {/* Threat Type Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Vector:</span>
            <select
              value={threatFilter}
              onChange={(e) => { setThreatFilter(e.target.value); setPage(0); }}
              className="input-control"
              style={{ width: 'auto', padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}
              id="threat-filter-type"
            >
              {THREAT_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>

          {/* Severity Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Severity:</span>
            <select
              value={severityFilter}
              onChange={(e) => { setSeverityFilter(e.target.value); setPage(0); }}
              className="input-control"
              style={{ width: 'auto', padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}
              id="threat-filter-severity"
            >
              {SEVERITIES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>

          {/* Report Event Button (Analysts & Admins only) */}
          {!isViewer && (
            <button
              onClick={() => setIsModalOpen(true)}
              className="btn btn-primary"
              style={{ fontSize: '0.8rem', padding: '0.45rem 0.9rem' }}
              id="btn-report-incident"
            >
              <PlusCircle size={15} />
              <span>Ingest Incident</span>
            </button>
          )}
        </div>
      </div>

      {successMsg && (
        <div style={{
          background: 'rgba(16, 185, 129, 0.12)',
          border: '1px solid rgba(16, 185, 129, 0.4)',
          padding: '0.75rem 1rem',
          borderRadius: '8px',
          color: '#6ee7b7',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          fontSize: '0.825rem'
        }}>
          <CheckCircle size={16} />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Main Table */}
      <div className="glass-panel" style={{ padding: '1.25rem' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <RefreshCw size={28} color="#06b6d4" className="spin" style={{ animation: 'spin 1.5s linear infinite' }} />
            <p style={{ marginTop: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
              Querying telemetry indexes...
            </p>
          </div>
        ) : error ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: '#f87171' }}>
            <AlertTriangle size={28} style={{ margin: '0 auto 0.5rem' }} />
            <p>{error}</p>
          </div>
        ) : (
          <>
            <div className="soc-table-container">
              <table className="soc-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Threat Category</th>
                    <th>Severity Rating</th>
                    <th>Count</th>
                    <th>Detection Source</th>
                    <th>Geographic Origin</th>
                    <th>Telemetry Summary</th>
                  </tr>
                </thead>
                <tbody>
                  {events.length === 0 ? (
                    <tr>
                      <td colSpan={7} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                        No threat events matching filter parameters.
                      </td>
                    </tr>
                  ) : (
                    events.map((ev) => (
                      <tr key={ev.id}>
                        <td className="mono" style={{ color: '#fff', fontWeight: 600 }}>
                          {ev.date}
                        </td>
                        <td style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>
                          {ev.threat_type}
                        </td>
                        <td>
                          <span className={`badge ${getSeverityBadgeClass(ev.severity)}`}>
                            {ev.severity}
                          </span>
                        </td>
                        <td className="mono" style={{ fontWeight: 700, color: '#f8fafc' }}>
                          {ev.count}
                        </td>
                        <td style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                          {ev.source}
                        </td>
                        <td style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                          {ev.location}
                        </td>
                        <td style={{ color: 'var(--text-muted)', fontSize: '0.75rem', maxWidth: '300px' }}>
                          {ev.description}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginTop: '1.25rem',
              paddingTop: '0.75rem',
              borderTop: '1px solid var(--border-subtle)',
              fontSize: '0.8rem',
              color: 'var(--text-secondary)'
            }}>
              <div>
                Showing <strong style={{ color: '#fff' }}>{page * limit + 1}</strong> to <strong style={{ color: '#fff' }}>{Math.min((page + 1) * limit, total)}</strong> of <strong style={{ color: '#fff' }}>{total.toLocaleString()}</strong> records
              </div>

              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <button
                  disabled={page === 0}
                  onClick={() => setPage(page - 1)}
                  className="btn btn-secondary"
                  style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem' }}
                  id="btn-threats-prev"
                >
                  <ChevronLeft size={14} /> Previous
                </button>
                <span className="mono" style={{ padding: '0 0.5rem' }}>
                  Page {page + 1} / {totalPages || 1}
                </span>
                <button
                  disabled={page >= totalPages - 1}
                  onClick={() => setPage(page + 1)}
                  className="btn btn-secondary"
                  style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem' }}
                  id="btn-threats-next"
                >
                  Next <ChevronRight size={14} />
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Ingest Incident Modal */}
      {isModalOpen && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <PlusCircle size={20} color="var(--accent-cyan)" />
                <h3 style={{ color: '#fff' }}>Ingest Real-Time Incident</h3>
              </div>
              <button onClick={() => setIsModalOpen(false)} style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            {modalError && (
              <div style={{ background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.4)', padding: '0.6rem 0.9rem', borderRadius: '6px', color: '#fda4af', marginBottom: '1rem', fontSize: '0.8rem' }}>
                {modalError}
              </div>
            )}

            <form onSubmit={handleCreateEvent} style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                    Incident Date
                  </label>
                  <input
                    type="date"
                    required
                    value={newDate}
                    onChange={(e) => setNewDate(e.target.value)}
                    className="input-control"
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                    Incident Count
                  </label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={newCount}
                    onChange={(e) => setNewCount(e.target.value)}
                    className="input-control"
                  />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                    Threat Category
                  </label>
                  <select
                    value={newThreat}
                    onChange={(e) => setNewThreat(e.target.value)}
                    className="input-control"
                  >
                    {THREAT_TYPES.filter(t => t !== 'All').map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                    Severity
                  </label>
                  <select
                    value={newSeverity}
                    onChange={(e) => setNewSeverity(e.target.value)}
                    className="input-control"
                  >
                    {SEVERITIES.filter(s => s !== 'All').map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                    Telemetry Sensor / Source
                  </label>
                  <input
                    type="text"
                    required
                    value={newSource}
                    onChange={(e) => setNewSource(e.target.value)}
                    className="input-control"
                    placeholder="e.g. WAF-Gateway, EDR"
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                    Location
                  </label>
                  <input
                    type="text"
                    required
                    value={newLocation}
                    onChange={(e) => setNewLocation(e.target.value)}
                    className="input-control"
                    placeholder="e.g. Global, Europe"
                  />
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>
                  Incident Description
                </label>
                <input
                  type="text"
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  className="input-control"
                  placeholder="Optional detail on attack signatures or IP payloads"
                />
              </div>

              <button
                type="submit"
                disabled={modalLoading}
                className="btn btn-primary"
                style={{ width: '100%', marginTop: '0.5rem', padding: '0.65rem' }}
                id="btn-submit-incident"
              >
                {modalLoading ? 'Ingesting...' : 'Confirm Ingestion into MongoDB'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
