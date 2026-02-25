import { motion } from 'framer-motion'
import {
  Activity, CheckCircle2, ChevronRight, Cloud, Cpu, Info,
  Loader2, Package, RefreshCw, Wifi, WifiOff, FileText
} from 'lucide-react'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import apiClient from '../services/apiClient'
import { ENDPOINTS } from '../config/api'
import { AI_MODELS, useDoclingStore } from '../store/useStore'

export default function SettingsPage() {
  const selectedModel = useDoclingStore(s => s.selectedModel)
  const setModel      = useDoclingStore(s => s.setModel)

  const [healthStatus, setHealthStatus] = useState(null)
  const [healthLoading, setHealthLoading] = useState(false)
  const [stats, setStats]   = useState(null)
  const [sync, setSync]     = useState(null)

  const handleSelectModel = (modelId) => {
    setModel(modelId)
    const model = AI_MODELS.find(m => m.id === modelId)
    toast.success(`Mod\u00e8le IA \u2192 ${model.label}`)
  }

  const testConnection = async () => {
    setHealthLoading(true)
    try {
      const start = Date.now()
      const { data } = await apiClient.get(ENDPOINTS.health, { timeout: 5000 })
      const latency = Date.now() - start
      setHealthStatus({ ok: true, latency, version: data.version })
      toast.success(`API connect\u00e9e (${latency}ms)`)
    } catch {
      setHealthStatus({ ok: false })
      toast.error('API inaccessible')
    } finally {
      setHealthLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const [statsRes, syncRes] = await Promise.all([
        apiClient.get(ENDPOINTS.stats).catch(() => null),
        apiClient.get(ENDPOINTS.syncStatus).catch(() => null),
      ])
      if (statsRes) setStats(statsRes.data)
      if (syncRes) setSync(syncRes.data)
    } catch { /* ignore */ }
  }

  useEffect(() => { fetchStats() }, [])

  return (
    <div className="p-5 min-h-screen bg-slate-950 pb-28">

      <div className="pt-4 pb-6">
        <h1 className="text-2xl font-black text-slate-100 tracking-tight">Param\u00e8tres</h1>
        <p className="text-sm text-slate-500 mt-1">Configuration de l'application</p>
      </div>

      {/* Connexion API */}
      <section className="mb-8" data-testid="settings-sync-status">
        <div className="flex items-center gap-2 mb-3">
          <Activity size={16} className="text-blue-400" />
          <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Connexion API</h2>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              {healthStatus === null ? (
                <div className="w-2.5 h-2.5 rounded-full bg-slate-600" />
              ) : healthStatus.ok ? (
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              ) : (
                <div className="w-2.5 h-2.5 rounded-full bg-red-500" />
              )}
              <span className="text-sm text-slate-300 font-medium">
                {healthStatus === null ? 'Non test\u00e9' :
                 healthStatus.ok ? `Connect\u00e9 (${healthStatus.latency}ms)` : 'D\u00e9connect\u00e9'}
              </span>
            </div>
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={testConnection}
              disabled={healthLoading}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700
                text-slate-300 text-xs font-bold rounded-lg border border-slate-700 transition-colors
                disabled:opacity-40"
            >
              {healthLoading ? <Loader2 size={12} className="animate-spin" /> : <Wifi size={12} />}
              Tester
            </motion.button>
          </div>

          {stats && (
            <div className="grid grid-cols-3 gap-2">
              <MiniStat icon={<Package size={13} />} label="Produits" value={stats.total_produits || 0} />
              <MiniStat icon={<FileText size={13} />} label="Fournisseurs" value={stats.total_fournisseurs || 0} />
              <MiniStat icon={<RefreshCw size={13} />} label="Cette semaine" value={stats.cette_semaine || 0} />
            </div>
          )}
        </div>
      </section>

      {/* Modele IA */}
      <section className="mb-8">
        <div className="flex items-center gap-2 mb-3">
          <Cpu size={16} className="text-emerald-400" />
          <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest">
            Mod\u00e8le IA d'extraction
          </h2>
        </div>

        <div className="space-y-2">
          {AI_MODELS.map((model, i) => {
            const isSelected = selectedModel === model.id
            return (
              <motion.button
                key={model.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                onClick={() => handleSelectModel(model.id)}
                className={`w-full flex items-center justify-between p-4 rounded-2xl border-2 transition-all duration-200 text-left ${
                  isSelected
                    ? 'border-emerald-500/50 bg-emerald-500/10'
                    : 'border-slate-800 bg-slate-900 hover:border-slate-700'
                }`}
              >
                <div className="flex flex-col gap-1">
                  <div className="flex items-center gap-2">
                    <span className={`font-bold text-sm ${isSelected ? 'text-emerald-300' : 'text-slate-200'}`}>
                      {model.label}
                    </span>
                    {model.recommended && (
                      <span className="text-[9px] font-black bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full uppercase tracking-wider">
                        Recommand\u00e9
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-slate-500 font-medium">{model.badge}</span>
                </div>
                {isSelected
                  ? <CheckCircle2 size={20} className="text-emerald-400 shrink-0" />
                  : <ChevronRight size={20} className="text-slate-600 shrink-0" />
                }
              </motion.button>
            )
          })}
        </div>

        <div className="mt-3 flex gap-2 p-3 bg-slate-900/50 border border-slate-800 rounded-xl">
          <Info size={14} className="text-slate-500 mt-0.5 shrink-0" />
          <p className="text-xs text-slate-500 leading-relaxed">
            Le mod\u00e8le s\u00e9lectionn\u00e9 est envoy\u00e9 \u00e0 chaque requ\u00eate d'extraction.
            Gemini 3 Flash offre le meilleur rapport vitesse/pr\u00e9cision pour les factures BTP.
          </p>
        </div>
      </section>

      {/* Watchdog sync status */}
      {sync && (
        <section className="mb-8">
          <div className="flex items-center gap-2 mb-3">
            <Cloud size={16} className="text-amber-400" />
            <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Dossier Magique</h2>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4">
            <div className="flex items-center gap-2 mb-2">
              {sync.running ? (
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              ) : (
                <div className="w-2.5 h-2.5 rounded-full bg-slate-600" />
              )}
              <span className="text-sm text-slate-300 font-medium">
                {sync.running ? 'Watchdog actif' : 'Watchdog inactif'}
              </span>
            </div>
            {sync.folder && (
              <p className="text-xs text-slate-500 font-mono truncate">{sync.folder}</p>
            )}
            {sync.files_processed != null && (
              <p className="text-xs text-slate-500 mt-1">{sync.files_processed} fichiers trait\u00e9s</p>
            )}
          </div>
        </section>
      )}

      {/* About */}
      <section>
        <div className="flex items-center gap-2 mb-3">
          <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest">\u00c0 propos</h2>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-2xl divide-y divide-slate-800">
          {[
            { label: 'Version', value: '3.0.0' },
            { label: 'Backend', value: 'FastAPI + Neon PostgreSQL' },
            { label: 'Stack', value: 'React 19 \u00b7 Vite 5 \u00b7 Tailwind 4' },
          ].map(({ label, value }) => (
            <div key={label} className="flex justify-between items-center px-4 py-3">
              <span className="text-sm text-slate-400 font-medium">{label}</span>
              <span className="text-sm text-slate-300 font-semibold">{value}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

function MiniStat({ icon, label, value }) {
  return (
    <div className="bg-slate-800/50 rounded-xl p-2.5 text-center">
      <div className="flex items-center justify-center gap-1 text-slate-400 mb-1">{icon}</div>
      <div className="text-sm font-black text-slate-200">{value}</div>
      <div className="text-[9px] text-slate-500 uppercase tracking-wider">{label}</div>
    </div>
  )
}