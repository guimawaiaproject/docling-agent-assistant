import { Fragment, lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { Toaster } from 'sonner'
import CommandPalette from './components/CommandPalette'
import Navbar from './components/Navbar'
import OfflineBanner from './components/OfflineBanner'
import { ProtectedRoute } from './features/auth'
import SkeletonCard from '@/shared/ui/SkeletonCard'
import { FEATURES } from '@/shared/config/features'

const ScanPage       = lazy(() => import('./features/scan/ScanPage'))
const ValidationPage = lazy(() => import('./features/validation/ValidationPage'))
const CataloguePage  = lazy(() => import('./features/catalogue/CataloguePage'))
const HistoryPage    = lazy(() => import('./features/history/HistoryPage'))
const SettingsPage   = lazy(() => import('./features/settings/SettingsPage'))
const DevisPage      = lazy(() => import('./features/devis/DevisPage'))
const LoginPage      = lazy(() => import('./features/auth/LoginPage'))
const RegisterPage   = lazy(() => import('./features/auth/RegisterPage'))

function PageLoader() {
  return (
    <div className="p-5 max-w-screen-md mx-auto min-h-[60vh]">
      <SkeletonCard count={4} variant="card" />
    </div>
  )
}

function LayoutWithNav({ children }) {
  return (
    <>
      <main className="max-w-screen-md mx-auto min-h-full px-4 sm:px-5 py-4 sm:py-5">{children}</main>
      <Navbar />
    </>
  )
}

// Si AUTH_REQUIRED=false → app accessible sans token
// Si AUTH_REQUIRED=true → ProtectedRoute actif, redirection /login si pas de token
const RouteWrapper = FEATURES.AUTH_REQUIRED ? ProtectedRoute : Fragment

export default function App() {
  return (
    <div className="min-h-screen bg-[#121212] pb-20 text-slate-200">
      <OfflineBanner />
      <CommandPalette />
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/login"  element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/*" element={
            <RouteWrapper>
              <LayoutWithNav>
                <Routes>
                  <Route path="/"           element={<Navigate to="/scan" replace />} />
                  <Route path="/scan"       element={<ScanPage />} />
                  <Route path="/validation" element={<ValidationPage />} />
                  <Route path="/catalogue"  element={<CataloguePage />} />
                  <Route path="/history"    element={<HistoryPage />} />
                  <Route path="/settings"   element={<SettingsPage />} />
                  <Route path="/devis"      element={<DevisPage />} />
                </Routes>
              </LayoutWithNav>
            </RouteWrapper>
          } />
        </Routes>
      </Suspense>

      <Toaster
        position="top-center"
        richColors
        toastOptions={{
          style: {
            background: 'rgba(30, 41, 59, 0.9)',
            backdropFilter: 'blur(12px)',
            color: '#e2e8f0',
            border: '1px solid rgba(51, 65, 85, 0.6)',
            borderRadius: '12px',
            fontWeight: '600',
          }
        }}
      />
    </div>
  )
}
