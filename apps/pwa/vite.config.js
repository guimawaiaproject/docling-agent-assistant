/// <reference types="vitest/config" />
import basicSsl from '@vitejs/plugin-basic-ssl'
import react from '@vitejs/plugin-react'
import path from 'path'
import { defineConfig, loadEnv } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig(({ mode }) => {
  const rootDir = path.resolve(__dirname, '../..')
  const env = loadEnv(mode, rootDir, '')
  return {
  envDir: rootDir,
  plugins: [
    react(),
    ...(mode === 'production' ? [basicSsl()] : []),
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
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/shared': path.resolve(__dirname, './src/shared'),
      '@/features': path.resolve(__dirname, './src/features'),
    },
    dedupe: ['react', 'react-dom'],
  },
  optimizeDeps: {
    include: ['react', 'react-dom', '@splinetool/react-spline'],
  },
  define: {
    // Force React dev build en dev (évite erreur DCE avec @splinetool/react-spline)
    'process.env.NODE_ENV': JSON.stringify(mode === 'production' ? 'production' : 'development'),
    'import.meta.env.VITE_API_URL': JSON.stringify(env.VITE_API_URL || 'http://localhost:8000'),
    'import.meta.env.VITE_AUTH_REQUIRED': JSON.stringify(env.VITE_AUTH_REQUIRED ?? 'false'),
    'import.meta.env.VITE_SENTRY_DSN': JSON.stringify(env.VITE_SENTRY_DSN || ''),
    'import.meta.env.VITE_TVA_RATE': JSON.stringify(env.VITE_TVA_RATE || '0.21'),
  },
  server: {
    port: 5173,
    host: true,
    // HTTP en dev (evite mixed content avec API http://localhost:8000)
    https: false
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
    chunkSizeWarningLimit: 600,
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
  }
})
