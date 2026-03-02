import * as Sentry from '@sentry/react'
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import ErrorBoundary from '@/shared/ui/ErrorBoundary'
import { measureWebVitals } from './utils/reportWebVitals'
import './index.css'

const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

if (SENTRY_DSN) {
  Sentry.init({
    dsn: SENTRY_DSN,
    release: 'docling-agent@3.0.0',
    environment: import.meta.env.MODE,
    integrations: [Sentry.browserTracingIntegration()],
    tracesSampleRate: import.meta.env.DEV ? 1.0 : 0.1,
    tracePropagationTargets: [/^\//, new RegExp(`^${API_URL.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`)],
  })
}

measureWebVitals()

const root = ReactDOM.createRoot(document.getElementById('root'), {
  onUncaughtError: Sentry.reactErrorHandler((error, errorInfo) => {
    if (import.meta.env.DEV) console.warn('[Uncaught]', error, errorInfo?.componentStack)
  }),
  onCaughtError: Sentry.reactErrorHandler(),
  onRecoverableError: Sentry.reactErrorHandler(),
})

root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ErrorBoundary>
  </React.StrictMode>
)
