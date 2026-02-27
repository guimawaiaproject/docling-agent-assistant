import { AnimatePresence, motion } from 'framer-motion'
import {
    AlertCircle, CheckCircle2, Clock, ExternalLink,
    Folder, Loader2, Monitor, Package, RefreshCw, RotateCcw, Smartphone
} from 'lucide-react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import apiClient from '../services/apiClient'
import { ENDPOINTS } from '../config/api'

const SOURCE_CONFIG = {
  mobile:   { icon: <Smartphone size={12} />, label: 'Mobile',   color: 'text-blue-400',   bg: 'bg-blue-500/10' },
  pc:       { icon: <Monitor    size={12} />, label: 'PC',        color: 'text-slate-400',  bg: 'bg-slate-500/10' },
  watchdog: { icon: <Folder     size={12} />, label: 'Dossier',   color: 'text-emerald-400',bg: 'bg-emerald-500/10' },
}

function formatDate(iso) {
  if (!iso) return '\u2014'
  const d = new Date(iso)
  return d.toLocaleDateString('fr-FR', {
    day: '2-digit', month: '2-digit', year: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

export default function HistoryPage() {
  const navigate = useNavigate()
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats,   setStats]   = useState(null)
  const [retrying, setRetrying] = useState(null)
  const [loadingPdf, setLoadingPdf] = useState(null)

  const handleViewPdf = async (facture) => {
    if (!facture.pdf_url || !facture.id) return
    setLoadingPdf(facture.id)
    try {
      const { data } = await apiClient.get(ENDPOINTS.pdfUrl(facture.id))
      if (data?.url) window.open(data.url, '_blank', 'noopener,noreferrer')
      else toast.error('URL PDF indisponible')
    } catch {
      toast.error('Impossible de charger le PDF')
    } finally {
      setLoadingPdf(null)
    }
  }

  const fetchData = async () => {
    setLoading(true)
    try {
      const [histRes, statsRes] = await Promise.all([
        apiClient.get(ENDPOINTS.history),
        apiClient.get(ENDPOINTS.stats),
      ])
      setHistory(histRes.data.history || [])
      setStats(statsRes.data)
    } catch {
      toast.error("Impossible de charger l'historique")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [])

  const handleRescan = async (facture) => {
    if (!facture.pdf_url) {
      toast.error('Pas de fichier cloud pour re-scanner')
      return
    }
    setRetrying(facture.id)
    try {
      const { data } = await apiClient.get(ENDPOINTS.pdfUrl(facture.id))
      const pdfFetchUrl = data?.url || facture.pdf_url
      const response = await fetch(pdfFetchUrl)
      if (!response.ok) throw new Error('Fichier inaccessible')
      const blob = await response.blob()
      const file = new File([blob], facture.filename || 'facture.pdf', { type: blob.type })

      const formData = new FormData()
      formData.append('file', file)
      formData.append('model', facture.modele_ia || 'gemini-3-flash-preview')
      formData.append('source', facture.source || 'pc')

      const { data: jobInfo } = await apiClient.post(ENDPOINTS.process, formData)
      if (!jobInfo.job_id) throw new Error('Pas de job_id')

      let attempts = 0
      while (attempts < 60) {
        const { data: status } = await apiClient.get(ENDPOINTS.status(jobInfo.job_id))
        if (status.status === 'completed') {
          toast.success(`Re-scan OK : ${status.result?.products_added || 0} produits`)
          fetchData()
          return
        }
        if (status.status === 'error') throw new Error(status.error || 'Erreur extraction')
        attempts++
        await new Promise(r => setTimeout(r, 3000))
      }
      throw new Error('Timeout')
    } catch (err) {
      toast.error(`Re-scan : ${err.message}`)
    } finally {
      setRetrying(null)
    }
  }

  const totalProduits = history.reduce((acc, f) => acc + (f.nb_produits_extraits || 0), 0)
  const totalCout     = history.reduce((acc, f) => acc + (parseFloat(f.cout_api_usd) || 0), 0)

  return (
    <div className="p-5 min-h-screen bg-slate-950 pb-28">

      <div className="pt-4 pb-5 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-slate-100 tracking-tight">Historique</h1>
          <p className="text-xs text-slate-500 mt-0.5">Audit trail des factures traitées</p>
        </div>
        <button
          onClick={fetchData}
          aria-label="Actualiser l'historique"
          className="p-2 text-slate-500 hover:text-slate-300 bg-slate-800 rounded-xl border border-slate-700 transition-colors"
        >
          <RefreshCw size={15} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {!loading && history.length > 0 && (
        <div className="grid grid-cols-3 gap-2 mb-5">
          <StatCard label="Factures"  value={history.length}          color="text-slate-300" />
          <StatCard label="Produits"  value={totalProduits}           color="text-emerald-400" />
          <StatCard label="Coût API"  value={`$${totalCout.toFixed(3)}`} color="text-amber-400" />
        </div>
      )}

      {stats?.familles?.length > 0 && (
        <div className="mb-5 bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-3">
            Répartition par famille
          </p>
          <div className="space-y-2">
            {stats.familles.slice(0, 6).map(f => (
              <div key={`${f.famille}-${f.nb}`} className="flex items-center gap-2">
                <span className="text-xs text-slate-400 w-28 truncate">{f.famille}</span>
                <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-emerald-600 to-emerald-400 rounded-full"
                    style={{ width: `${Math.min((f.nb / stats.total_produits) * 100, 100)}%` }}
                  />
                </div>
                <span className="text-xs text-slate-500 w-8 text-right">{f.nb}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center pt-10">
          <Loader2 className="w-8 h-8 text-emerald-500 animate-spin" />
        </div>
      ) : history.length === 0 ? (
        <div className="flex flex-col items-center pt-12 text-slate-500 gap-5 px-6">
          <Clock size={64} className="text-slate-600 opacity-40" />
          <div className="text-center space-y-2">
            <h2 className="text-lg font-bold text-slate-400">Aucune facture traitée</h2>
            <p className="text-sm text-slate-600 max-w-xs">
              Scannez une facture pour commencer à alimenter votre historique.
            </p>
          </div>
          <button
            onClick={() => navigate('/scan')}
            className="flex items-center gap-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500
              text-white rounded-xl text-sm font-bold transition-colors"
          >
            <Package size={16} />
            Scanner une facture
          </button>
        </div>
      ) : (
        <AnimatePresence>
          <div className="space-y-2">
            {history.map((f, i) => {
              const src = SOURCE_CONFIG[f.source] || SOURCE_CONFIG.pc
              const isOk = f.statut === 'traite'
              const isRetrying = retrying === f.id

              return (
                <motion.div
                  key={f.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: Math.min(i * 0.02, 0.3) }}
                  className="bg-slate-900 border border-slate-800 rounded-2xl p-4"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2 min-w-0 flex-1">
                      {isOk
                        ? <CheckCircle2 size={16} className="text-emerald-500 shrink-0" />
                        : <AlertCircle  size={16} className="text-red-500 shrink-0" />
                      }
                      <p className="text-sm font-semibold text-slate-200 truncate">
                        {f.filename || 'Fichier inconnu'}
                      </p>
                    </div>
                    <div className={`flex items-center gap-1 px-2 py-1 rounded-lg text-[10px] font-bold shrink-0 ${src.bg} ${src.color}`}>
                      {src.icon}
                      {src.label}
                    </div>
                  </div>

                  <div className="flex items-center gap-3 mt-2.5 flex-wrap">
                    {isOk && (
                      <span className="flex items-center gap-1 text-xs text-emerald-500 font-bold">
                        <Package size={11} />
                        {f.nb_produits_extraits} produit{f.nb_produits_extraits > 1 ? 's' : ''}
                      </span>
                    )}
                    <span className="text-xs text-slate-600">{f.modele_ia}</span>
                    {parseFloat(f.cout_api_usd) > 0 && (
                      <span className="text-xs text-amber-600">${parseFloat(f.cout_api_usd).toFixed(4)}</span>
                    )}
                    <span className="text-xs text-slate-600 ml-auto">{formatDate(f.created_at)}</span>
                  </div>

                  <div className="flex items-center gap-2 mt-3 pt-2.5 border-t border-slate-800/60">
                    {f.pdf_url && (
                      <button
                        onClick={() => handleViewPdf(f)}
                        disabled={loadingPdf === f.id}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600/15 hover:bg-blue-600/25
                          text-blue-400 rounded-lg text-[11px] font-bold transition-colors disabled:opacity-40"
                      >
                        {loadingPdf === f.id
                          ? <Loader2 size={12} className="animate-spin" />
                          : <ExternalLink size={12} />
                        }
                        Voir PDF
                      </button>
                    )}
                    {!isOk && f.pdf_url && (
                      <button
                        onClick={() => handleRescan(f)}
                        disabled={isRetrying}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-amber-600/15 hover:bg-amber-600/25
                          text-amber-400 rounded-lg text-[11px] font-bold transition-colors disabled:opacity-40"
                      >
                        {isRetrying
                          ? <Loader2 size={12} className="animate-spin" />
                          : <RotateCcw size={12} />
                        }
                        Re-scanner
                      </button>
                    )}
                    {!f.pdf_url && (
                      <span className="text-[10px] text-slate-600 italic">Pas de fichier cloud</span>
                    )}
                  </div>
                </motion.div>
              )
            })}
          </div>
        </AnimatePresence>
      )}
    </div>
  )
}

function StatCard({ label, value, color }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-center">
      <div className={`text-lg font-black ${color}`}>{value}</div>
      <div className="text-[9px] text-slate-500 uppercase tracking-wider mt-0.5">{label}</div>
    </div>
  )
}