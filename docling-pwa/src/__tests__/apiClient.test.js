import MockAdapter from 'axios-mock-adapter'
import { afterEach, beforeEach, describe, expect, test } from 'vitest'
import apiClient from '../services/apiClient'

let mock

beforeEach(() => {
  mock = new MockAdapter(apiClient)
  localStorage.clear()
})

afterEach(() => {
  mock.restore()
  localStorage.clear()
})

describe('apiClient configuration', () => {
  test('has correct baseURL', () => {
    expect(apiClient.defaults.baseURL).toBe('http://localhost:8000')
  })

  test('has 120 second timeout', () => {
    expect(apiClient.defaults.timeout).toBe(120_000)
  })

  test('is an axios instance', () => {
    expect(typeof apiClient.get).toBe('function')
    expect(typeof apiClient.post).toBe('function')
    expect(typeof apiClient.delete).toBe('function')
  })
})

describe('apiClient request interceptor — auth token injection', () => {
  test('adds Authorization header when token exists in localStorage', async () => {
    localStorage.setItem('docling-token', 'jwt-abc-xyz')
    let capturedHeaders = null

    mock.onGet('/api/v1/auth/me').reply((config) => {
      capturedHeaders = config.headers
      return [200, { user: 'test' }]
    })

    await apiClient.get('/api/v1/auth/me')
    expect(capturedHeaders?.Authorization).toBe('Bearer jwt-abc-xyz')
  })

  test('does NOT add Authorization header when no token', async () => {
    let capturedHeaders = null

    mock.onGet('/api/v1/stats').reply((config) => {
      capturedHeaders = config.headers
      return [200, {}]
    })

    await apiClient.get('/api/v1/stats')
    expect(capturedHeaders?.Authorization).toBeUndefined()
  })

  test('uses fresh token on each request', async () => {
    localStorage.setItem('docling-token', 'token-v1')
    const headers1 = []
    mock.onGet('/api/v1/catalogue').reply((config) => {
      headers1.push(config.headers?.Authorization)
      return [200, { products: [] }]
    })
    await apiClient.get('/api/v1/catalogue')

    localStorage.setItem('docling-token', 'token-v2')
    await apiClient.get('/api/v1/catalogue')

    expect(headers1[0]).toBe('Bearer token-v1')
    expect(headers1[1]).toBe('Bearer token-v2')
  })
})

describe('apiClient response interceptor — 401 cleanup', () => {
  test('removes token from localStorage on 401 response', async () => {
    localStorage.setItem('docling-token', 'expired-token')
    mock.onGet('/api/v1/auth/me').reply(401, { detail: 'Token invalide' })

    await expect(apiClient.get('/api/v1/auth/me')).rejects.toThrow()
    expect(localStorage.getItem('docling-token')).toBeNull()
  })

  test('does NOT remove token on non-401 errors', async () => {
    localStorage.setItem('docling-token', 'valid-token')
    mock.onGet('/api/v1/catalogue').reply(503, { detail: 'Service unavailable' })

    await expect(apiClient.get('/api/v1/catalogue')).rejects.toThrow()
    expect(localStorage.getItem('docling-token')).toBe('valid-token')
  })

  test('passes through 200 responses unchanged', async () => {
    mock.onGet('/health').reply(200, { status: 'ok', db: 'connected', version: '3.0.0' })

    const resp = await apiClient.get('/health')
    expect(resp.data.status).toBe('ok')
    expect(resp.data.db).toBe('connected')
  })
})
