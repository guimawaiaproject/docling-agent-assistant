import axios from 'axios'
import { API_BASE_URL } from '../config/api'

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

// Cookie httpOnly envoyé automatiquement avec withCredentials
// Fallback Authorization pour rétrocompatibilité (localStorage legacy)
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('docling-token')
  if (token) config.headers.Authorization = `Bearer ${token}`
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
