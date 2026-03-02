import { useState } from 'react'
import { AlertCircle, CheckCircle2, ExternalLink, Loader2, PackagePlus, X } from 'lucide-react'
import { motion } from 'framer-motion'
import { toast } from 'sonner'
import apiClient from '@/shared/lib/apiClient'
import { ENDPOINTS } from '@/shared/config/api'

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} o`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} Ko`
  return `${(bytes / 1024 / 1024).toFixed(1)} Mo`
}

const STATUS_CONFIG = {
  pending:    { color: 'text-slate-400', bg: 'bg-slate-800',   label: 'En attente' },
  uploading:  { color: 'text-blue-400',  bg: 'bg-blue-500/20', label: 'Envoi...' },
  processing: { color: 'text-amber-400', bg: 'bg-amber-500/20', label: 'Analyse IA...' },
  done:       { color: 'text-emerald-400', bg: 'bg-emerald-500/20', label: 'Terminé' },
  error:      { color: 'text-red-400',   bg: 'bg-red-500/20',  label: 'Erreur' },
}

/**
 * Carte affichant le statut d'un job (fichier en cours / terminé / erreur).
 */
export default function JobStatusCard({ item, onRemove }) {
  const cfg = STATUS_CONFIG[item.status] || STATUS_CONFIG.pending
  const [loadingPdf, setLoadingPdf] = useState(false)

  const handleViewPdf = async () => {
    if (!item.facture_id) return
    setLoadingPdf(true)
    try {
      const { data } = await apiClient.get(ENDPOINTS.pdfUrl(item.facture_id))
      if (data?.url) window.open(data.url, '_blank', 'noopener,noreferrer')
      else toast.error('URL PDF indisponible')
    } catch {
      toast.error('Impossible de charger le PDF')
    } finally {
      setLoadingPdf(false)
    }
  }

  return (
    <motion.div
      layout
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      className="bg-slate-800/80 border border-slate-700/50 rounded-xl px-4 py-3 flex items-center gap-3 shadow-sm hover:bg-slate-800 transition-colors"
    >
      <div className={`shrink-0 ${cfg.color}`}>
        {item.status === 'done'
          ? <CheckCircle2 size={18} />
          : item.status === 'error'
          ? <AlertCircle size={18} />
          : ['uploading', 'processing'].includes(item.status)
          ? <Loader2 size={18} className="animate-spin" />
          : <PackagePlus size={18} className="text-slate-600" />
        }
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs font-semibold text-slate-300 truncate">
          {item.name || item.file?.name || 'Fichier'}
        </p>
        <div className="flex items-center gap-2 mt-0.5">
          <span className={`text-[9px] font-bold uppercase tracking-wider ${cfg.color}`}>
            {cfg.label}
          </span>
          {item.status === 'done' && item.productsAdded > 0 && (
            <span className="text-[9px] text-emerald-500 font-bold">
              +{item.productsAdded} produits
            </span>
          )}
          {item.status === 'error' && (
            <span className="text-[9px] text-red-400 truncate">{item.error}</span>
          )}
          <span className="text-[9px] text-slate-600 ml-auto">{formatSize(item.size)}</span>
        </div>
        {['uploading', 'processing'].includes(item.status) && (
          <div className="h-0.5 bg-slate-800 rounded-full mt-1.5 overflow-hidden">
            <motion.div
              className="h-full bg-blue-500 rounded-full"
              animate={{ width: `${item.progress}%` }}
            />
          </div>
        )}
      </div>
      {item.status === 'done' && item.facture_id && (
        <button
          onClick={handleViewPdf}
          disabled={loadingPdf}
          aria-label="Voir le PDF de la facture"
          className="flex items-center gap-1.5 px-2.5 py-1.5 bg-blue-600/15 hover:bg-blue-600/25
            text-blue-400 rounded-lg text-[10px] font-bold transition-colors disabled:opacity-40 shrink-0"
        >
          {loadingPdf ? <Loader2 size={12} className="animate-spin" /> : <ExternalLink size={12} />}
          Voir PDF
        </button>
      )}
      {(item.status === 'pending' || item.status === 'error') && (
        <button
          onClick={() => onRemove(item.id)}
          aria-label="Retirer de la file"
          className="text-slate-600 hover:text-red-400 transition-colors shrink-0"
        >
          <X size={16} />
        </button>
      )}
    </motion.div>
  )
}
