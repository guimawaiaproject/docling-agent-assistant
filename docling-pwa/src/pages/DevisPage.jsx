import { AnimatePresence, motion } from 'framer-motion'
import { FileText, Loader2, Minus, Plus, Search, Trash2 } from 'lucide-react'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { toast } from 'sonner'
import apiClient from '../services/apiClient'
import { ENDPOINTS } from '../config/api'
import { generateDevisPDF, getNextDevisNum, getPreviewDevisNum } from '../services/devisGenerator'

const DRAFT_KEY = 'docling_devis_draft'
const DRAFT_MAX_AGE_MS = 24 * 60 * 60 * 1000

const TVA_OPTIONS = [5.5, 10, 20]

function getDefaultTvaRate() {
  try {
    const s = JSON.parse(localStorage.getItem('docling_settings') || '{}')
    const r = typeof s.tvaRate === 'number' ? s.tvaRate : 20
    return TVA_OPTIONS.includes(r) ? r : 20
  } catch {
    return 20
  }
}

export default function DevisPage() {
  const [allProducts, setAllProducts] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState([])
  const [entreprise, setEntreprise] = useState('Mon Entreprise BTP')
  const [client, setClient] = useState('')
  const [remiseGlobale, setRemiseGlobale] = useState(0)
  const [remiseType, setRemiseType] = useState('percent')
  const [devisNum, setDevisNum] = useState(() => getPreviewDevisNum())
  const saveDraftTimerRef = useRef(null)

  // Restore draft on mount if < 24h old
  useEffect(() => {
    try {
      const raw = localStorage.getItem(DRAFT_KEY)
      if (!raw) return
      const { data, savedAt } = JSON.parse(raw)
      if (Date.now() - savedAt > DRAFT_MAX_AGE_MS) {
        localStorage.removeItem(DRAFT_KEY)
        return
      }
      if (data.entreprise != null) setEntreprise(data.entreprise)
      if (data.client != null) setClient(data.client)
      if (data.remiseGlobale != null) setRemiseGlobale(data.remiseGlobale)
      if (data.remiseType != null) setRemiseType(data.remiseType)
      if (data.devisNum != null) setDevisNum(data.devisNum)
      if (Array.isArray(data.selected) && data.selected.length > 0) {
        setSelected(data.selected.map(p => ({
          ...p,
          tvaRate: p.tvaRate ?? getDefaultTvaRate(),
        })))
        toast.success('Brouillon restauré')
      }
    } catch {
      localStorage.removeItem(DRAFT_KEY)
    }
  }, [])

  // Debounced save draft
  useEffect(() => {
    saveDraftTimerRef.current = setTimeout(() => {
      const draft = {
        entreprise,
        client,
        selected,
        remiseGlobale,
        remiseType,
        devisNum,
      }
      localStorage.setItem(DRAFT_KEY, JSON.stringify({
        data: draft,
        savedAt: Date.now(),
      }))
    }, 1500)
    return () => clearTimeout(saveDraftTimerRef.current)
  }, [entreprise, client, selected, remiseGlobale, remiseType, devisNum])

  const fetchProducts = useCallback(async () => {
    setLoading(true)
    try {
      const { data } = await apiClient.get(ENDPOINTS.catalogue, { params: { limit: 500 } })
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
    const defaultTva = getDefaultTvaRate()
    const exists = selected.find(s => s.id === product.id)
    if (exists) {
      setSelected(selected.map(s =>
        s.id === product.id ? { ...s, quantite: s.quantite + 1 } : s
      ))
    } else {
      setSelected([...selected, { ...product, quantite: 1, tvaRate: product.tvaRate ?? defaultTva }])
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

  const updateTvaRate = (id, rate) => {
    setSelected(selected.map(s =>
      s.id === id ? { ...s, tvaRate: parseFloat(rate) } : s
    ))
  }

  const totalHT = selected.reduce((acc, s) =>
    acc + (parseFloat(s.prix_remise_ht) || 0) * s.quantite, 0
  )
  const totalTVA = selected.reduce((acc, p) =>
    acc + (parseFloat(p.prix_remise_ht) || 0) * p.quantite * ((p.tvaRate ?? getDefaultTvaRate()) / 100), 0
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
        remiseGlobale: parseFloat(remiseGlobale) || 0,
        remiseType,
      })
      localStorage.removeItem(DRAFT_KEY)
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
                  <select
                    value={[5.5, 10, 20].includes(Number(s.tvaRate)) ? s.tvaRate : 20}
                    onChange={e => updateTvaRate(s.id, e.target.value)}
                    aria-label={`TVA pour ${s.designation_fr}`}
                    className="w-14 bg-slate-700 border border-slate-600 rounded px-1 py-0.5 text-[10px] text-slate-200"
                  >
                    <option value="5.5">5.5%</option>
                    <option value="10">10%</option>
                    <option value="20">20%</option>
                  </select>
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

          <div className="space-y-1.5 mt-3 pt-3 border-t border-slate-700">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-400 uppercase">Total HT</span>
              <span className="text-sm font-bold text-slate-200">{totalHT.toFixed(2)} EUR</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-400 uppercase">TVA</span>
              <span className="text-sm font-bold text-slate-200">{totalTVA.toFixed(2)} EUR</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-black text-slate-400 uppercase">Total TTC</span>
              <span className="text-lg font-black text-emerald-400">
                {(() => {
                  const remiseAmount = remiseType === 'percent'
                    ? totalHT * (parseFloat(remiseGlobale) || 0) / 100
                    : Math.min(parseFloat(remiseGlobale) || 0, totalHT)
                  const totalHTAfterRemise = totalHT - remiseAmount
                  const tvaScaled = totalHT > 0 ? totalTVA * (totalHTAfterRemise / totalHT) : 0
                  return (totalHTAfterRemise + tvaScaled).toFixed(2)
                })()} EUR
              </span>
            </div>
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