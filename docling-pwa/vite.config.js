/// <reference types="vitest/config" />
import basicSsl from '@vitejs/plugin-basic-ssl'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig(({ mode }) => ({
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
        // Aucun cache pour /api/v1/* — endpoints authentifiés, pas de cache Workbox
        runtimeCaching: []
      }
    })
  ],
  define: mode === 'development'
    ? { 'import.meta.env.VITE_AUTH_REQUIRED': JSON.stringify(process.env.VITE_AUTH_REQUIRED ?? 'false') }
    : {},
  server: {
    port: 5173,
    host: true,
    https: true
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/__tests__/setup.js'],
    include: ['src/__tests__/**/*.{test,spec}.{js,jsx}', 'src/**/__tests__/**/*.{test,spec}.{js,jsx}'],
    env: { NODE_ENV: 'test' },
    define: {
      'import.meta.env.VITE_API_URL': JSON.stringify('http://localhost:8000'),
      'import.meta.env.VITE_AUTH_REQUIRED': JSON.stringify('false'),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-core': ['react', 'react-dom'],
          'router': ['react-router-dom'],
          'ui-motion': ['framer-motion', 'lucide-react'],
          'charts': ['recharts'],
          'pdf-gen': ['jspdf', 'jspdf-autotable'],
          'excel-gen': ['exceljs'],
          'dropzone': ['react-dropzone']
        }
      }
    }
  }
}))
