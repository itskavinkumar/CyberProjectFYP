import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  Activity, 
  Zap, 
  AlertOctagon, 
  Calendar, 
  ArrowRight,
  RefreshCw
} from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line, Doughnut } from 'react-chartjs-2';
import { getAnalyticsOverview } from '../api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function OverviewView({ onSelectThreatForForecast }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchOverview = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAnalyticsOverview();
      setAnalytics(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch SOC analytics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 1rem' }}>
        <RefreshCw size={36} color="#06b6d4" className="spin" style={{ animation: 'spin 1.5s linear infinite' }} />
        <p style={{ marginTop: '1rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Aggregating SOC Telemetry and Deep Learning Risk Indicators...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center', border: '1px solid var(--accent-rose)' }}>
        <AlertOctagon size={40} color="#f43f5e" style={{ margin: '0 auto 1rem' }} />
        <h3 style={{ color: '#fff' }}>Telemetry Ingestion Error</h3>
        <p style={{ color: 'var(--text-secondary)', margin: '0.5rem 0 1.5rem' }}>{error}</p>
        <button onClick={fetchOverview} className="btn btn-primary">
          <RefreshCw size={16} /> Retry Telemetry Pipeline
        </button>
      </div>
    );
  }

  // Daily Trend Chart configuration
  const trendLabels = analytics.daily_trend.map(d => d.date);
  const trendValues = analytics.daily_trend.map(d => d.count);

  const trendChartData = {
    labels: trendLabels,
    datasets: [
      {
        label: 'Daily Cyber Incidents',
        data: trendValues,
        fill: true,
        borderColor: '#06b6d4',
        borderWidth: 2,
        backgroundColor: (context) => {
          const ctx = context.chart.ctx;
          const gradient = ctx.createLinearGradient(0, 0, 0, 300);
          gradient.addColorStop(0, 'rgba(6, 182, 212, 0.35)');
          gradient.addColorStop(1, 'rgba(6, 182, 212, 0.0)');
          return gradient;
        },
        tension: 0.35,
        pointRadius: 2,
        pointHoverRadius: 6,
        pointBackgroundColor: '#06b6d4',
      }
    ]
  };

  const trendChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: '#0f172a',
        borderColor: '#38bdf8',
        borderWidth: 1,
        titleColor: '#fff',
        bodyColor: '#38bdf8',
        displayColors: false,
        padding: 10
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(51, 65, 85, 0.2)' },
        ticks: { color: '#64748b', maxTicksLimit: 10, font: { family: 'JetBrains Mono', size: 10 } }
      },
      y: {
        grid: { color: 'rgba(51, 65, 85, 0.2)' },
        ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono', size: 10 } }
      }
    }
  };

  // Severity Distribution Doughnut Chart
  const sevColors = {
    Critical: '#f43f5e',
    High: '#f59e0b',
    Medium: '#3b82f6',
    Low: '#10b981'
  };

  const sevDoughnutData = {
    labels: analytics.severity_distribution.map(s => s.severity),
    datasets: [
      {
        data: analytics.severity_distribution.map(s => s.count),
        backgroundColor: analytics.severity_distribution.map(s => sevColors[s.severity] || '#64748b'),
        borderColor: '#0f172a',
        borderWidth: 3,
        hoverOffset: 6
      }
    ]
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top 4 KPI Metrics */}
      <div className="grid-metrics">
        {/* Metric 1 */}
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Historical Telemetry Events
            </span>
            <div style={{ background: 'rgba(6, 182, 212, 0.1)', padding: '0.4rem', borderRadius: '8px' }}>
              <Activity size={18} color="#06b6d4" />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#fff', marginTop: '0.5rem', fontFamily: 'var(--font-mono)' }}>
            {analytics.total_threat_events.toLocaleString()}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Spanning {analytics.threat_categories_count} primary threat vectors
          </div>
        </div>

        {/* Metric 2 */}
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Primary Threat Vector
            </span>
            <div style={{ background: 'rgba(245, 158, 11, 0.1)', padding: '0.4rem', borderRadius: '8px' }}>
              <Zap size={18} color="#f59e0b" />
            </div>
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fde68a', marginTop: '0.5rem' }}>
            {analytics.most_frequent_threat}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Highest historical volume detected
          </div>
        </div>

        {/* Metric 3 */}
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              High-Severity Impact Threat
            </span>
            <div style={{ background: 'rgba(244, 63, 94, 0.1)', padding: '0.4rem', borderRadius: '8px' }}>
              <AlertOctagon size={18} color="#f43f5e" />
            </div>
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fca5a5', marginTop: '0.5rem' }}>
            {analytics.highest_severity_threat}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Dominant critical breach severity profile
          </div>
        </div>

        {/* Metric 4 */}
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Avg Daily Incident Velocity
            </span>
            <div style={{ background: 'rgba(16, 185, 129, 0.1)', padding: '0.4rem', borderRadius: '8px' }}>
              <TrendingUp size={18} color="#10b981" />
            </div>
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#fff', marginTop: '0.5rem', fontFamily: 'var(--font-mono)' }}>
            {analytics.avg_threats_per_day.toLocaleString()} <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>/ day</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginTop: '0.35rem' }}>
            <span className={`badge ${
              analytics.overall_trend_direction === 'Increasing' ? 'badge-trend-up' :
              analytics.overall_trend_direction === 'Decreasing' ? 'badge-trend-down' : 'badge-trend-stable'
            }`} style={{ fontSize: '0.7rem' }}>
              {analytics.overall_trend_direction}
            </span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Network-wide posture</span>
          </div>
        </div>
      </div>

      {/* Main Charts Section */}
      <div className="grid-charts">
        {/* Daily Trendline */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <div>
              <h3 style={{ fontSize: '1.05rem', color: '#fff' }}>60-Day Network Threat Timeline</h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Granular incident counts across all monitored sensory endpoints
              </p>
            </div>
            <span className="badge badge-low">Live Stream</span>
          </div>
          <div style={{ height: '280px', width: '100%' }}>
            <Line data={trendChartData} options={trendChartOptions} />
          </div>
        </div>

        {/* Severity Distribution */}
        <div className="glass-panel" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ fontSize: '1.05rem', color: '#fff', marginBottom: '0.25rem' }}>Severity Distribution</h3>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
            Impact rating categorization
          </p>
          <div style={{ height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Doughnut data={sevDoughnutData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 11 } } } } }} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginTop: '1rem' }}>
            {analytics.severity_distribution.map(sev => (
              <div key={sev.severity} style={{ background: 'rgba(30, 41, 59, 0.4)', padding: '0.4rem 0.6rem', borderRadius: '6px' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>{sev.severity}</div>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: sevColors[sev.severity] || '#fff', fontFamily: 'var(--font-mono)' }}>
                  {sev.count.toLocaleString()} ({sev.percentage}%)
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Cyber Threat Risk Indicators & Model Forecast Preview */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', color: '#fff' }}>Cyber Threat Risk Matrix & Deep Learning Forecast Status</h3>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Real-time composite risk scores (0–100) generated by trained LSTM forecasting models
            </p>
          </div>
          <button
            onClick={() => onSelectThreatForForecast('Phishing')}
            className="btn btn-outline"
            style={{ fontSize: '0.75rem', padding: '0.4rem 0.8rem' }}
          >
            Launch Full AI Forecaster <ArrowRight size={14} />
          </button>
        </div>

        <div className="soc-table-container">
          <table className="soc-table">
            <thead>
              <tr>
                <th>Threat Category</th>
                <th>Risk Posture</th>
                <th>Composite Score</th>
                <th>Velocity Trend</th>
                <th>Historical Avg/Day</th>
                <th>Forecasted Shift</th>
                <th>Contributing Threat Factors</th>
                <th>Forecasting Action</th>
              </tr>
            </thead>
            <tbody>
              {analytics.risk_indicators.map((ri) => {
                const badgeClass = 
                  ri.risk_level === 'Critical' ? 'badge-critical' :
                  ri.risk_level === 'High' ? 'badge-high' :
                  ri.risk_level === 'Medium' ? 'badge-medium' : 'badge-low';

                const trendClass =
                  ri.recent_trend === 'Increasing' ? 'badge-trend-up' :
                  ri.recent_trend === 'Decreasing' ? 'badge-trend-down' : 'badge-trend-stable';

                return (
                  <tr key={ri.threat_type}>
                    <td style={{ fontWeight: 600, color: '#fff' }}>
                      {ri.threat_type}
                    </td>
                    <td>
                      <span className={`badge ${badgeClass}`}>
                        {ri.risk_level}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                        <span className="mono" style={{ fontWeight: 700, fontSize: '0.9rem', color: ri.risk_score >= 70 ? '#fb7185' : '#38bdf8' }}>
                          {ri.risk_score}
                        </span>
                        <div style={{ width: '60px', height: '6px', background: '#1e293b', borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{
                            width: `${ri.risk_score}%`,
                            height: '100%',
                            background: ri.risk_score >= 70 ? 'linear-gradient(90deg, #f59e0b, #ef4444)' : 'linear-gradient(90deg, #10b981, #06b6d4)'
                          }} />
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${trendClass}`}>
                        {ri.recent_trend === 'Increasing' ? <TrendingUp size={12} /> :
                         ri.recent_trend === 'Decreasing' ? <TrendingDown size={12} /> : <Minus size={12} />}
                        {ri.recent_trend}
                      </span>
                    </td>
                    <td className="mono" style={{ color: 'var(--text-secondary)' }}>
                      {ri.avg_daily_count}
                    </td>
                    <td className="mono" style={{ color: ri.forecasted_change_pct > 0 ? '#f87171' : '#34d399', fontWeight: 600 }}>
                      {ri.forecasted_change_pct > 0 ? `+${ri.forecasted_change_pct}%` : `${ri.forecasted_change_pct}%`}
                    </td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-muted)', maxWidth: '280px' }}>
                      {ri.contributing_factors.join(' • ')}
                    </td>
                    <td>
                      <button
                        onClick={() => onSelectThreatForForecast(ri.threat_type)}
                        className="btn btn-secondary"
                        style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem' }}
                      >
                        Forecast <ArrowRight size={12} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
