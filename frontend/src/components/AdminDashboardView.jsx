import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Users, 
  UserCheck, 
  UserX, 
  Key, 
  AlertTriangle, 
  LineChart, 
  Database, 
  FileText, 
  RefreshCw, 
  ArrowRight,
  Clock,
  Shield,
  Activity
} from 'lucide-react';
import { getAdminDashboard } from '../api';

export default function AdminDashboardView({ onNavigateTab }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getAdminDashboard();
      setData(res);
    } catch (err) {
      setError(err.message || 'Failed to load SOC administration metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    try {
      const d = new Date(dateStr);
      return d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return dateStr;
    }
  };

  if (loading) {
    return (
      <div className="glass-panel" style={{ padding: '4rem 2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        <RefreshCw className="spin" size={32} style={{ margin: '0 auto 1rem auto', color: 'var(--accent-cyan)' }} />
        <h3 style={{ color: '#fff', fontSize: '1.2rem', marginBottom: '0.5rem' }}>Synchronizing SOC Administration Console</h3>
        <p style={{ fontSize: '0.85rem' }}>Aggregating operator telemetry, session counts, and audit logs...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="glass-panel" style={{ padding: '2rem', border: '1px solid rgba(244, 63, 94, 0.4)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: '#fda4af', marginBottom: '1rem' }}>
          <AlertTriangle size={24} />
          <h3 style={{ fontSize: '1.15rem' }}>Administration Console Error</h3>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
          {error || 'Unable to retrieve administrator metrics. Please ensure you are authenticated with Administrator privileges.'}
        </p>
        <button onClick={fetchDashboard} className="btn btn-primary">
          <RefreshCw size={16} /> Retry
        </button>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Console Header Banner */}
      <div className="glass-panel glass-panel-glow" style={{ padding: '1.75rem', position: 'relative', overflow: 'hidden' }}>
        <div style={{
          position: 'absolute',
          right: '-20px',
          top: '-20px',
          width: '180px',
          height: '180px',
          background: 'radial-gradient(circle, rgba(6, 182, 212, 0.15) 0%, transparent 70%)',
          pointerEvents: 'none'
        }} />

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', position: 'relative', zIndex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
            <div style={{
              background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.25) 0%, rgba(139, 92, 246, 0.25) 100%)',
              border: '1px solid var(--accent-cyan)',
              padding: '0.65rem',
              borderRadius: '12px',
              display: 'flex',
              boxShadow: '0 0 20px rgba(6, 182, 212, 0.2)'
            }}>
              <ShieldCheck size={28} color="#06b6d4" />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                <h2 style={{ fontSize: '1.4rem', color: '#fff', letterSpacing: '-0.02em' }}>
                  SOC SECURITY & ACCESS GOVERNANCE CONSOLE
                </h2>
                <span className="badge badge-low" style={{ fontSize: '0.65rem' }}>
                  ADMIN ROOT
                </span>
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                Holistic management of operator identities, session authorization events, ML forecasting pipelines, and tamper-resistant audit logs.
              </p>
            </div>
          </div>

          <button onClick={fetchDashboard} className="btn btn-secondary" title="Refresh Telemetry">
            <RefreshCw size={16} />
            <span>Sync SOC Data</span>
          </button>
        </div>
      </div>

      {/* Primary Key Metrics Grid (8 Cards as requested in Feature 15) */}
      <div className="grid-metrics" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))' }}>
        {/* Card 1: Registered Users */}
        <div 
          className="glass-panel" 
          style={{ padding: '1.25rem', cursor: 'pointer' }}
          onClick={() => onNavigateTab && onNavigateTab('users')}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
              Registered Users
            </span>
            <div style={{ background: 'rgba(6, 182, 212, 0.15)', padding: '0.4rem', borderRadius: '6px' }}>
              <Users size={18} color="#06b6d4" />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 700, color: '#fff', fontFamily: 'var(--font-mono)' }}>
            {data.registered_users}
          </div>
          <div style={{ fontSize: '0.725rem', color: 'var(--accent-cyan)', marginTop: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <span>Manage accounts</span> <ArrowRight size={12} />
          </div>
        </div>

        {/* Card 2: Active Operators */}
        <div 
          className="glass-panel" 
          style={{ padding: '1.25rem', cursor: 'pointer' }}
          onClick={() => onNavigateTab && onNavigateTab('users')}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
              Active Accounts
            </span>
            <div style={{ background: 'rgba(16, 185, 129, 0.15)', padding: '0.4rem', borderRadius: '6px' }}>
              <UserCheck size={18} color="#10b981" />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 700, color: '#34d399', fontFamily: 'var(--font-mono)' }}>
            {data.active_users}
          </div>
          <div style={{ fontSize: '0.725rem', color: '#a7f3d0', marginTop: '0.35rem' }}>
            Verified operational status
          </div>
        </div>

        {/* Card 3: Disabled Accounts */}
        <div 
          className="glass-panel" 
          style={{ padding: '1.25rem', cursor: 'pointer' }}
          onClick={() => onNavigateTab && onNavigateTab('users')}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
              Disabled Accounts
            </span>
            <div style={{ background: 'rgba(244, 63, 94, 0.15)', padding: '0.4rem', borderRadius: '6px' }}>
              <UserX size={18} color="#f43f5e" />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 700, color: data.disabled_users > 0 ? '#f87171' : 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            {data.disabled_users}
          </div>
          <div style={{ fontSize: '0.725rem', color: data.disabled_users > 0 ? '#fda4af' : 'var(--text-muted)', marginTop: '0.35rem' }}>
            Barred from authentication
          </div>
        </div>

        {/* Card 4: Today's Logins */}
        <div 
          className="glass-panel" 
          style={{ padding: '1.25rem', cursor: 'pointer' }}
          onClick={() => onNavigateTab && onNavigateTab('login-history')}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
              Today's Logins
            </span>
            <div style={{ background: 'rgba(59, 130, 246, 0.15)', padding: '0.4rem', borderRadius: '6px' }}>
              <Key size={18} color="#3b82f6" />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 700, color: '#60a5fa', fontFamily: 'var(--font-mono)' }}>
            {data.today_logins}
          </div>
          <div style={{ fontSize: '0.725rem', color: 'var(--accent-blue)', marginTop: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <span>View session trail</span> <ArrowRight size={12} />
          </div>
        </div>

        {/* Card 5: Failed Logins */}
        <div 
          className="glass-panel" 
          style={{ padding: '1.25rem', cursor: 'pointer' }}
          onClick={() => onNavigateTab && onNavigateTab('login-history')}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
              Failed Logins Today
            </span>
            <div style={{ background: 'rgba(245, 158, 11, 0.15)', padding: '0.4rem', borderRadius: '6px' }}>
              <AlertTriangle size={18} color="#f59e0b" />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 700, color: data.failed_logins > 0 ? '#fbbf24' : '#34d399', fontFamily: 'var(--font-mono)' }}>
            {data.failed_logins}
          </div>
          <div style={{ fontSize: '0.725rem', color: data.failed_logins > 0 ? '#fde68a' : 'var(--text-muted)', marginTop: '0.35rem' }}>
            {data.failed_logins > 0 ? 'Requires SOC inspection' : 'Zero auth anomalies'}
          </div>
        </div>

        {/* Card 6: Forecasts Today */}
        <div 
          className="glass-panel" 
          style={{ padding: '1.25rem', cursor: 'pointer' }}
          onClick={() => onNavigateTab && onNavigateTab('audit-logs')}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
              Forecasts Today
            </span>
            <div style={{ background: 'rgba(139, 92, 246, 0.15)', padding: '0.4rem', borderRadius: '6px' }}>
              <LineChart size={18} color="#8b5cf6" />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 700, color: '#c084fc', fontFamily: 'var(--font-mono)' }}>
            {data.today_forecasts}
          </div>
          <div style={{ fontSize: '0.725rem', color: 'var(--accent-purple)', marginTop: '0.35rem' }}>
            LSTM inferences run
          </div>
        </div>

        {/* Card 7: Datasets */}
        <div 
          className="glass-panel" 
          style={{ padding: '1.25rem', cursor: 'pointer' }}
          onClick={() => onNavigateTab && onNavigateTab('audit-logs')}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
              Datasets Ingested
            </span>
            <div style={{ background: 'rgba(16, 185, 129, 0.15)', padding: '0.4rem', borderRadius: '6px' }}>
              <Database size={18} color="#10b981" />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 700, color: '#fff', fontFamily: 'var(--font-mono)' }}>
            {data.total_datasets}
          </div>
          <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Validated threat datasets
          </div>
        </div>

        {/* Card 8: Reports */}
        <div 
          className="glass-panel" 
          style={{ padding: '1.25rem', cursor: 'pointer' }}
          onClick={() => onNavigateTab && onNavigateTab('reports-history')}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
              Reports Compiled
            </span>
            <div style={{ background: 'rgba(56, 189, 248, 0.15)', padding: '0.4rem', borderRadius: '6px' }}>
              <FileText size={18} color="#38bdf8" />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 700, color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>
            {data.total_reports}
          </div>
          <div style={{ fontSize: '0.725rem', color: '#7dd3fc', marginTop: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <span>Review archives</span> <ArrowRight size={12} />
          </div>
        </div>
      </div>

      {/* Split Streams: Recent Login Activity vs Recent Audit Activity */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(480px, 1fr))', gap: '1.5rem' }}>
        {/* Stream 1: Recent Login Activity */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Key size={18} color="#3b82f6" />
              <h3 style={{ fontSize: '1rem', color: '#fff' }}>Recent Authentication Activity</h3>
            </div>
            <button 
              onClick={() => onNavigateTab && onNavigateTab('login-history')}
              className="btn btn-secondary" 
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }}
            >
              View Full History <ArrowRight size={13} />
            </button>
          </div>

          <div style={{ flex: 1, overflowX: 'auto' }}>
            {data.recent_logins.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textAlign: 'center', padding: '2rem' }}>
                No recent logins recorded.
              </p>
            ) : (
              <table className="soc-table" style={{ fontSize: '0.8rem' }}>
                <thead>
                  <tr>
                    <th>Operator</th>
                    <th>Action</th>
                    <th>Time</th>
                    <th>Result</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent_logins.map((ev) => (
                    <tr key={ev.id}>
                      <td>
                        <div style={{ fontWeight: 600, color: '#fff' }}>{ev.user_name || ev.email || 'Unknown'}</div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{ev.email || ev.ip_address}</div>
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>{ev.action}</td>
                      <td style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>{formatDate(ev.timestamp)}</td>
                      <td>
                        <span className={`badge ${ev.status === 'success' ? 'badge-low' : 'badge-critical'}`} style={{ fontSize: '0.65rem' }}>
                          {ev.status.toUpperCase()}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Stream 2: Recent Security Audit Trail */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Shield size={18} color="#8b5cf6" />
              <h3 style={{ fontSize: '1rem', color: '#fff' }}>Recent SOC Audit Events</h3>
            </div>
            <button 
              onClick={() => onNavigateTab && onNavigateTab('audit-logs')}
              className="btn btn-secondary" 
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }}
            >
              View Complete Audit <ArrowRight size={13} />
            </button>
          </div>

          <div style={{ flex: 1, overflowX: 'auto' }}>
            {data.recent_audits.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textAlign: 'center', padding: '2rem' }}>
                No audit events recorded yet.
              </p>
            ) : (
              <table className="soc-table" style={{ fontSize: '0.8rem' }}>
                <thead>
                  <tr>
                    <th>Operator</th>
                    <th>Action</th>
                    <th>Resource</th>
                    <th>Time</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent_audits.map((a) => (
                    <tr key={a.id}>
                      <td>
                        <div style={{ fontWeight: 600, color: '#fff' }}>{a.user_name || 'System'}</div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{a.role}</div>
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--accent-cyan)' }}>
                        {a.action}
                      </td>
                      <td style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                        {a.resource_type || '-'}
                      </td>
                      <td style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>
                        {formatDate(a.timestamp)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
