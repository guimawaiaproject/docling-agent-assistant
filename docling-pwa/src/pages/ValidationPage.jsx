import { AnimatePresence, motion } from 'framer-motion'
import { AlertCircle, CheckCircle2, Maximize2, Trash2, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import apiClient from '../services/apiClient'
import { ENDPOINTS } from '../config/api'
import { useDoclingStore } from '../store/useStore'
import { FAMILLES } from '../constants/categories'

const TVA_RATE = parseFloat(import.meta.env.VITE_TVA_RATE || '0.21')

export default function ValidationPage() {
  const navigate = useNavigate()

  const products          = useDoclingStore(s => s.extractedProducts)
  const currentInvoiceUrl = useDoclingStore(s => s.currentInvoice)
  const pendingSource     = useDoclingStore(s => s.pendingSource ?? 'pc')
  const updateProduct     = useDoclingStore(s => s.updateProduct)
  const removeProduct     = useDoclingStore(s => s.removeProduct)
  const clearJob          = useDoclingStore(s => s.clearJob)

  const [isSaving, setIsSaving]       = useState(false)
  const [lightboxOpen, setLightboxOpen] = useState(false)

  useEffect(() => {
    const onKeyDown = (e) => {
      if (e.key === 'Escape' && lightboxOpen) setLightboxOpen(false)
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [lightboxOpen])

  if (!products || products.length === 0) {
    return <Navigate to="/scan" replace />
  }

  const handleValidate = async () => {
    setIsSaving(true)
    try {
      await apiClient.post(ENDPOINTS.batch, { produits: products, source: pendingSource })
      clearJob()
      if (navigator.vibrate) navigator.vibrate([100, 50, 100])
      toast.success(`${products.length} produits enregistr\u00e9s dans le catalogue`)
      navigate('/catalogue', { replace: true })
    } catch (err) {
      console.error(err)
      toast.error("Erreur de sauvegarde")
      setIsSaving(false)
    }
  }

  const handleRemove = (index) => {
    removeProduct(index)
    toast.info('Produit retir\u00e9')
  }

  return (
    <div className="p-5 bg-slate-950 min-h-screen">

      {/* Lightbox */}
      <AnimatePresence>
        {lightboxOpen && currentInvoiceUrl && (
          <motion.div
            role="dialog"
            aria-modal="true"
            aria-label="Aperçu facture en grand format"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/90 backdrop-blur flex items-center justify-center p-4"
            onClick={() => setLightboxOpen(false)}
          >
            <motion.img
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.8 }}
              src={currentInvoiceUrl}
              alt="Facture"
              className="max-w-full max-h-[85vh] object-contain rounded-2xl"
            />
            <button
              onClick={() => setLightboxOpen(false)}
              aria-label="Fermer l'aperçu"
              className="absolute top-6 right-6 p-2 bg-slate-800/80 rounded-full text-white hover:bg-slate-700"
            >
              <X size={24} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="pt-4 pb-5 text-center">
        <h1 className="text-2xl font-black text-slate-100">Validation IA</h1>
        <p className="text-sm text-slate-500 mt-1">{products.length} produits extraits</p>
      </div>

      {/* Invoice preview */}
      {currentInvoiceUrl && (
        <div
          className="mb-6 rounded-2xl overflow-hidden border border-slate-800 relative cursor-pointer group"
          onClick={() => setLightboxOpen(true)}
        >
          <img
            src={currentInvoiceUrl}
            alt="Aperçu facture"
            className="w-full max-h-52 object-cover"
          />
          <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors flex items-center justify-center">
            <Maximize2 size={28} className="text-white opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </div>
      )}

      <div className="space-y-3 pb-28">
        <AnimatePresence>
          {products.map((p, i) => {
            const isLow   = p.confidence === 'low'
            const prixTTC = (parseFloat(p.prix_remise_ht) || 0) * (1 + TVA_RATE)

            return (
              <motion.div
                key={p._key ?? p.id ?? `val-${(p.designation_fr || p.fournisseur || '').slice(0, 30)}-${i}`}
                layout
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: -100, height: 0 }}
                transition={{ delay: Math.min(i * 0.04, 0.4) }}
                className={`p-4 rounded-2xl border-2 ${
                  isLow ? 'border-amber-500/40 bg-amber-500/5' : 'border-slate-800 bg-slate-900'
                }`}
              >
                {isLow && (
                  <div className="flex items-center gap-1.5 text-amber-400 text-xs font-bold mb-3">
                    <AlertCircle size={13} />
                    V\u00e9rification recommand\u00e9e
                  </div>
                )}

                {/* Row 1: Designation + delete */}
                <div className="flex items-start gap-2 mb-3">
                  <label htmlFor={`val-designation-${i}`} className="sr-only">Désignation produit</label>
                  <input
                    id={`val-designation-${i}`}
                    value={p.designation_fr || ''}
                    onChange={e => updateProduct(i, 'designation_fr', e.target.value)}
                    placeholder="D\u00e9signation produit"
                    className="flex-1 font-bold text-slate-100 text-base bg-transparent
                      border-none focus:outline-none focus:ring-0 p-0 placeholder-slate-600"
                  />
                  <button
                    onClick={() => handleRemove(i)}
                    aria-label="Supprimer ce produit"
                    className="shrink-0 p-1.5 text-slate-600 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>

                {/* Row 2: Fournisseur + Famille */}
                <div className="grid grid-cols-2 gap-3 mb-3">
                  <div>
                    <label htmlFor={`val-fournisseur-${i}`} className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Fournisseur</label>
                    <input
                      id={`val-fournisseur-${i}`}
                      value={p.fournisseur || ''}
                      onChange={e => updateProduct(i, 'fournisseur', e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2
                        text-sm text-slate-200 font-medium focus:outline-none focus:border-emerald-500"
                    />
                  </div>
                  <div>
                    <label htmlFor={`val-famille-${i}`} className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Famille</label>
                    <select
                      id={`val-famille-${i}`}
                      value={p.famille || ''}
                      onChange={e => updateProduct(i, 'famille', e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2
                        text-sm text-slate-200 font-medium focus:outline-none focus:border-emerald-500"
                    >
                      {FAMILLES.map(f => <option key={f} value={f}>{f}</option>)}
                    </select>
                  </div>
                </div>

                {/* Row 3: Prix brut + Remise + Prix remise + Unite */}
                <div className="grid grid-cols-4 gap-2 mb-3">
                  <div>
                    <label htmlFor={`val-brut-${i}`} className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Brut HT</label>
                    <div className="relative">
                      <input
                        id={`val-brut-${i}`}
                        type="number" step="0.01"
                        value={p.prix_brut_ht || ''}
                        onChange={e => updateProduct(i, 'prix_brut_ht', parseFloat(e.target.value) || 0)}
                        className="w-full bg-slate-800 border border-slate-700 rounded-xl pl-2 pr-5 py-2
                          text-sm text-slate-100 font-bold focus:outline-none focus:border-emerald-500"
                      />
                      <span className="absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-500 text-[10px]">\u20ac</span>
                    </div>
                  </div>
                  <div>
                    <label htmlFor={`val-remise-${i}`} className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Remise</label>
                    <div className="relative">
                      <input
                        id={`val-remise-${i}`}
                        type="number" step="0.5"
                        value={p.remise_pct || ''}
                        onChange={e => updateProduct(i, 'remise_pct', parseFloat(e.target.value) || 0)}
                        className="w-full bg-slate-800 border border-slate-700 rounded-xl pl-2 pr-5 py-2
                          text-sm text-slate-100 font-bold focus:outline-none focus:border-emerald-500"
                      />
                      <span className="absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-500 text-[10px]">%</span>
                    </div>
                  </div>
                  <div>
                    <label htmlFor={`val-net-${i}`} className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Net HT</label>
                    <div className="relative">
                      <input
                        id={`val-net-${i}`}
                        type="number" step="0.01"
                        value={p.prix_remise_ht || ''}
                        onChange={e => updateProduct(i, 'prix_remise_ht', parseFloat(e.target.value) || 0)}
                        className="w-full bg-slate-800 border border-slate-700 rounded-xl pl-2 pr-5 py-2
                          text-sm text-emerald-400 font-bold focus:outline-none focus:border-emerald-500"
                      />
                      <span className="absolute right-1.5 top-1/2 -translate-y-1/2 text-slate-500 text-[10px]">\u20ac</span>
                    </div>
                  </div>
                  <div>
                    <label htmlFor={`val-unite-${i}`} className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Unit\u00e9</label>
                    <input
                      id={`val-unite-${i}`}
                      value={p.unite || ''}
                      onChange={e => updateProduct(i, 'unite', e.target.value)}
                      className="w-full bg-slate-800 border border-slate-700 rounded-xl px-2 py-2
                        text-sm text-slate-200 font-medium focus:outline-none focus:border-emerald-500"
                    />
                  </div>
                </div>

                {/* Footer: TTC */}
                <div className="flex items-center justify-between pt-2 border-t border-slate-800">
                  <span className="text-xs text-slate-600 truncate max-w-[140px]">
                    {p.numero_facture ? `#${p.numero_facture}` : ''} {p.date_facture || ''}
                  </span>
                  <div className="text-right">
                    <span className="text-[10px] text-slate-500 font-bold uppercase">TTC +{(TVA_RATE * 100).toFixed(0)}%</span>
                    <span className="ml-1.5 text-sm font-black text-slate-300">{prixTTC.toFixed(2)} \u20ac</span>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>

      {/* Sticky save button */}
      <div className="fixed bottom-20 left-0 right-0 px-5 max-w-screen-md mx-auto">
        <motion.button
          whileTap={{ scale: 0.97 }}
          onClick={handleValidate}
          disabled={isSaving || products.length === 0}
          data-testid="validation-save-btn"
          className="w-full py-4 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50
            text-white rounded-2xl text-base font-bold flex items-center justify-center gap-2
            shadow-[0_0_30px_rgba(16,185,129,0.3)] transition-all"
        >
          {isSaving
            ? <><div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> Enregistrement...</>
            : <><CheckCircle2 size={22} /> Enregistrer {products.length} produit{products.length > 1 ? 's' : ''}</>
          }
        </motion.button>
      </div>
    </div>
  )
}