import React, { useState, useEffect } from 'react';
import { 
  LineChart, 
  Cpu, 
  Calendar, 
  TrendingUp, 
  TrendingDown, 
  ShieldAlert, 
  Activity, 
  Info, 
  AlertTriangle,
  RefreshCw,
  CheckCircle2
} from 'lucide-react';
import { Line } from 'react-chartjs-2';
import { generateForecast } from '../api';

const THREAT_CATEGORIES = [
  'Phishing',
  'Malware',
  'Brute Force',
  'DDoS',
  'Botnet',
  'SQL Injection',
  'Ransomware',
  'Data Breach'
];

const HORIZONS = [
  { days: 7, label: '7 Days', desc: 'Tactical Sprint' },
  { days: 14, label: '14 Days', desc: 'Operational Window' },
  { days: 30, label: '30 Days', desc: 'Strategic Horizon' }
];

export default function ForecastView({ initialThreatType = 'Phishing' }) {
  const [selectedThreat, setSelectedThreat] = useState(initialThreatType);
  const [selectedHorizon, setSelectedHorizon] = useState(30);
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (initialThreatType) {
      setSelectedThreat(initialThreatType);
    }
  }, [initialThreatType]);

  const runForecast = async (threat = selectedThreat, days = selectedHorizon) => {
    setLoading(true);
    setError(null);
    try {
      const data = await generateForecast(threat, days);
      setForecastData(data);
    } catch (err) {
      setError(err.message || `Failed to generate forecast for ${threat}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runForecast(selectedThreat, selectedHorizon);
  }, [selectedThreat, selectedHorizon]);

  // Construct combined historical + forecast datasets for Chart.js
  let chartData = null;
  let chartOptions = null;

  if (forecastData) {
    const histPoints = forecastData.historical_data.slice(-30);
    const fcPoints = forecastData.forecast_data;

    const allLabels = [
      ...histPoints.map(p => p.date),
      ...fcPoints.map(p => p.date)
    ];

    // Historical dataset: filled up to last historical date, then null
    const histCounts = [
      ...histPoints.map(p => p.count),
      ...fcPoints.map(() => null)
    ];

    // Bridge point so line connects smoothly
    const lastHistVal = histPoints[histPoints.length - 1].count;

    // Forecast line: null during historical, then starts at bridge point
    const forecastCounts = [
      ...histPoints.slice(0, -1).map(() => null),
      lastHistVal,
      ...fcPoints.map(p => p.predicted_count)
    ];

    // Upper and lower bounds for confidence cone
    const upperBounds = [
      ...histPoints.slice(0, -1).map(() => null),
      lastHistVal,
      ...fcPoints.map(p => p.upper_bound)
    ];

    const lowerBounds = [
      ...histPoints.slice(0, -1).map(() => null),
      lastHistVal,
      ...fcPoints.map(p => p.lower_bound)
    ];

    chartData = {
      labels: allLabels,
      datasets: [
        {
          label: 'Observed Daily Incidents',
          data: histCounts,
          borderColor: '#06b6d4',
          backgroundColor: 'rgba(6, 182, 212, 0.1)',
          borderWidth: 2,
          pointRadius: 2,
          pointHoverRadius: 5,
          tension: 0.25,
        },
        {
          label: 'AI LSTM Forecast',
          data: forecastCounts,
          borderColor: '#a855f7',
          backgroundColor: 'rgba(168, 85, 247, 0.1)',
          borderWidth: 2.5,
          borderDash: [5, 4],
          pointRadius: 4,
          pointHoverRadius: 7,
          pointBackgroundColor: '#c084fc',
          tension: 0.25,
        },
        {
          label: '95% Upper Bound',
          data: upperBounds,
          borderColor: 'rgba(168, 85, 247, 0.35)',
          borderWidth: 1,
          borderDash: [2, 2],
          pointRadius: 0,
          fill: '+1', // Fill down to lower bound
          backgroundColor: 'rgba(168, 85, 247, 0.12)',
          tension: 0.25,
        },
        {
          label: '95% Lower Bound',
          data: lowerBounds,
          borderColor: 'rgba(168, 85, 247, 0.35)',
          borderWidth: 1,
          borderDash: [2, 2],
          pointRadius: 0,
          fill: false,
          tension: 0.25,
        }
      ]
    };

    chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: '#94a3b8',
            font: { family: 'Inter', size: 12 },
            boxWidth: 14,
            usePointStyle: true
          }
        },
        tooltip: {
          backgroundColor: '#0f172a',
          borderColor: '#a855f7',
          borderWidth: 1,
          padding: 12,
          titleFont: { family: 'JetBrains Mono', size: 12 },
          bodyFont: { family: 'Inter', size: 12 },
          callbacks: {
            label: function(context) {
              const label = context.dataset.label || '';
              const val = context.parsed.y;
              if (val === null || val === undefined) return null;
              return `${label}: ${val.toFixed(1)} incidents`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(51, 65, 85, 0.2)' },
          ticks: { color: '#64748b', maxTicksLimit: 12, font: { family: 'JetBrains Mono', size: 10 } }
        },
        y: {
          grid: { color: 'rgba(51, 65, 85, 0.2)' },
          ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono', size: 10 } }
        }
      }
    };
  }

  const riskBadgeClass = 
    forecastData?.risk_level === 'Critical' ? 'badge-critical' :
    forecastData?.risk_level === 'High' ? 'badge-high' :
    forecastData?.risk_level === 'Medium' ? 'badge-medium' : 'badge-low';

  const trendBadgeClass = 
    forecastData?.trend_direction === 'Increasing' ? 'badge-trend-up' :
    forecastData?.trend_direction === 'Decreasing' ? 'badge-trend-down' : 'badge-trend-stable';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Category & Horizon Control Panel */}
      <div className="glass-panel" style={{ padding: '1.25rem 1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
          <div>
            <h2 style={{ fontSize: '1.2rem', color: '#fff' }}>LSTM Deep Learning Forecaster</h2>
            <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>
              Select threat category and projection horizon for recursive multi-step forecasting
            </p>
          </div>
          {/* Horizon Selection Buttons */}
          <div style={{ display: 'flex', gap: '0.5rem', background: 'rgba(15, 23, 42, 0.7)', padding: '0.3rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            {HORIZONS.map((h) => (
              <button
                key={h.days}
                onClick={() => setSelectedHorizon(h.days)}
                id={`btn-horizon-${h.days}`}
                style={{
                  padding: '0.45rem 0.85rem',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  borderRadius: '6px',
                  border: 'none',
                  cursor: 'pointer',
                  background: selectedHorizon === h.days ? 'linear-gradient(135deg, #a855f7 0%, #3b82f6 100%)' : 'transparent',
                  color: selectedHorizon === h.days ? '#fff' : 'var(--text-secondary)',
                  transition: 'all 0.2s ease'
                }}
              >
                {h.label}
              </button>
            ))}
          </div>
        </div>

        {/* Threat Category Pills */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {THREAT_CATEGORIES.map((cat) => {
            const isSelected = selectedThreat === cat;
            return (
              <button
                key={cat}
                onClick={() => setSelectedThreat(cat)}
                id={`btn-threat-${cat.toLowerCase().replace(/\s+/g, '-')}`}
                style={{
                  padding: '0.45rem 0.95rem',
                  borderRadius: '9999px',
                  fontSize: '0.825rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  border: isSelected ? '1px solid #a855f7' : '1px solid var(--border-subtle)',
                  background: isSelected ? 'rgba(168, 85, 247, 0.18)' : 'rgba(15, 23, 42, 0.6)',
                  color: isSelected ? '#c084fc' : 'var(--text-secondary)',
                  boxShadow: isSelected ? '0 0 12px rgba(168, 85, 247, 0.3)' : 'none',
                  transition: 'all 0.2s ease'
                }}
              >
                {cat}
              </button>
            );
          })}
        </div>
      </div>

      {loading && (
        <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
          <RefreshCw size={36} color="#a855f7" className="spin" style={{ animation: 'spin 1.5s linear infinite' }} />
          <p style={{ marginTop: '0.75rem', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            Executing 2-layer stacked LSTM inference for {selectedThreat} ({selectedHorizon} days)...
          </p>
        </div>
      )}

      {error && (
        <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center', border: '1px solid var(--accent-rose)' }}>
          <AlertTriangle size={36} color="#f43f5e" style={{ margin: '0 auto 0.75rem' }} />
          <h3 style={{ color: '#fff' }}>Forecast Computation Error</h3>
          <p style={{ color: 'var(--text-secondary)', margin: '0.5rem 0 1rem' }}>{error}</p>
          <button onClick={() => runForecast()} className="btn btn-primary">
            Retry Inference
          </button>
        </div>
      )}

      {forecastData && !loading && (
        <>
          {/* Key Forecast Summary Highlights */}
          <div className="grid-metrics">
            {/* Risk Card */}
            <div className="glass-panel" style={{ padding: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                  Risk Assessment
                </span>
                <span className={`badge ${riskBadgeClass}`}>
                  {forecastData.risk_level}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginTop: '0.5rem' }}>
                <span style={{ fontSize: '1.85rem', fontWeight: 800, color: '#fff', fontFamily: 'var(--font-mono)' }}>
                  {forecastData.summary_stats.risk_score}
                </span>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>/ 100 Risk Score</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginTop: '0.35rem' }}>
                <span className={`badge ${trendBadgeClass}`} style={{ fontSize: '0.7rem' }}>
                  {forecastData.trend_direction}
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {forecastData.summary_stats.predicted_change_pct > 0 ? `+${forecastData.summary_stats.predicted_change_pct}%` : `${forecastData.summary_stats.predicted_change_pct}%`} vs lookback
                </span>
              </div>
            </div>

            {/* Peak Prediction */}
            <div className="glass-panel" style={{ padding: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                  Peak Projected Incident
                </span>
                <Calendar size={18} color="var(--accent-purple)" />
              </div>
              <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#c084fc', marginTop: '0.5rem', fontFamily: 'var(--font-mono)' }}>
                {forecastData.summary_stats.peak_forecast_count}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
                Forecast Date: <strong style={{ color: '#fff' }}>{forecastData.summary_stats.peak_forecast_date}</strong>
              </div>
            </div>

            {/* Projected Average */}
            <div className="glass-panel" style={{ padding: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                  Projected Daily Average
                </span>
                <Activity size={18} color="var(--accent-cyan)" />
              </div>
              <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#38bdf8', marginTop: '0.5rem', fontFamily: 'var(--font-mono)' }}>
                {forecastData.summary_stats.avg_forecast_count}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
                Historical Baseline: {forecastData.summary_stats.avg_historical_count} / day
              </div>
            </div>

            {/* Model Architecture & Validation MAE */}
            <div className="glass-panel" style={{ padding: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                  Model Accuracy (Test Split)
                </span>
                <Cpu size={18} color="var(--accent-emerald)" />
              </div>
              <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#34d399', marginTop: '0.5rem', fontFamily: 'var(--font-mono)' }}>
                MAE: {forecastData.evaluation_metrics?.mae}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
                RMSE: {forecastData.evaluation_metrics?.rmse} | MAPE: {forecastData.evaluation_metrics?.mape}%
              </div>
            </div>
          </div>

          {/* Interactive Chart Canvas */}
          <div className="glass-panel" style={{ padding: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div>
                <h3 style={{ fontSize: '1.15rem', color: '#fff' }}>
                  {selectedThreat} Threat Forecast ({selectedHorizon} Days)
                </h3>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Solid Line: Observed 30-Day History • Dashed Line: AI Projected Trend • Shaded Band: 95% Confidence Interval
                </p>
              </div>
              <span className="badge badge-medium">
                {selectedHorizon}-Day Projection
              </span>
            </div>
            <div style={{ height: '360px', width: '100%' }}>
              <Line data={chartData} options={chartOptions} />
            </div>
          </div>

          {/* Forecast Data Breakdown Table */}
          <div className="glass-panel" style={{ padding: '1.5rem' }}>
            <h3 style={{ fontSize: '1.05rem', color: '#fff', marginBottom: '0.25rem' }}>
              Forecasted Projection Timetable
            </h3>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
              Chronological day-by-day forecasted incidents with confidence thresholds
            </p>
            <div className="soc-table-container" style={{ maxHeight: '280px' }}>
              <table className="soc-table">
                <thead>
                  <tr>
                    <th>Day #</th>
                    <th>Projected Date</th>
                    <th>Predicted Threat Count</th>
                    <th>Lower Bound (95%)</th>
                    <th>Upper Bound (95%)</th>
                    <th>Uncertainty Margin</th>
                  </tr>
                </thead>
                <tbody>
                  {forecastData.forecast_data.map((pt, idx) => (
                    <tr key={pt.date}>
                      <td className="mono" style={{ color: 'var(--text-muted)' }}>
                        +{idx + 1}
                      </td>
                      <td style={{ fontWeight: 600, color: '#fff' }}>
                        {pt.date}
                      </td>
                      <td className="mono" style={{ fontWeight: 700, color: '#c084fc' }}>
                        {pt.predicted_count}
                      </td>
                      <td className="mono" style={{ color: '#64748b' }}>
                        {pt.lower_bound}
                      </td>
                      <td className="mono" style={{ color: '#fca5a5' }}>
                        {pt.upper_bound}
                      </td>
                      <td className="mono" style={{ color: 'var(--text-secondary)' }}>
                        ±{(pt.upper_bound - pt.predicted_count).toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
