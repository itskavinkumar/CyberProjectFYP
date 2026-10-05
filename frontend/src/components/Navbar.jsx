import { 
  Shield, 
  Activity, 
  Cpu, 
  BarChart3, 
  LineChart, 
  Database, 
  Layers, 
  User, 
  LogOut, 
  CheckCircle2, 
  AlertCircle,
  FileText,
  ShieldCheck
} from 'lucide-react';

export default function Navbar({ 
  activeTab, 
  setActiveTab, 
  currentUser, 
  onOpenAuth, 
  onLogout,
  systemStatus 
}) {
  const userRole = (currentUser?.role || '').toLowerCase();
  const isAdmin = userRole === 'admin';
  const isViewer = userRole === 'viewer';

  const tabs = [
    { id: 'overview', label: 'SOC Overview', icon: BarChart3 },
    { id: 'forecast', label: 'AI Forecaster', icon: LineChart },
    { id: 'threats', label: 'Threat Telemetry', icon: Activity },
    { id: 'models', label: 'LSTM Registry', icon: Cpu },
  ];

  // Viewers do not have dataset ingestion/upload permissions
  if (!isViewer) {
    tabs.push({ id: 'datasets', label: 'Datasets', icon: Database });
  }

  // Reports section
  tabs.push({ id: 'reports', label: 'SOC Reports', icon: FileText });

  // Admin Console - ONLY visible to ADMIN users
  if (isAdmin) {
    tabs.push({ id: 'admin', label: 'Admin Console', icon: ShieldCheck, isAdminOnly: true });
  }

  return (
    <header style={{
      borderBottom: '1px solid var(--border-subtle)',
      background: 'rgba(7, 10, 19, 0.85)',
      backdropFilter: 'blur(16px)',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      <div style={{
        maxWidth: '1440px',
        margin: '0 auto',
        padding: '0.85rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div style={{
            background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.2) 0%, rgba(59, 130, 246, 0.2) 100%)',
            border: '1px solid var(--accent-cyan)',
            padding: '0.5rem',
            borderRadius: '10px',
            display: 'flex',
            boxShadow: '0 0 15px rgba(6, 182, 212, 0.3)'
          }}>
            <Shield size={24} color="#06b6d4" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <h1 style={{ fontSize: '1.25rem', color: '#ffffff', letterSpacing: '-0.02em' }}>
                CYBER<span style={{ color: 'var(--accent-cyan)' }}>GUARD</span> AI
              </h1>
              <span className="badge badge-low" style={{ fontSize: '0.65rem' }}>SOC v1.0</span>
            </div>
            <p style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
              Deep Learning Cyber Threat Forecasting & SOC Intelligence
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.35rem',
          background: 'rgba(15, 23, 42, 0.6)',
          padding: '0.3rem',
          borderRadius: '10px',
          border: '1px solid var(--border-subtle)'
        }}>
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            const isSpecialAdmin = tab.isAdminOnly;
            let bgStyle = 'transparent';
            let textColor = 'var(--text-secondary)';
            let borderBottom = '2px solid transparent';

            if (isActive) {
              if (isSpecialAdmin) {
                bgStyle = 'linear-gradient(135deg, rgba(139, 92, 246, 0.3) 0%, rgba(244, 63, 94, 0.3) 100%)';
                textColor = '#f43f5e';
                borderBottom = '2px solid #f43f5e';
              } else {
                bgStyle = 'linear-gradient(135deg, rgba(6, 182, 212, 0.25) 0%, rgba(37, 99, 235, 0.25) 100%)';
                textColor = 'var(--accent-cyan)';
                borderBottom = '2px solid var(--accent-cyan)';
              }
            } else if (isSpecialAdmin) {
              textColor = '#c084fc';
            }

            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                id={`nav-tab-${tab.id}`}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.45rem',
                  padding: '0.45rem 0.95rem',
                  borderRadius: '7px',
                  border: isSpecialAdmin && !isActive ? '1px solid rgba(139, 92, 246, 0.4)' : '1px solid transparent',
                  fontSize: '0.825rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  background: bgStyle,
                  color: textColor,
                  borderBottom: borderBottom
                }}
              >
                <Icon size={16} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right Status & Auth */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {/* Heartbeat Badge */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            background: 'rgba(16, 185, 129, 0.08)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
            padding: '0.35rem 0.75rem',
            borderRadius: '9999px',
            fontSize: '0.75rem'
          }}>
            <span className="pulse-dot" />
            <span style={{ color: '#34d399', fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
              {systemStatus?.database === 'connected' ? 'LIVE TELEMETRY' : 'CONNECTING'}
            </span>
          </div>

          {/* User Button */}
          {currentUser ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                  {currentUser.name}
                </div>
                <div style={{ fontSize: '0.7rem', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.3rem' }}>
                  <span className={`badge ${currentUser.role === 'admin' ? 'badge-critical' : (currentUser.role === 'analyst' ? 'badge-medium' : 'badge-low')}`} style={{ fontSize: '0.6rem', padding: '0.1rem 0.4rem' }}>
                    {currentUser.role}
                  </span>
                </div>
              </div>
              <button
                onClick={onLogout}
                title="Sign out of SOC session"
                className="btn btn-secondary"
                style={{ padding: '0.4rem 0.65rem' }}
                id="btn-logout"
              >
                <LogOut size={15} />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="btn btn-primary"
              id="btn-login-modal"
              style={{ padding: '0.45rem 1rem', fontSize: '0.8rem' }}
            >
              <User size={15} />
              <span>SOC Access</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
