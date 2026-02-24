import axios from 'axios'
import { motion } from 'framer-motion'
import { AlertCircle, CheckCircle2 } from 'lucide-react'
import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { ENDPOINTS } from '../config/api'
import { useDoclingStore } from '../store/useStore'

const FAMILLES = ['Armature','Cloison','Climatisation','Plomberie','Électricité',
  'Menuiserie','Couverture','Carrelage','Isolation','Peinture','Outillage','Consommable','Autre']

export default function ValidationPage() {
  const navigate = useNavigate()

  // Utilisation de Zustand (persistant) plutôt que du Router State
  const products = useDoclingStore(state => state.extractedProducts)
  const currentInvoiceUrl = useDoclingStore(state => state.currentInvoice)
  const updateProduct = useDoclingStore(state => state.updateProduct)
  const clearJob = useDoclingStore(state => state.clearJob)

  const [isSaving, setIsSaving] = useState(false)

  // Si pas de données dans le store, l'utilisateur a tapé l'URL à la main ou rafraîchi sans session
  if (!products || products.length === 0) {
    return <Navigate to="/scan" replace />
  }

  const handleValidate = async () => {
    setIsSaving(true)
    try {
      // POST massif vers la nouvelle API Batch
      await axios.post(ENDPOINTS.batch, { produits: products })

      // Succès: on purge le store et on rentre au catalogue
      clearJob()
      if (navigator.vibrate) navigator.vibrate([100, 50, 100])
      navigate('/catalogue', { replace: true })

    } catch (err) {
      console.error(err)
      alert("Erreur lors de la sauvegarde sur la Base Neon.")
      setIsSaving(false)
    }
  }

  return (
    <div className="p-4 bg-slate-50 min-h-screen">
      <div className="mt-2 mb-6 text-center">
         <h1 className="text-2xl font-black text-slate-800">Validation IA</h1>
         <p className="text-sm font-medium text-slate-500 mt-1">{products.length} produits extraits</p>
      </div>

      {currentInvoiceUrl && (
        <div className="mb-6 rounded-2xl overflow-hidden shadow-sm border border-slate-200">
          <img
            src={currentInvoiceUrl}
            alt="Aperçu facture"
            className="w-full h-48 object-cover opacity-90 hover:opacity-100 transition-opacity"
          />
        </div>
      )}

      <div className="space-y-4">
        {products.map((p, i) => {
          const isLowConfidence = p.confidence === 'low'
          const prixTTC = parseFloat(p.prix_remise_ht) * 1.21

          return (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              key={i}
              className={`p-4 rounded-2xl border-2 transition-colors ${
                isLowConfidence
                  ? 'border-orange-300 bg-orange-50/50'
                  : 'border-white bg-white shadow-sm'
              }`}
            >
              {isLowConfidence && (
                <div className="flex items-center gap-1.5 text-orange-600 bg-orange-100 px-3 py-1 rounded-full text-xs font-bold w-max mb-3">
                  <AlertCircle size={14} />
                  <span>Coup d'œil requis</span>
                </div>
              )}

              <input
                value={p.designation_fr}
                onChange={e => updateProduct(i, 'designation_fr', e.target.value)}
                placeholder="Nom du produit"
                className="w-full font-bold text-slate-800 border-none bg-transparent focus:ring-0 p-0 mb-3 text-lg placeholder-slate-300"
              />

              <div className="grid grid-cols-2 gap-3 mb-2">
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] uppercase font-bold text-slate-400">Famille</label>
                  <select
                    value={p.famille}
                    onChange={e => updateProduct(i, 'famille', e.target.value)}
                    className="border border-slate-200 bg-slate-50 rounded-xl px-3 py-2 text-sm font-medium text-slate-700 outline-none focus:border-blue-500"
                  >
                    {FAMILLES.map(f => <option key={f} value={f}>{f}</option>)}
                  </select>
                </div>

                <div className="flex flex-col gap-1">
                  <label className="text-[10px] uppercase font-bold text-slate-400">Prix remisé (HT)</label>
                  <div className="relative">
                    <input
                      type="number"
                      step="0.01"
                      value={p.prix_remise_ht}
                      onChange={e => updateProduct(i, 'prix_remise_ht', parseFloat(e.target.value))}
                      className="w-full border border-slate-200 bg-slate-50 rounded-xl pl-3 pr-8 py-2 text-sm font-bold text-slate-800 outline-none focus:border-blue-500"
                    />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm font-bold">€</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100/50">
                <div className="flex items-center gap-2 text-xs text-slate-500 font-medium">
                  <span className="bg-slate-200/50 px-2 py-1 rounded-md">{p.unite}</span>
                  <span className="truncate max-w-[120px]">{p.fournisseur}</span>
                </div>
                <div className="text-right">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mr-1">TTC (+21%)</span>
                  <span className="text-sm font-black text-slate-800">{prixTTC.toFixed(2)} €</span>
                </div>
              </div>

            </motion.div>
          )
        })}
      </div>

      <div className="mt-8 mb-6">
        <motion.button
          whileTap={{ scale: 0.95 }}
          onClick={handleValidate}
          disabled={isSaving}
          className="flex items-center justify-center gap-2 w-full py-4 bg-slate-900 text-white rounded-2xl text-lg font-bold shadow-lg disabled:opacity-50"
        >
          {isSaving ? (
            <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <>
              <CheckCircle2 size={24} />
              Enregistrer ({products.length})
            </>
          )}
        </motion.button>
      </div>
    </div>
  )
}
