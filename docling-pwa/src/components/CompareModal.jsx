import { AnimatePresence, motion } from 'framer-motion'
import { BarChart3, Loader2, Search, TrendingUp, X } from 'lucide-react'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { toast } from 'sonner'
import apiClient from '../services/apiClient'
import { ENDPOINTS } from '../config/api'

export default function CompareModal({ isOpen, onClose, initialSearch = '' }) {
  const [search, setSearch] = useState(initialSearch)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const abortRef = useRef(null)
  const debounceRef = useRef(null)

  useEffect(() => {
    return () => {
      abortRef.current?.abort()
      clearTimeout(debounceRef.current)
    }
  }, [])

  const doSearch = useCallback(async (q) => {
    const term = (q || search).trim()
    if (term.length < 2) return
    abortRef.current?.abort()
    const ctrl = new AbortController()
    abortRef.current = ctrl
    setLoading(true)
    try {
      const { data } = await apiClient.get(ENDPOINTS.compare, {
        params: { search: term },
        signal: ctrl.signal,
      })
      setResults(data.results || [])
      if (data.results?.length === 0) toast.info('Aucun produit similaire')
    } catch (err) {
      if (err.name === 'CanceledError' || ctrl.signal.aborted) return
      toast.error('Erreur comparaison')
    } finally {
      if (!ctrl.signal.aborted) setLoading(false)
    }
  }, [search])

  const handleInputChange = useCallback((e) => {
    const val = e.target.value
    setSearch(val)
    clearTimeout(debounceRef.current)
    if (val.trim().length >= 2) {
      debounceRef.current = setTimeout(() => doSearch(val), 400)
    }
  }, [doSearch])

  const chartData = useMemo(() => {
    const all = []
    for (const r of results) {
      const hist = r.price_history || []
      for (const h of hist) {
        all.push({
          date: h.recorded_at ? new Date(h.recorded_at).toLocaleDateString('fr-FR', { month: 'short', day: 'numeric', year: '2-digit' }) : '',
          prix: parseFloat(h.prix_ht) || 0,
          fournisseur: r.fournisseur,
        })
      }
    }
    return all.sort((a, b) => (a.date || '').localeCompare(b.date || ''))
  }, [results])

  const bestPrice = results.length > 0
    ? Math.min(...results.map(r => parseFloat(r.prix_remise_ht) || Infinity))
    : 0
  const maxPrice = results.length > 0
    ? Math.max(...results.map(r => parseFloat(r.prix_remise_ht) || 0))
    : 1

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-end sm:items-center justify-center"
        onClick={onClose}
      >
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          className="bg-slate-900 w-full max-w-lg rounded-t-3xl sm:rounded-3xl max-h-[85vh] flex flex-col border border-slate-800"
          onClick={e => e.stopPropagation()}
        >
          <div className="flex items-center justify-between p-4 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <BarChart3 size={18} className="text-emerald-400" />
              <h2 className="text-lg font-black text-slate-100">Comparateur Prix</h2>
            </div>
            <button onClick={onClose} className="text-slate-500 hover:text-slate-300 transition-colors">
              <X size={20} />
            </button>
          </div>

          <div className="p-4 border-b border-slate-800">
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  value={search}
                  onChange={handleInputChange}
                  onKeyDown={e => e.key === 'Enter' && doSearch()}
                  placeholder="Ex: ciment, tube cuivre..."
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl py-2.5 pl-9 pr-4
                    text-sm text-slate-200 placeholder-slate-600
                    focus:outline-none focus:border-emerald-500/60 transition-all"
                  autoFocus
                />
              </div>
              <button
                onClick={() => doSearch()}
                disabled={loading || search.trim().length < 2}
                className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40
                  text-white rounded-xl font-bold text-sm transition-colors"
              >
                {loading ? <Loader2 size={16} className="animate-spin" /> : 'Comparer'}
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-auto p-4">
            {results.length === 0 && !loading && (
              <p className="text-center text-slate-600 text-sm py-8">
                Recherchez un produit pour comparer les prix
              </p>
            )}

            {loading && (
              <div className="flex justify-center py-8">
                <Loader2 className="w-6 h-6 text-emerald-500 animate-spin" />
              </div>
            )}

            {results.length > 0 && chartData.length > 0 && (
              <div className="mb-4 p-3 bg-slate-800/50 rounded-xl border border-slate-700">
                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                  <TrendingUp size={12} />
                  Evolution des prix
                </p>
                <div className="h-32">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData}>
                      <XAxis dataKey="date" tick={{ fontSize: 9, fill: '#94a3b8' }} />
                      <YAxis tick={{ fontSize: 9, fill: '#94a3b8' }} tickFormatter={v => `${v}€`} />
                      <Tooltip
                        contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
                        labelStyle={{ color: '#94a3b8' }}
                        formatter={(v) => [`${parseFloat(v).toFixed(2)} €`, 'Prix HT']}
                        labelFormatter={(l) => l}
                      />
                      <Area type="monotone" dataKey="prix" stroke="#10b981" fill="#10b98120" strokeWidth={2} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            <div className="space-y-2">
              {results.map((r, i) => {
                const price = parseFloat(r.prix_remise_ht) || 0
                const isBest = price === bestPrice && price > 0
                const barWidth = maxPrice > 0 ? (price / maxPrice) * 100 : 0

                return (
                  <motion.div
                    key={`${(r.fournisseur || '')}-${(r.designation_fr || '').slice(0, 50)}-${r.prix_remise_ht ?? 0}-${i}`}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.03 }}
                    className={`p-3 rounded-xl border ${
                      isBest
                        ? 'border-emerald-500/40 bg-emerald-500/10'
                        : 'border-slate-800 bg-slate-800/50'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-slate-200 truncate">{r.designation_fr}</p>
                        <p className="text-xs text-slate-500 mt-0.5">{r.fournisseur}</p>
                      </div>
                      <div className="text-right shrink-0">
                        <span className={`text-base font-black ${isBest ? 'text-emerald-400' : 'text-slate-300'}`}>
                          {price.toFixed(2)} €
                        </span>
                        <span className="block text-[10px] text-slate-500">/{r.unite}</span>
                        {isBest && (
                          <span className="text-[9px] font-bold text-emerald-400 uppercase">Meilleur prix</span>
                        )}
                      </div>
                    </div>

                    <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${isBest ? 'bg-emerald-500' : 'bg-slate-500'}`}
                        style={{ width: `${barWidth}%` }}
                      />
                    </div>

                    {r.remise_pct > 0 && (
                      <span className="text-[10px] text-amber-500 font-bold mt-1 inline-block">
                        -{r.remise_pct}% remise
                      </span>
                    )}
                  </motion.div>
                )
              })}
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}