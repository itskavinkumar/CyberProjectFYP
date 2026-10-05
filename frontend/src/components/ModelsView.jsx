import React, { useState, useEffect } from 'react';
import { 
  Cpu, 
  CheckCircle2, 
  AlertCircle, 
  ArrowRight, 
  RefreshCw, 
  Layers, 
  BarChart, 
  ShieldCheck 
} from 'lucide-react';
import { getModelsStatus } from '../api';

export default function ModelsView({ onSelectThreatForForecast }) {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchModels = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getModelsStatus();
      setModels(data.models || []);
    } catch (err) {
      setError(err.message || 'Failed to load model registry.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Header */}
      <div className="glass-panel" style={{ padding: '1.25rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', color: '#fff' }}>LSTM Deep Learning Model Registry</h2>
          <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>
            8/8 Specialized Neural Forecasting Networks • Trained with Keras 3 & Huber Loss
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <span className="badge badge-low" style={{ fontSize: '0.75rem' }}>
            <ShieldCheck size={14} /> All 8 Models Deployed
          </span>
          <button onClick={fetchModels} className="btn btn-secondary" style={{ padding: '0.4rem 0.75rem' }}>
            <RefreshCw size={14} /> Refresh
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem' }}>
          <RefreshCw size={32} color="#06b6d4" className="spin" style={{ animation: 'spin 1.5s linear infinite' }} />
          <p style={{ marginTop: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            Querying active LSTM weights and evaluation matrices...
          </p>
        </div>
      ) : error ? (
        <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center', color: '#f87171' }}>
          <AlertCircle size={32} style={{ margin: '0 auto 0.5rem' }} />
          <p>{error}</p>
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '1.25rem'
        }}>
          {models.map((m) => {
            const metrics = m.metrics || {};
            const slug = m.threat_type.toLowerCase().replace(/\s+/g, '_');
            return (
              <div 
                key={m.threat_type} 
                className="glass-panel" 
                style={{ 
                  padding: '1.5rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  borderTop: '3px solid var(--accent-cyan)'
                }}
              >
                <div>
                  {/* Top card bar */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                    <div>
                      <h3 style={{ fontSize: '1.15rem', color: '#fff' }}>{m.threat_type}</h3>
                      <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                        {slug}_lstm.keras
                      </div>
                    </div>
                    <span className="badge badge-low" style={{ fontSize: '0.65rem' }}>
                      <CheckCircle2 size={12} /> Active
                    </span>
                  </div>

                  {/* Architecture spec */}
                  <div style={{
                    background: 'rgba(15, 23, 42, 0.6)',
                    padding: '0.65rem 0.85rem',
                    borderRadius: '8px',
                    border: '1px solid var(--border-subtle)',
                    marginBottom: '1rem',
                    fontSize: '0.75rem',
                    color: 'var(--text-secondary)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--accent-cyan)', fontWeight: 600, marginBottom: '0.2rem' }}>
                      <Layers size={13} /> 2-Layer Stacked LSTM (64, 32)
                    </div>
                    <div>Sequence: 30-day window • Dropout: 0.20 • Huber Loss</div>
                  </div>

                  {/* Metrics grid */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginBottom: '1.25rem' }}>
                    <div style={{ background: 'rgba(30, 41, 59, 0.4)', padding: '0.5rem', borderRadius: '6px' }}>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Test MAE</div>
                      <div className="mono" style={{ fontSize: '1.05rem', fontWeight: 700, color: '#38bdf8' }}>
                        {metrics.mae ? metrics.mae.toFixed(2) : 'N/A'}
                      </div>
                    </div>

                    <div style={{ background: 'rgba(30, 41, 59, 0.4)', padding: '0.5rem', borderRadius: '6px' }}>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Test RMSE</div>
                      <div className="mono" style={{ fontSize: '1.05rem', fontWeight: 700, color: '#c084fc' }}>
                        {metrics.rmse ? metrics.rmse.toFixed(2) : 'N/A'}
                      </div>
                    </div>

                    <div style={{ background: 'rgba(30, 41, 59, 0.4)', padding: '0.5rem', borderRadius: '6px' }}>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Test MAPE</div>
                      <div className="mono" style={{ fontSize: '1.05rem', fontWeight: 700, color: '#34d399' }}>
                        {metrics.mape ? `${metrics.mape.toFixed(2)}%` : 'N/A'}
                      </div>
                    </div>

                    <div style={{ background: 'rgba(30, 41, 59, 0.4)', padding: '0.5rem', borderRadius: '6px' }}>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>R² Score</div>
                      <div className="mono" style={{ fontSize: '1.05rem', fontWeight: 700, color: metrics.r2_score > 0 ? '#34d399' : '#fca5a5' }}>
                        {metrics.r2_score ? metrics.r2_score.toFixed(3) : 'N/A'}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Card Button */}
                <button
                  onClick={() => onSelectThreatForForecast(m.threat_type)}
                  className="btn btn-primary"
                  style={{ width: '100%', fontSize: '0.8rem', padding: '0.5rem' }}
                >
                  <span>Launch {m.threat_type} Forecaster</span>
                  <ArrowRight size={14} />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
