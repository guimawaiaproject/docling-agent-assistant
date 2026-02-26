import axios from 'axios'
import { API_BASE_URL } from '../config/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120_000,
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('docling-token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
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
