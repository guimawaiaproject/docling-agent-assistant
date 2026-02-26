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
    `flex flex-col items-center gap-1 transition-all duration-200 px-4 py-1 rounded-xl ${
      isActive
        ? 'text-emerald-400'
        : 'text-slate-500 hover:text-slate-300'
    }`

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50
      bg-slate-900/95 backdrop-blur-xl
      border-t border-slate-800
      flex justify-around items-start
      pb-safe pt-3
      shadow-[0_-1px_0_0_rgba(255,255,255,0.05)]">

      {!online && (
        <div className="absolute -top-6 left-1/2 -translate-x-1/2 flex items-center gap-1.5
          bg-amber-600/90 text-white text-[10px] font-bold px-3 py-1 rounded-t-lg">
          <WifiOff size={11} />
          Hors ligne
        </div>
      )}

      <NavLink to="/scan" className={linkClass} data-testid="nav-scan">
        <Camera size={22} strokeWidth={2} />
        <span className="text-[10px] font-semibold tracking-wide uppercase">Scanner</span>
      </NavLink>

      <NavLink to="/catalogue" className={linkClass} data-testid="nav-catalogue">
        <PackageSearch size={22} strokeWidth={2} />
        <span className="text-[10px] font-semibold tracking-wide uppercase">Catalogue</span>
      </NavLink>

      <NavLink to="/devis" className={linkClass} data-testid="nav-devis">
        <FileText size={22} strokeWidth={2} />
        <span className="text-[10px] font-semibold tracking-wide uppercase">Devis</span>
      </NavLink>

      <NavLink to="/history" className={linkClass} data-testid="nav-history">
        <Clock size={22} strokeWidth={2} />
        <span className="text-[10px] font-semibold tracking-wide uppercase">Historique</span>
      </NavLink>

      <NavLink to="/settings" className={linkClass} data-testid="nav-settings">
        <Settings size={22} strokeWidth={2} />
        <span className="text-[10px] font-semibold tracking-wide uppercase">Réglages</span>
      </NavLink>
    </nav>
  )
}