import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['icons/*.png'],
      manifest: {
        name: 'Docling Agent BTP',
        short_name: 'Docling',
        description: 'Scanner de factures fournisseurs BTP',
        theme_color: '#1a1a2e',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait',
        start_url: '/',
        icons: [
          { src: 'icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: 'icons/icon-512.png', sizes: '512x512', type: 'image/png' }
        ]
      },
      workbox: {
        runtimeCaching: [{
          urlPattern: /\/api\/v1\/catalogue/,
          handler: 'StaleWhileRevalidate',
          options: { cacheName: 'catalogue-cache', expiration: { maxAgeSeconds: 3600 } }
        }]
      }
    })
  ],
  server: {
    port: 5173,
    host: true, // Necessary to access from mobile on the same wifi network
  }
})
