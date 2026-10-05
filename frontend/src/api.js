/**
 * Central API Client connecting to FastAPI backend
 */

const API_BASE = '/api';

// Retrieve auth token from localStorage
export const getAuthToken = () => localStorage.getItem('cyber_token');
export const setAuthToken = (token) => localStorage.setItem('cyber_token', token);
export const removeAuthToken = () => localStorage.removeItem('cyber_token');

export const getStoredUser = () => {
  const user = localStorage.getItem('cyber_user');
  try {
    return user ? JSON.parse(user) : null;
  } catch {
    return null;
  }
};
export const setStoredUser = (user) => localStorage.setItem('cyber_user', JSON.stringify(user));
export const removeStoredUser = () => localStorage.removeItem('cyber_user');

async function request(endpoint, options = {}) {
  const token = getAuthToken();
  const headers = {
    ...(options.headers || {}),
  };

  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // If body is an object and not FormData, stringify
  if (options.body && !(options.body instanceof FormData) && typeof options.body === 'object') {
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.body);
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    try {
      const errJson = await res.json();
      errorDetail = errJson.detail || errJson.message || JSON.stringify(errJson);
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }

  return await res.json();
}

// Health API
export const checkHealth = () => request('/health');

// Auth APIs
export const loginUser = async (email, password) => {
  const data = await request('/auth/login', {
    method: 'POST',
    body: { email, password },
  });
  setAuthToken(data.access_token);
  setStoredUser(data.user);
  return data;
};

export const registerUser = async (name, email, password, role = 'analyst') => {
  const data = await request('/auth/register', {
    method: 'POST',
    body: { name, email, password, role },
  });
  setAuthToken(data.access_token);
  setStoredUser(data.user);
  return data;
};

export const getCurrentUser = () => request('/auth/me');

export const logoutUser = async () => {
  try {
    await request('/auth/logout', { method: 'POST' });
  } catch (err) {
    console.warn('Backend logout audit warning:', err);
  } finally {
    removeAuthToken();
    removeStoredUser();
  }
};

// Threat Events APIs
export const getThreatEvents = (params = {}) => {
  const query = new URLSearchParams();
  if (params.threat_type) query.append('threat_type', params.threat_type);
  if (params.severity) query.append('severity', params.severity);
  if (params.limit) query.append('limit', params.limit);
  if (params.skip) query.append('skip', params.skip);
  const qStr = query.toString();
  return request(`/threats${qStr ? `?${qStr}` : ''}`);
};

export const getThreatsSummary = () => request('/threats/summary');
export const getThreatCategories = () => request('/threats/categories');
export const createThreatEvent = (eventData) => request('/threats', {
  method: 'POST',
  body: eventData,
});

// Forecasting APIs
export const generateForecast = (threat_type, forecast_days = 30) => request('/forecast', {
  method: 'POST',
  body: { threat_type, forecast_days: Number(forecast_days) },
});

export const getForecastByThreat = (threat_type, days = 30) => 
  request(`/forecast/${encodeURIComponent(threat_type)}?days=${days}`);

export const getModelsStatus = () => request('/forecast/models/status');

// Datasets APIs
export const listDatasets = () => request('/datasets');
export const getDatasetDetails = (id) => request(`/datasets/${id}`);
export const uploadDatasetFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return request('/datasets/upload', {
    method: 'POST',
    body: formData,
  });
};

// Analytics APIs
export const getAnalyticsOverview = () => request('/analytics/overview');
export const getRiskMatrix = () => request('/analytics/risk-matrix');

// ============================================================================
// Admin & Audit APIs (Features 1, 3, 5, 6, 7, 8, 9, 10, 15, 18)
// ============================================================================

export const getAdminDashboard = () => request('/admin/dashboard');

export const getAdminUsers = (params = {}) => {
  const query = new URLSearchParams();
  if (params.search) query.append('search', params.search);
  if (params.role) query.append('role', params.role);
  if (params.status) query.append('status', params.status);
  if (params.sort_by) query.append('sort_by', params.sort_by);
  if (params.sort_order) query.append('sort_order', params.sort_order);
  if (params.page) query.append('page', params.page);
  if (params.limit) query.append('limit', params.limit);
  const qStr = query.toString();
  return request(`/admin/users${qStr ? `?${qStr}` : ''}`);
};

export const getAdminUserDetail = (userId) => request(`/admin/users/${encodeURIComponent(userId)}`);

export const createAdminUser = (userData) => request('/admin/users', {
  method: 'POST',
  body: userData,
});

export const updateUserRole = (userId, role) => request(`/admin/users/${encodeURIComponent(userId)}/role`, {
  method: 'PATCH',
  body: { role },
});

export const updateUserStatus = (userId, status) => request(`/admin/users/${encodeURIComponent(userId)}/status`, {
  method: 'PATCH',
  body: { status },
});

export const getLoginHistory = (params = {}) => {
  const query = new URLSearchParams();
  if (params.status) query.append('status', params.status);
  if (params.search) query.append('search', params.search);
  if (params.page) query.append('page', params.page);
  if (params.limit) query.append('limit', params.limit);
  const qStr = query.toString();
  return request(`/admin/login-history${qStr ? `?${qStr}` : ''}`);
};

export const getAuditLogs = (params = {}) => {
  const query = new URLSearchParams();
  if (params.action) query.append('action', params.action);
  if (params.resource_type) query.append('resource_type', params.resource_type);
  if (params.role) query.append('role', params.role);
  if (params.status) query.append('status', params.status);
  if (params.search) query.append('search', params.search);
  if (params.page) query.append('page', params.page);
  if (params.limit) query.append('limit', params.limit);
  const qStr = query.toString();
  return request(`/admin/audit-logs${qStr ? `?${qStr}` : ''}`);
};

export const getAuditLogById = (logId) => request(`/admin/audit-logs/${encodeURIComponent(logId)}`);

export const getUserActivity = (userId, limit = 30) => 
  request(`/admin/activity/${encodeURIComponent(userId)}?limit=${limit}`);

// ============================================================================
// Reports APIs (Features 14, 25, 28)
// ============================================================================

export const listReports = (reportType = null) => {
  const query = reportType && reportType !== 'all' ? `?report_type=${encodeURIComponent(reportType)}` : '';
  return request(`/reports${query}`);
};

export const generateReport = (reportData) => request('/reports/generate', {
  method: 'POST',
  body: reportData,
});

export const getReportDetails = (reportId) => request(`/reports/${encodeURIComponent(reportId)}`);

export const getReportExportUrl = (reportId, format = 'csv') => 
  `/api/reports/${encodeURIComponent(reportId)}/export?format=${format}`;
