import { AnimatePresence, motion } from 'framer-motion'
import { Loader2, Trash2, UploadCloud } from 'lucide-react'
import JobStatusCard from './JobStatusCard'

/**
 * Liste des fichiers en attente avec stats, barre de progression et actions batch.
 */
export default function BatchQueue({
  batchQueue,
  stats,
  totalProducts,
  removeFromQueue,
  clearQueue,
  startBatch,
}) {
  if (batchQueue.length === 0) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="mb-5"
      >
        {stats.total > 1 && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-3">
            {[
              { label: 'Total',    val: stats.total,   color: 'text-slate-300' },
              { label: 'En cours', val: stats.running, color: 'text-amber-400' },
              { label: 'OK',       val: stats.done,    color: 'text-emerald-400' },
              { label: 'Produits', val: totalProducts, color: 'text-blue-400' },
            ].map(({ label, val, color }) => (
              <div
                key={label}
                className="bg-slate-800/80 rounded-xl p-3 text-center border border-slate-700/50 shadow-sm"
              >
                <div className={`text-xl font-black ${color}`}>{val}</div>
                <div className="text-[9px] text-slate-500 uppercase font-bold tracking-wider mt-0.5">
                  {label}
                </div>
              </div>
            ))}
          </div>
        )}

        {stats.total > 0 && (
          <div className="h-1.5 bg-slate-800 rounded-full mb-3 overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-blue-500 to-emerald-500 rounded-full"
              animate={{ width: `${(stats.done / stats.total) * 100}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        )}

        <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
          <AnimatePresence>
            {batchQueue.map((item) => (
              <JobStatusCard key={item.id} item={item} onRemove={removeFromQueue} />
            ))}
          </AnimatePresence>
        </div>

        <div className="flex gap-3 mt-4">
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={startBatch}
            disabled={stats.pending === 0 || stats.running > 0}
            data-testid="scan-lancer-btn"
            className="flex-1 py-4 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40
              text-white rounded-2xl font-bold text-sm flex items-center justify-center gap-2 transition-colors"
          >
            {stats.running > 0
              ? <><Loader2 size={18} className="animate-spin" /> Traitement en cours...</>
              : <><UploadCloud size={18} /> Lancer ({stats.pending} fichier{stats.pending > 1 ? 's' : ''})</>
            }
          </motion.button>
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={() => {
              if (window.confirm('Vider toute la file d\'attente ?')) clearQueue()
            }}
            disabled={stats.running > 0}
            aria-label="Vider la file"
            className="px-4 py-4 bg-slate-800 hover:bg-slate-700 disabled:opacity-40
              text-slate-400 rounded-2xl border border-slate-700 transition-colors"
          >
            <Trash2 size={18} />
          </motion.button>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}
