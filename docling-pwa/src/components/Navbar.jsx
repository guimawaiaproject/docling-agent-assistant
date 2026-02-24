import { Camera, PackageSearch } from 'lucide-react'
import { NavLink } from 'react-router-dom'

export default function Navbar() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 flex justify-around py-3 z-50 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] safe-area-pb">
      <NavLink
        to="/scan"
        className={({ isActive }) =>
          `flex flex-col items-center gap-1 transition-colors ${isActive ? 'text-blue-600' : 'text-gray-400'}`
        }
      >
        <Camera size={26} strokeWidth={2.5} />
        <span className="text-xs font-medium">Scanner</span>
      </NavLink>

      <NavLink
        to="/catalogue"
        className={({ isActive }) =>
          `flex flex-col items-center gap-1 transition-colors ${isActive ? 'text-green-600' : 'text-gray-400'}`
        }
      >
        <PackageSearch size={26} strokeWidth={2.5} />
        <span className="text-xs font-medium">Catalogue</span>
      </NavLink>
    </nav>
  )
}
