import basicSsl from '@vitejs/plugin-basic-ssl'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    basicSsl(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['icons/*.png', 'icons/*.svg'],
      manifest: {
        name: 'Docling Agent BTP',
        short_name: 'Docling',
        description: 'Scanner IA de factures fournisseurs BTP',
        theme_color: '#0f172a',
        background_color: '#0f172a',
        display: 'standalone',
        orientation: 'portrait',
        start_url: '/',
        scope: '/',
        icons: [
          { src: 'icons/icon-192.png', sizes: '192x192', type: 'image/png', purpose: 'any maskable' },
          { src: 'icons/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'any maskable' }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,webp}'],
        runtimeCaching: [
          {
            urlPattern: /\/api\/v1\/catalogue/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'catalogue-cache',
              expiration: { maxAgeSeconds: 3600, maxEntries: 50 }
            }
          },
          {
            urlPattern: /\/api\/v1\/stats/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'stats-cache',
              expiration: { maxAgeSeconds: 300, maxEntries: 5 },
              networkTimeoutSeconds: 5
            }
          },
          {
            urlPattern: /\/api\/v1\/history/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'history-cache',
              expiration: { maxAgeSeconds: 300, maxEntries: 5 },
              networkTimeoutSeconds: 5
            }
          },
          {
            urlPattern: /\/api\/v1\/catalogue\/fournisseurs/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'fournisseurs-cache',
              expiration: { maxAgeSeconds: 3600, maxEntries: 5 }
            }
          }
        ]
      }
    })
  ],
  server: {
    port: 5173,
    host: true,
    https: true
  },
})