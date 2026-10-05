import React, { useState } from 'react';
import { X, Shield, Lock, Mail, User, CheckCircle, AlertTriangle } from 'lucide-react';
import { loginUser, registerUser } from '../api';

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('analyst');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      let data;
      if (isLogin) {
        data = await loginUser(email, password);
      } else {
        data = await registerUser(name, email, password, role);
      }
      onAuthSuccess(data.user);
      onClose();
    } catch (err) {
      setError(err.message || 'Authentication failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handlePreFill = (demoRole) => {
    if (demoRole === 'analyst') {
      setEmail('analyst@soc.defense.gov');
      setPassword('CyberAnalyst2026!');
      setName('SOC Threat Analyst');
      setRole('analyst');
    } else {
      setEmail('admin@soc.defense.gov');
      setPassword('CyberAdmin2026!');
      setName('SOC Director');
      setRole('admin');
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <div style={{
              background: 'rgba(6, 182, 212, 0.15)',
              padding: '0.5rem',
              borderRadius: '8px',
              border: '1px solid var(--accent-cyan)'
            }}>
              <Shield size={20} color="#06b6d4" />
            </div>
            <div>
              <h2 style={{ fontSize: '1.15rem', color: '#fff' }}>
                {isLogin ? 'SOC Analyst Sign In' : 'Register SOC Operator'}
              </h2>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {isLogin ? 'Access secure threat intelligence and forecasting telemetry' : 'Create new authorized SOC personnel account'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Error Alert */}
        {error && (
          <div style={{
            background: 'rgba(244, 63, 94, 0.12)',
            border: '1px solid rgba(244, 63, 94, 0.4)',
            padding: '0.75rem 1rem',
            borderRadius: '8px',
            marginBottom: '1rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.65rem',
            fontSize: '0.825rem',
            color: '#fca5a5'
          }}>
            <AlertTriangle size={18} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {!isLogin && (
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
                Full Name / Callsign
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  type="text"
                  required
                  placeholder="e.g. Lead Analyst Marcus"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="input-control"
                  id="auth-input-name"
                />
              </div>
            </div>
          )}

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              SOC Email Address
            </label>
            <input
              type="email"
              required
              placeholder="operator@soc.defense.gov"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input-control"
              id="auth-input-email"
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
              Access Password
            </label>
            <input
              type="password"
              required
              placeholder="••••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-control"
              id="auth-input-password"
            />
          </div>

          {!isLogin && (
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.35rem' }}>
                Operational Role
              </label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="input-control"
                id="auth-select-role"
              >
                <option value="analyst">Cyber Threat Analyst (Operational)</option>
                <option value="viewer">Intelligence Auditor (Read-Only)</option>
              </select>
              <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
                * SOC Administrator accounts cannot be self-registered publicly. They must be provisioned by an existing Administrator.
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '0.5rem', padding: '0.75rem' }}
            id="auth-btn-submit"
          >
            {loading ? 'Authenticating...' : (isLogin ? 'Sign In to Terminal' : 'Create Authorized Account')}
          </button>
        </form>

        {/* Quick Pre-fills */}
        <div style={{
          marginTop: '1.25rem',
          paddingTop: '1rem',
          borderTop: '1px solid var(--border-subtle)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '0.75rem'
        }}>
          <button
            type="button"
            onClick={() => setIsLogin(!isLogin)}
            style={{ background: 'none', border: 'none', color: 'var(--accent-cyan)', cursor: 'pointer', fontWeight: 600 }}
          >
            {isLogin ? "Need an account? Register" : "Already registered? Sign In"}
          </button>

          <div style={{ display: 'flex', gap: '0.4rem' }}>
            <button
              type="button"
              onClick={() => handlePreFill('analyst')}
              style={{ background: 'rgba(51, 65, 85, 0.4)', border: 'none', color: 'var(--text-secondary)', padding: '0.2rem 0.5rem', borderRadius: '4px', cursor: 'pointer' }}
            >
              Demo Analyst
            </button>
            <button
              type="button"
              onClick={() => handlePreFill('admin')}
              style={{ background: 'rgba(51, 65, 85, 0.4)', border: 'none', color: 'var(--text-secondary)', padding: '0.2rem 0.5rem', borderRadius: '4px', cursor: 'pointer' }}
            >
              Demo Admin
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
