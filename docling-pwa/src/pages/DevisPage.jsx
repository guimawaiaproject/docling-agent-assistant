import { AnimatePresence, motion } from 'framer-motion'
import { FileText, Loader2, Minus, Plus, Search, Trash2 } from 'lucide-react'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { toast } from 'sonner'
import apiClient from '../services/apiClient'
import { ENDPOINTS } from '../config/api'
import { generateDevisPDF, getNextDevisNum, getPreviewDevisNum } from '../services/devisGenerator'

export default function DevisPage() {
  const [allProducts, setAllProducts] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState([])
  const [entreprise, setEntreprise] = useState('Mon Entreprise BTP')
  const [client, setClient] = useState('')
  const [tvaRate, setTvaRate] = useState(21)
  const [remiseGlobale, setRemiseGlobale] = useState(0)
  const [remiseType, setRemiseType] = useState('percent')
  const [devisNum, setDevisNum] = useState(() => getPreviewDevisNum())

  const fetchProducts = useCallback(async () => {
    setLoading(true)
    try {
      const { data } = await apiClient.get(ENDPOINTS.catalogue)
      setAllProducts(Array.isArray(data) ? data : (data.products || []))
    } catch {
      toast.error('Impossible de charger le catalogue')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchProducts() }, [fetchProducts])

  const filtered = useMemo(() => {
    if (!search.trim()) return allProducts
    const q = search.toLowerCase()
    return allProducts.filter(p =>
      p.designation_fr?.toLowerCase().includes(q) ||
      p.fournisseur?.toLowerCase().includes(q)
    )
  }, [allProducts, search])

  const addProduct = (product) => {
    const exists = selected.find(s => s.id === product.id)
    if (exists) {
      setSelected(selected.map(s =>
        s.id === product.id ? { ...s, quantite: s.quantite + 1 } : s
      ))
    } else {
      setSelected([...selected, { ...product, quantite: 1 }])
    }
  }

  const updateQty = (id, delta) => {
    setSelected(selected.map(s => {
      if (s.id !== id) return s
      const newQty = Math.max(1, s.quantite + delta)
      return { ...s, quantite: newQty }
    }))
  }

  const removeProduct = (id) => {
    setSelected(selected.filter(s => s.id !== id))
  }

  const totalHT = selected.reduce((acc, s) =>
    acc + (parseFloat(s.prix_remise_ht) || 0) * s.quantite, 0
  )

  const handleGenerate = () => {
    if (selected.length === 0) {
      toast.error('Ajoutez au moins un produit')
      return
    }
    try {
      const num = generateDevisPDF(selected, {
        entreprise,
        client,
        devisNum,
        tvaRate,
        remiseGlobale: parseFloat(remiseGlobale) || 0,
        remiseType,
      })
      setDevisNum(getNextDevisNum())
      toast.success(`Devis ${num} généré !`)
    } catch (err) {
      toast.error(`Erreur PDF : ${err.message}`)
    }
  }

  return (
    <div className="p-5 min-h-screen bg-slate-950 pb-28">
      <div className="pt-4 pb-5">
        <h1 className="text-2xl font-black text-slate-100 tracking-tight">Devis</h1>
        <p className="text-xs text-slate-500 mt-0.5">Générez un devis PDF depuis votre catalogue</p>
      </div>

      <div className="grid grid-cols-2 gap-2 mb-4">
        <div>
          <label htmlFor="devis-entreprise" className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Votre entreprise</label>
          <input
            id="devis-entreprise"
            value={entreprise}
            onChange={e => setEntreprise(e.target.value)}
            placeholder="Ex: Mon Entreprise BTP"
            className="w-full bg-slate-900 border border-slate-700 rounded-xl py-2.5 px-3
              text-sm text-slate-200 placeholder-slate-600
              focus:outline-none focus:border-emerald-500/60 transition-all"
          />
        </div>
        <div>
          <label htmlFor="devis-client" className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Nom du client</label>
          <input
            id="devis-client"
            value={client}
            onChange={e => setClient(e.target.value)}
            placeholder="Ex: Client SA"
            className="w-full bg-slate-900 border border-slate-700 rounded-xl py-2.5 px-3
              text-sm text-slate-200 placeholder-slate-600
              focus:outline-none focus:border-emerald-500/60 transition-all"
          />
        </div>
        <div className="col-span-2">
          <label htmlFor="devis-num" className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">N° devis</label>
          <input
            id="devis-num"
            value={devisNum}
            onChange={e => setDevisNum(e.target.value)}
            placeholder="Ex: DEV-2026-001"
            className="w-full bg-slate-900 border border-slate-700 rounded-xl py-2.5 px-3
              text-sm text-slate-200 placeholder-slate-600
              focus:outline-none focus:border-emerald-500/60 transition-all"
          />
        </div>
        <div className="flex justify-between items-center px-3 py-2 bg-slate-900 border border-slate-700 rounded-xl">
          <label htmlFor="devis-tva" className="text-xs text-slate-400">TVA %</label>
          <input
            id="devis-tva"
            type="number"
            min="0"
            max="100"
            step="0.1"
            value={tvaRate}
            onChange={e => setTvaRate(parseFloat(e.target.value) || 0)}
            className="w-16 bg-transparent text-right text-sm font-bold text-slate-200 focus:outline-none"
          />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="devis-remise" className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">Remise globale</label>
          <div className="flex gap-2">
            <input
              id="devis-remise"
              type="number"
              min="0"
              step={remiseType === 'percent' ? 0.1 : 0.01}
              value={remiseGlobale}
              onChange={e => setRemiseGlobale(e.target.value)}
              placeholder={remiseType === 'percent' ? '0' : '0.00'}
              className="flex-1 bg-slate-900 border border-slate-700 rounded-xl py-2 px-3
                text-sm text-slate-200 font-bold focus:outline-none focus:border-emerald-500/60"
            />
            <select
              id="devis-remise-type"
              value={remiseType}
              onChange={e => setRemiseType(e.target.value)}
              aria-label="Type de remise (pourcentage ou montant)"
              className="bg-slate-900 border border-slate-700 rounded-xl py-2 px-2 text-sm text-slate-200"
            >
              <option value="percent">%</option>
              <option value="amount">€</option>
            </select>
          </div>
        </div>
      </div>

      {selected.length > 0 && (
        <div className="mb-5 bg-slate-900 border border-slate-800 rounded-2xl p-4">
          <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-3">
            Produits sélectionnés ({selected.length})
          </p>
          <div className="space-y-2">
            <AnimatePresence>
              {selected.map(s => (
                <motion.div
                  key={s.id}
                  layout
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="flex items-center gap-2 bg-slate-800 rounded-xl p-2.5"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-semibold text-slate-200 truncate">{s.designation_fr}</p>
                    <p className="text-[10px] text-slate-500">{(parseFloat(s.prix_remise_ht)||0).toFixed(2)} EUR/{s.unite}</p>
                  </div>
                  <div className="flex items-center gap-1">
                    <button onClick={() => updateQty(s.id, -1)}
                      aria-label="Diminuer la quantité"
                      className="w-6 h-6 flex items-center justify-center bg-slate-700 rounded text-slate-400 hover:text-white">
                      <Minus size={12} />
                    </button>
                    <span className="text-sm font-bold text-slate-200 w-8 text-center">{s.quantite}</span>
                    <button onClick={() => updateQty(s.id, 1)}
                      aria-label="Augmenter la quantité"
                      className="w-6 h-6 flex items-center justify-center bg-slate-700 rounded text-slate-400 hover:text-white">
                      <Plus size={12} />
                    </button>
                  </div>
                  <span className="text-xs font-bold text-emerald-400 w-16 text-right">
                    {((parseFloat(s.prix_remise_ht)||0) * s.quantite).toFixed(2)}
                  </span>
                  <button onClick={() => removeProduct(s.id)}
                    aria-label="Retirer ce produit du devis"
                    className="text-slate-600 hover:text-red-400 transition-colors">
                    <Trash2 size={14} />
                  </button>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-700">
            <span className="text-xs font-bold text-slate-400 uppercase">Total HT</span>
            <span className="text-lg font-black text-emerald-400">{totalHT.toFixed(2)} EUR</span>
          </div>

          <button
            onClick={handleGenerate}
            className="w-full mt-3 py-3 bg-emerald-600 hover:bg-emerald-500
              text-white rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-colors"
          >
            <FileText size={16} />
            Générer le devis PDF
          </button>
        </div>
      )}

      <div className="relative mb-3">
        <label htmlFor="devis-search" className="sr-only">Chercher un produit dans le catalogue</label>
        <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 pointer-events-none" />
        <input
          id="devis-search"
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="Chercher un produit..."
          className="w-full bg-slate-900 border border-slate-700 rounded-xl py-2.5 pl-9 pr-4
            text-sm text-slate-200 placeholder-slate-600
            focus:outline-none focus:border-emerald-500/60 transition-all"
        />
      </div>

      {loading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="w-6 h-6 text-emerald-500 animate-spin" />
        </div>
      ) : (
        <div className="space-y-1.5 max-h-[40vh] overflow-auto">
          {filtered.slice(0, 50).map(p => (
            <button
              key={p.id}
              onClick={() => addProduct(p)}
              className="w-full flex items-center justify-between p-3 bg-slate-900 border border-slate-800
                rounded-xl hover:border-slate-700 transition-colors text-left"
            >
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-slate-200 truncate">{p.designation_fr}</p>
                <p className="text-[10px] text-slate-500">{p.fournisseur} - {p.famille}</p>
              </div>
              <span className="text-sm font-bold text-emerald-400 shrink-0 ml-2">
                {(parseFloat(p.prix_remise_ht)||0).toFixed(2)} EUR
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}