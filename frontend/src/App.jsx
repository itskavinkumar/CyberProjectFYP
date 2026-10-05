import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import OverviewView from './components/OverviewView';
import ForecastView from './components/ForecastView';
import ThreatsView from './components/ThreatsView';
import ModelsView from './components/ModelsView';
import DatasetsView from './components/DatasetsView';
import ReportsView from './components/ReportsView';
import AdminConsole from './components/AdminConsole';
import AuthModal from './components/AuthModal';
import { 
  checkHealth, 
  getStoredUser, 
  logoutUser 
} from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedThreatForForecast, setSelectedThreatForForecast] = useState('Phishing');
  const [currentUser, setCurrentUser] = useState(getStoredUser());
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [systemStatus, setSystemStatus] = useState(null);

  const isAdmin = (currentUser?.role || '').toLowerCase() === 'admin';

  // Feature 17 Frontend Role Guard: Redirect non-admins if activeTab is set to admin
  useEffect(() => {
    if (activeTab === 'admin' && !isAdmin) {
      setActiveTab('overview');
    }
  }, [currentUser, activeTab, isAdmin]);

  useEffect(() => {
    const pingBackend = async () => {
      try {
        const health = await checkHealth();
        setSystemStatus(health);
      } catch (err) {
        setSystemStatus({ status: 'disconnected', database: 'disconnected' });
      }
    };
    pingBackend();
    const interval = setInterval(pingBackend, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectThreatForForecast = (threatType) => {
    setSelectedThreatForForecast(threatType);
    setActiveTab('forecast');
  };

  const handleLogout = async () => {
    await logoutUser();
    setCurrentUser(null);
    if (activeTab === 'admin') {
      setActiveTab('overview');
    }
  };

  const handleAuthSuccess = (user) => {
    setCurrentUser(user);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Top Cyber Navigation Bar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        currentUser={currentUser}
        onOpenAuth={() => setIsAuthOpen(true)}
        onLogout={handleLogout}
        systemStatus={systemStatus}
      />

      {/* Main Content Viewport */}
      <main style={{ flex: 1, maxWidth: '1440px', width: '100%', margin: '0 auto', padding: '1.75rem 1.5rem' }}>
        {activeTab === 'overview' && (
          <OverviewView onSelectThreatForForecast={handleSelectThreatForForecast} />
        )}

        {activeTab === 'forecast' && (
          <ForecastView initialThreatType={selectedThreatForForecast} />
        )}

        {activeTab === 'threats' && (
          <ThreatsView currentUser={currentUser} />
        )}

        {activeTab === 'models' && (
          <ModelsView onSelectThreatForForecast={handleSelectThreatForForecast} />
        )}

        {activeTab === 'datasets' && (
          <DatasetsView currentUser={currentUser} />
        )}

        {activeTab === 'reports' && (
          <ReportsView currentUser={currentUser} />
        )}

        {activeTab === 'admin' && isAdmin && (
          <AdminConsole currentUser={currentUser} />
        )}
      </main>

      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onAuthSuccess={handleAuthSuccess}
      />

      {/* System Footer */}
      <footer style={{
        borderTop: '1px solid var(--border-subtle)',
        background: 'rgba(7, 10, 19, 0.9)',
        padding: '1.25rem 1.5rem',
        marginTop: '2rem'
      }}>
        <div style={{
          maxWidth: '1440px',
          margin: '0 auto',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '0.75rem',
          fontSize: '0.75rem',
          color: 'var(--text-muted)'
        }}>
          <div>
            <strong style={{ color: 'var(--text-secondary)' }}>CYBER THREAT FORECASTING SYSTEM</strong> — Academic FYP 2026
          </div>
          <div>
            Backend: <span style={{ color: 'var(--accent-cyan)' }}>FastAPI & Motor (MongoDB)</span> • ML Engine: <span style={{ color: 'var(--accent-purple)' }}>TensorFlow/Keras 3 (LSTM)</span> • Frontend: <span style={{ color: '#38bdf8' }}>React 19 & Chart.js</span>
          </div>
          <div style={{ fontFamily: 'var(--font-mono)' }}>
            SOC Status: <span style={{ color: '#34d399' }}>OPERATIONAL</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
