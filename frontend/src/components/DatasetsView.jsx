import React, { useState, useEffect } from 'react';
import { 
  Database, 
  UploadCloud, 
  CheckCircle2, 
  AlertCircle, 
  FileText, 
  Calendar, 
  RefreshCw,
  Layers
} from 'lucide-react';
import { listDatasets, uploadDatasetFile } from '../api';

export default function DatasetsView({ currentUser }) {
  const isViewer = (currentUser?.role || '').toLowerCase() === 'viewer';
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [uploadError, setUploadError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const fetchDatasets = async () => {
    setLoading(true);
    try {
      const data = await listDatasets();
      setDatasets(data.datasets || []);
    } catch (err) {
      console.error('Failed to load datasets:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setUploadResult(null);
      setUploadError(null);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    setUploadResult(null);
    setUploadError(null);
    try {
      const result = await uploadDatasetFile(selectedFile);
      setUploadResult(result);
      setSelectedFile(null);
      fetchDatasets();
    } catch (err) {
      setUploadError(err.message || 'Dataset upload and validation failed.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Upload Zone */}
      <div className="glass-panel" style={{ padding: '1.75rem' }}>
        <h2 style={{ fontSize: '1.2rem', color: '#fff', marginBottom: '0.35rem' }}>
          Cyber Threat Dataset Ingestion & Validation Engine
        </h2>
        <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
          Upload new intrusion detection or threat intelligence CSV logs. The system automatically validates schema headers (Date, Threat_Type, Severity, Count) and ingests events into the database.
        </p>

        {isViewer ? (
          <div style={{
            background: 'rgba(59, 130, 246, 0.1)',
            border: '1px solid rgba(59, 130, 246, 0.3)',
            borderRadius: '10px',
            padding: '1.25rem',
            color: '#93c5fd',
            fontSize: '0.85rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem'
          }}>
            <AlertCircle size={20} />
            <span>Viewer Access: You have read-only privileges. Dataset uploading is restricted to Analysts and Administrators.</span>
          </div>
        ) : (
          <form onSubmit={handleUpload}>
          <div style={{
            border: '2px dashed var(--border-bright)',
            background: 'rgba(15, 23, 42, 0.4)',
            borderRadius: '12px',
            padding: '2rem 1.5rem',
            textAlign: 'center',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            position: 'relative'
          }}>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              id="file-upload-input"
              style={{
                position: 'absolute',
                inset: 0,
                opacity: 0,
                cursor: 'pointer',
                width: '100%',
                height: '100%'
              }}
            />
            <UploadCloud size={44} color="#06b6d4" style={{ margin: '0 auto 0.75rem' }} />
            <div style={{ color: '#fff', fontWeight: 600, fontSize: '0.95rem' }}>
              {selectedFile ? selectedFile.name : 'Choose a CSV dataset or drop it here'}
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              Supported: RFC 4180 CSV with headers: Date, Threat_Type, Severity, Count
            </p>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem', gap: '0.75rem' }}>
            {selectedFile && (
              <button
                type="submit"
                disabled={uploading}
                className="btn btn-primary"
                id="btn-confirm-upload"
              >
                {uploading ? 'Validating & Ingesting...' : `Ingest "${selectedFile.name}"`}
              </button>
            )}
          </div>
        </form>
        )}

        {/* Upload Success Alert */}
        {uploadResult && (
          <div style={{
            background: 'rgba(16, 185, 129, 0.12)',
            border: '1px solid rgba(16, 185, 129, 0.4)',
            padding: '1rem 1.25rem',
            borderRadius: '8px',
            marginTop: '1.25rem',
            color: '#a7f3d0'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, fontSize: '0.9rem' }}>
              <CheckCircle2 size={18} /> Dataset Successfully Ingested (ID: {uploadResult.dataset_id})
            </div>
            <div style={{ fontSize: '0.8rem', marginTop: '0.4rem', color: '#6ee7b7' }}>
              • Total Records: {uploadResult.number_of_records.toLocaleString()}<br />
              • Detected Threat Types: {uploadResult.threat_types?.join(', ')}<br />
              • Date Range: {uploadResult.date_range?.start} to {uploadResult.date_range?.end}
            </div>
          </div>
        )}

        {/* Upload Error Alert */}
        {uploadError && (
          <div style={{
            background: 'rgba(244, 63, 94, 0.12)',
            border: '1px solid rgba(244, 63, 94, 0.4)',
            padding: '1rem 1.25rem',
            borderRadius: '8px',
            marginTop: '1.25rem',
            color: '#fda4af'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, fontSize: '0.9rem' }}>
              <AlertCircle size={18} /> Ingestion & Validation Failure
            </div>
            <p style={{ fontSize: '0.8rem', marginTop: '0.35rem' }}>{uploadError}</p>
          </div>
        )}
      </div>

      {/* Existing Registered Datasets List */}
      <div className="glass-panel" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1.05rem', color: '#fff' }}>Registered Datasets Registry</h3>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Historical and uploaded data stores registered in MongoDB
            </p>
          </div>
          <button onClick={fetchDatasets} className="btn btn-secondary" style={{ padding: '0.4rem 0.75rem', fontSize: '0.75rem' }}>
            <RefreshCw size={14} /> Refresh Registry
          </button>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
            Loading dataset registry...
          </div>
        ) : (
          <div className="soc-table-container">
            <table className="soc-table">
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>Total Events</th>
                  <th>Timeline Range</th>
                  <th>Recognized Threat Vectors</th>
                  <th>Validation Status</th>
                  <th>Registered At</th>
                </tr>
              </thead>
              <tbody>
                {datasets.map((ds) => (
                  <tr key={ds.id || ds.filename}>
                    <td style={{ fontWeight: 600, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <FileText size={15} color="var(--accent-cyan)" />
                      {ds.filename}
                    </td>
                    <td className="mono" style={{ fontWeight: 700, color: '#38bdf8' }}>
                      {ds.number_of_records?.toLocaleString()}
                    </td>
                    <td className="mono" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      {ds.date_range?.start || 'N/A'} → {ds.date_range?.end || 'N/A'}
                    </td>
                    <td style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {ds.threat_types ? ds.threat_types.join(', ') : 'All Supported'}
                    </td>
                    <td>
                      <span className="badge badge-low">
                        <CheckCircle2 size={12} /> {ds.processing_status || 'Processed'}
                      </span>
                    </td>
                    <td className="mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {ds.upload_date ? new Date(ds.upload_date).toLocaleDateString() : 'Active'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
