import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { Toaster } from 'sonner'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'

const ScanPage       = lazy(() => import('./pages/ScanPage'))
const ValidationPage = lazy(() => import('./pages/ValidationPage'))
const CataloguePage  = lazy(() => import('./pages/CataloguePage'))
const HistoryPage    = lazy(() => import('./pages/HistoryPage'))
const SettingsPage   = lazy(() => import('./pages/SettingsPage'))
const DevisPage      = lazy(() => import('./pages/DevisPage'))
const LoginPage      = lazy(() => import('./pages/LoginPage'))
const RegisterPage   = lazy(() => import('./pages/RegisterPage'))

function PageLoader() {
  return (
    <div className="flex items-center justify-center h-[60vh]">
      <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
    </div>
  )
}

function LayoutWithNav({ children }) {
  return (
    <>
      <main className="max-w-screen-md mx-auto min-h-full">{children}</main>
      <Navbar />
    </>
  )
}

export default function App() {
  return (
    <div className="min-h-screen bg-slate-950 pb-20 text-slate-100">
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/login"  element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/*" element={
            <ProtectedRoute>
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
            </ProtectedRoute>
          } />
        </Routes>
      </Suspense>

      <Toaster
        position="top-center"
        richColors
        toastOptions={{
          style: {
            background: '#1e293b',
            color: '#f1f5f9',
            border: '1px solid #334155',
            borderRadius: '12px',
            fontWeight: '600',
          }
        }}
      />
    </div>
  )
}
