import axios from 'axios'
import { API_BASE_URL } from '@/shared/config/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120_000,
  withCredentials: true, // Envoie le cookie httpOnly docling-token
})

// Retry interceptor: max 3 retries, exponential backoff 500*2^n ms for 5xx/network errors
apiClient.interceptors.response.use(
  (res) => res,
  async (err) => {
    const config = err.config
    config._retryCount = config._retryCount ?? 0
    const maxRetries = 3
    const is5xx = err.response?.status >= 500
    const isNetworkError = !err.response && (err.code === 'ECONNABORTED' || err.code === 'ERR_NETWORK')

    if ((is5xx || isNetworkError) && config._retryCount < maxRetries) {
      config._retryCount += 1
      const delay = 500 * Math.pow(2, config._retryCount - 1)
      await new Promise((r) => setTimeout(r, delay))
      return apiClient(config)
    }
    return Promise.reject(err)
  },
)

// Sanitize token to prevent header injection (SAFE-MCP-101)
function sanitizeAuthToken(value) {
  if (!value || typeof value !== 'string') return ''
  return value.replace(/[\r\n\0]/g, '').trim()
}

// Cookie httpOnly envoyé automatiquement avec withCredentials
// Fallback Authorization pour rétrocompatibilité (localStorage legacy)
// X-Requested-With pour identification requêtes AJAX (CSRF mitigation)
apiClient.interceptors.request.use((config) => {
  config.headers['X-Requested-With'] = 'XMLHttpRequest'
  const raw = localStorage.getItem('docling-token')
  const token = sanitizeAuthToken(raw)
  if (token) config.headers.Authorization = 'Bearer ' + token
  return config
})

apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('docling-token')
      const path = typeof window !== 'undefined' ? window.location.pathname : ''
      if (!path.startsWith('/login') && !path.startsWith('/register')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  },
)

export default apiClient
