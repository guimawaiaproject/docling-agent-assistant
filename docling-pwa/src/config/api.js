const _env = import.meta.env.VITE_API_URL || ''

function resolveBaseURL() {
  if (_env) return _env.replace(/\/+$/, '')
  if (import.meta.env.PROD) {
    console.warn('[api] VITE_API_URL non défini en production — fallback relatif')
    return ''
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
}
