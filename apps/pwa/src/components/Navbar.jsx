import { Camera, Clock, FileText, PackageSearch, Settings, WifiOff } from 'lucide-react'
import { useEffect, useState } from 'react'
import { NavLink } from 'react-router-dom'

export default function Navbar() {
  const [online, setOnline] = useState(navigator.onLine)

  useEffect(() => {
    const on  = () => setOnline(true)
    const off = () => setOnline(false)
    window.addEventListener('online', on)
    window.addEventListener('offline', off)
    return () => {
      window.removeEventListener('online', on)
      window.removeEventListener('offline', off)
    }
  }, [])

  const linkClass = ({ isActive }) =>
    `relative flex flex-col items-center gap-1 transition-all duration-200 px-4 py-2 rounded-xl
     active:scale-95 focus-visible:ring-2 focus-visible:ring-emerald-400/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#121212]
     ${isActive ? 'text-emerald-400' : 'text-slate-500 hover:text-slate-300 hover:scale-105'}`

  const navItems = [
    { to: '/scan', icon: Camera, label: 'Scanner', testId: 'nav-scan' },
    { to: '/catalogue', icon: PackageSearch, label: 'Catalogue', testId: 'nav-catalogue' },
    { to: '/devis', icon: FileText, label: 'Devis', testId: 'nav-devis' },
    { to: '/history', icon: Clock, label: 'Historique', testId: 'nav-history' },
    { to: '/settings', icon: Settings, label: 'Réglages', testId: 'nav-settings' },
  ]

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-50
        bg-slate-900/70 backdrop-blur-2xl
        border-t border-slate-700/50
        flex justify-around items-start
        pb-safe pt-3
        shadow-[0_-4px_24px_rgba(0,0,0,0.3)]"
      aria-label="Navigation principale"
    >
      {!online && (
        <div className="absolute -top-6 left-1/2 -translate-x-1/2 flex items-center gap-1.5
          bg-amber-600/90 backdrop-blur-sm text-white text-[10px] font-bold px-3 py-1 rounded-t-lg">
          <WifiOff size={11} aria-hidden />
          Hors ligne
        </div>
      )}

      {navItems.map(({ to, icon, label, testId }) => {
        const IconComponent = icon
        return (
        <NavLink
          key={to}
          to={to}
          className={linkClass}
          data-testid={testId}
          aria-label={label}
        >
          {({ isActive }) => (
            <>
              <IconComponent size={22} strokeWidth={2} aria-hidden />
              <span className="text-[10px] font-semibold tracking-wide uppercase">{label}</span>
              {isActive && (
                <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-8 h-0.5 rounded-full bg-emerald-400" aria-hidden />
              )}
            </>
          )}
        </NavLink>
        )
      })}
    </nav>
  )
}
