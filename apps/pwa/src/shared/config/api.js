// Sanitize URL from env to prevent injection (SAFE-MCP-101)
function sanitizeUrl(value) {
  if (!value || typeof value !== 'string') return ''
  const cleaned = value.replace(/[\r\n\0]/g, '').trim().replace(/\/+$/, '')
  if (!/^https?:\/\//.test(cleaned)) return ''
  return cleaned
}

const _env = sanitizeUrl(import.meta.env.VITE_API_URL || '')

function resolveBaseURL() {
  if (_env) return _env
  if (import.meta.env.PROD) {
    throw new Error('VITE_API_URL requis en production')
  }
  return 'http://localhost:8000'
}

export const API_BASE_URL = resolveBaseURL()

export const ENDPOINTS = {
  process:      `${API_BASE_URL}/api/v1/invoices/process`,
  status:       (jobId) => `${API_BASE_URL}/api/v1/invoices/status/${jobId}`,
  catalogue:    `${API_BASE_URL}/api/v1/catalogue`,
  fournisseurs: `${API_BASE_URL}/api/v1/catalogue/fournisseurs`,
  compare:      `${API_BASE_URL}/api/v1/catalogue/compare`,
  batch:        `${API_BASE_URL}/api/v1/catalogue/batch`,
  stats:        `${API_BASE_URL}/api/v1/stats`,
  history:      `${API_BASE_URL}/api/v1/history`,
  pdfUrl:       (factureId) => `${API_BASE_URL}/api/v1/history/${factureId}/pdf`,
  syncStatus:   `${API_BASE_URL}/api/v1/sync/status`,
  health:       `${API_BASE_URL}/health`,
  login:        `${API_BASE_URL}/api/v1/auth/login`,
  register:     `${API_BASE_URL}/api/v1/auth/register`,
  logout:       `${API_BASE_URL}/api/v1/auth/logout`,
  me:           `${API_BASE_URL}/api/v1/auth/me`,
  exportMyData: `${API_BASE_URL}/api/v1/export/my-data`,
  communityPreferences: `${API_BASE_URL}/api/v1/community/preferences`,
  communityStats: `${API_BASE_URL}/api/v1/community/stats`,
}
