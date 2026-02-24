// Configuration de l'API FastAPI distante
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const ENDPOINTS = {
  process:   `${API_BASE_URL}/api/v1/invoices/process`,
  // Le backend renvoie directement la reponse, mais on garde status pour une flexibilité future
  status:    (jobId) => `${API_BASE_URL}/api/v1/invoices/status/${jobId}`,
  catalogue: `${API_BASE_URL}/api/v1/catalogue`,
  batch:     `${API_BASE_URL}/api/v1/catalogue/batch`,
}
