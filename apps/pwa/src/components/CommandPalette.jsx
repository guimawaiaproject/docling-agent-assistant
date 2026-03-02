import { AnimatePresence, motion } from 'framer-motion'
import { Camera, Clock, FileText, PackageSearch, Settings } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

const COMMANDS = [
  { id: 'scan', label: 'Scanner', path: '/scan', icon: Camera },
  { id: 'catalogue', label: 'Catalogue', path: '/catalogue', icon: PackageSearch },
  { id: 'devis', label: 'Devis', path: '/devis', icon: FileText },
  { id: 'history', label: 'Historique', path: '/history', icon: Clock },
  { id: 'settings', label: 'Paramètres', path: '/settings', icon: Settings },
]

export default function CommandPalette() {
  const [open, setOpen] = useState(false)
  const [selected, setSelected] = useState(0)
  const navigate = useNavigate()

  useEffect(() => {
    const onKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setOpen(prev => !prev)
        setSelected(0)
        return
      }
      if (!open) return
      if (e.key === 'Escape') {
        setOpen(false)
        return
      }
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelected(i => Math.min(i + 1, COMMANDS.length - 1))
        return
      }
      if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelected(i => Math.max(i - 1, 0))
        return
      }
      if (e.key === 'Enter') {
        e.preventDefault()
        const cmd = COMMANDS[selected]
        if (cmd) {
          navigate(cmd.path)
          setOpen(false)
        }
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [open, selected, navigate])

  const handleSelect = (cmd) => {
    navigate(cmd.path)
    setOpen(false)
  }

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[100] bg-slate-950/80 backdrop-blur-sm flex items-start justify-center pt-[15vh] px-4"
          onClick={() => setOpen(false)}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -10 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            onClick={e => e.stopPropagation()}
            className="w-full max-w-md bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden"
          >
            <div className="px-4 py-3 border-b border-slate-800">
              <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">
                Navigation rapide
              </p>
            </div>
            <div className="py-2 max-h-72 overflow-y-auto">
              {COMMANDS.map((cmd, i) => {
                const Icon = cmd.icon
                const isSelected = i === selected
                return (
                  <motion.button
                    key={cmd.id}
                    onClick={() => handleSelect(cmd)}
                    onMouseEnter={() => setSelected(i)}
                    className={`w-full flex items-center gap-3 px-4 py-3 text-left transition-colors
                      ${isSelected ? 'bg-emerald-500/15 text-emerald-300' : 'text-slate-300 hover:bg-slate-800/50'}`}
                  >
                    <Icon size={18} className={isSelected ? 'text-emerald-400' : 'text-slate-500'} />
                    <span className="font-semibold text-sm">{cmd.label}</span>
                  </motion.button>
                )
              })}
            </div>
            <div className="px-4 py-2 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-500">
              <span>↑↓ naviguer</span>
              <span>↵ sélectionner</span>
              <span>Esc fermer</span>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
