/**
 * Web Vitals — Core Web Metrics (CLS, INP, LCP, FCP, TTFB)
 * Dev: console.log avec emoji
 * Prod: navigator.sendBeacon('/api/vitals', data)
 */
import { onCLS, onINP, onLCP, onFCP, onTTFB } from 'web-vitals'
import { API_BASE_URL } from '@/shared/config/api'

const isDev = import.meta.env.DEV

function sendToAnalytics(metric) {
  const body = JSON.stringify({
    name: metric.name,
    value: metric.value,
    rating: metric.rating,
    delta: metric.delta,
    id: metric.id,
    navigationType: metric.navigationType,
  })

  if (isDev) {
    const emoji = {
      CLS: '📐',
      INP: '👆',
      LCP: '🖼️',
      FCP: '🎨',
      TTFB: '⏱️',
    }[metric.name] || '📊'
    console.log(`${emoji} [Web Vitals] ${metric.name}:`, metric.value, `(${metric.rating})`)
  } else {
    const base = (API_BASE_URL || '').trim()
    const url = base.startsWith('http') ? `${base.replace(/\/+$/, '')}/api/vitals` : null
    if (url) {
      const blob = new Blob([body], { type: 'application/json' })
      navigator.sendBeacon(url, blob)
    }
  }
}

export function measureWebVitals() {
  onCLS(sendToAnalytics)
  onINP(sendToAnalytics)
  onLCP(sendToAnalytics)
  onFCP(sendToAnalytics)
  onTTFB(sendToAnalytics)
}
